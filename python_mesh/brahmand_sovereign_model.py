"""
Project Brahmand: End-to-End Sovereign Multiplier-Free LLM Architecture (v1.1)
=============================================================================
Authored by Chandramouli (@Changmaulee) for Sovereign AI Research & TimeMeshin.
"""

import math
import time
from typing import Optional, Tuple, Dict, List
import torch
import torch.nn as nn
import torch.nn.functional as F

from otm_subtractive_attention import TimeMeshinOTMSubtractiveAttention, StandardTransformerAttention
from otm_subtractive_ffn import TimeMeshinOTMSubtractiveFFN, StandardSwiGLUFFN
from otm_predictive_bframe_head import PredictiveBFrameOutputHead


class MacroOTMEnergyNorm(nn.Module):
    """
    Macro-OTM Discrete Energy Bounding Normalization.
    Replaces expensive continuous RMSNorm / LayerNorm square-roots and divisions.
    """
    def __init__(self, embed_dim: int):
        super().__init__()
        self.gate = nn.Parameter(torch.zeros(embed_dim))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        mean_abs = torch.mean(torch.abs(x), dim=-1, keepdim=True) + 1e-5
        return (x / mean_abs) + self.gate.unsqueeze(0).unsqueeze(0)


class TimeMeshinOTMTransformerBlock(nn.Module):
    def __init__(
        self,
        embed_dim: int = 512,
        num_heads: int = 8,
        hidden_dim: Optional[int] = None,
        sparsity: float = 0.5,
        delta_threshold: float = 0.02,
        dropout: float = 0.0
    ):
        super().__init__()
        self.embed_dim = embed_dim
        self.norm1 = MacroOTMEnergyNorm(embed_dim)
        self.attn = TimeMeshinOTMSubtractiveAttention(
            embed_dim=embed_dim,
            num_heads=num_heads,
            sparsity=sparsity,
            delta_threshold=delta_threshold,
            dropout=dropout
        )
        self.norm2 = MacroOTMEnergyNorm(embed_dim)
        self.ffn = TimeMeshinOTMSubtractiveFFN(
            embed_dim=embed_dim,
            hidden_dim=hidden_dim,
            sparsity=sparsity,
            delta_threshold=delta_threshold,
            dropout=dropout
        )

    def forward(
        self,
        x: torch.Tensor,
        causal_playhead: bool = True,
        prev_states: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        # Residual 1 + Attn
        norm_x1 = self.norm1(x)
        attn_out, attn_metrics = self.attn(norm_x1, causal_playhead=causal_playhead, prev_states=prev_states)
        x = x + attn_out
        
        # Residual 2 + FFN
        norm_x2 = self.norm2(x)
        ffn_out, ffn_metrics = self.ffn(norm_x2, prev_states=prev_states)
        x = x + ffn_out
        
        return x, {**attn_metrics, **ffn_metrics}


class ProjectBrahmandModel(nn.Module):
    def __init__(
        self,
        vocab_size: int = 32000,
        embed_dim: int = 512,
        num_layers: int = 4,
        num_heads: int = 8,
        hidden_dim: Optional[int] = None,
        manifold_dim: int = 24,
        sparsity: float = 0.5,
        delta_threshold: float = 0.02,
        dropout: float = 0.0
    ):
        super().__init__()
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.num_layers = num_layers
        self.manifold_dim = manifold_dim
        
        self.embed_24d = nn.Parameter(torch.randn(vocab_size, manifold_dim) * 0.1, requires_grad=False)
        self.embed_proj = nn.Parameter(torch.randn(manifold_dim, embed_dim) * 0.1, requires_grad=False)
        
        self.blocks = nn.ModuleList([
            TimeMeshinOTMTransformerBlock(
                embed_dim=embed_dim,
                num_heads=num_heads,
                hidden_dim=hidden_dim,
                sparsity=sparsity,
                delta_threshold=delta_threshold,
                dropout=dropout
            )
            for _ in range(num_layers)
        ])
        
        self.final_norm = MacroOTMEnergyNorm(embed_dim)
        self.head = PredictiveBFrameOutputHead(
            embed_dim=embed_dim,
            vocab_size=vocab_size,
            manifold_dim=manifold_dim,
            sparsity=sparsity,
            delta_threshold=delta_threshold
        )

    def forward(
        self,
        input_ids: torch.Tensor,
        causal_playhead: bool = True,
        boundary_targets: Optional[torch.Tensor] = None,
        prev_hidden: Optional[List[torch.Tensor]] = None
    ) -> Tuple[torch.Tensor, torch.Tensor, Dict[str, float]]:
        coords = self.embed_24d[input_ids]
        x = torch.matmul(coords, self.embed_proj)
        
        layer_metrics = {}
        for idx, block in enumerate(self.blocks):
            prev_h = prev_hidden[idx] if prev_hidden is not None else None
            x, metrics = block(x, causal_playhead=causal_playhead, prev_states=prev_h)
            for k, v in metrics.items():
                layer_metrics[f"l{idx}_{k}"] = v
                
        x = self.final_norm(x)
        logits, manifold_out, head_metrics = self.head(x, boundary_targets=boundary_targets)
        return logits, manifold_out, {**layer_metrics, **head_metrics}

    def generate(self, prompt_ids: torch.Tensor, max_new_tokens: int = 16) -> torch.Tensor:
        self.eval()
        with torch.no_grad():
            curr_ids = prompt_ids.clone()
            for _ in range(max_new_tokens):
                logits, _, _ = self.forward(curr_ids, causal_playhead=True)
                next_token = torch.argmax(logits[:, -1, :], dim=-1, keepdim=True)
                curr_ids = torch.cat([curr_ids, next_token], dim=1)
        return curr_ids


class StandardBaselineTransformer(nn.Module):
    def __init__(self, vocab_size=32000, embed_dim=512, num_layers=4, num_heads=8, hidden_dim=2048):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.layers = nn.ModuleList([
            nn.ModuleDict({
                "attn": StandardTransformerAttention(embed_dim, num_heads),
                "norm1": nn.LayerNorm(embed_dim),
                "ffn": StandardSwiGLUFFN(embed_dim, hidden_dim),
                "norm2": nn.LayerNorm(embed_dim)
            })
            for _ in range(num_layers)
        ])
        self.lm_head = nn.Linear(embed_dim, vocab_size, bias=False)

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        x = self.embedding(input_ids)
        for layer in self.layers:
            x = x + layer["attn"](layer["norm1"](x))
            x = x + layer["ffn"](layer["norm2"](x))
        return self.lm_head(x)
