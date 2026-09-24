"""
TimeMeshin-OTM Subtractive Feed-Forward Network (FFN/MLP) (v1.1)
===============================================================
Authored by Chandramouli (@Changmaulee) for Project Brahmand & TimeMeshin.
"""

import math
import time
from typing import Optional, Tuple, Dict
import torch
import torch.nn as nn
import torch.nn.functional as F
from otm_subtractive_attention import SubtractiveSupermask


class SwiPO2Activation(nn.Module):
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return F.relu(x) - 0.5 * F.relu(-x)


class TimeMeshinOTMSubtractiveFFN(nn.Module):
    def __init__(
        self,
        embed_dim: int = 512,
        hidden_dim: Optional[int] = None,
        sparsity: float = 0.5,
        delta_threshold: float = 0.02,
        dropout: float = 0.0
    ):
        super().__init__()
        self.embed_dim = embed_dim
        self.hidden_dim = hidden_dim if hidden_dim is not None else int(embed_dim * 4)
        self.sparsity = sparsity
        self.delta_threshold = delta_threshold
        
        self.gate_proj = SubtractiveSupermask(self.hidden_dim, embed_dim, sparsity=sparsity)
        self.up_proj = SubtractiveSupermask(self.hidden_dim, embed_dim, sparsity=sparsity)
        self.down_proj = SubtractiveSupermask(embed_dim, self.hidden_dim, sparsity=sparsity)
        
        self.act_fn = SwiPO2Activation()
        self.energy_gate = nn.Parameter(torch.zeros(embed_dim))
        self.dropout = nn.Dropout(dropout)

    def forward(
        self,
        x: torch.Tensor,
        prev_states: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        if prev_states is not None:
            delta = x - prev_states
            dormant_mask = torch.abs(delta) < self.delta_threshold
            eff_x = torch.where(dormant_mask, torch.zeros_like(x), delta)
            dormant_ratio = dormant_mask.float().mean().item()
        else:
            eff_x = x
            dormant_ratio = 0.0
            
        gate = self.act_fn(self.gate_proj(eff_x))
        up = self.up_proj(eff_x)
        intermediate = self.dropout(gate * up)
        output = self.down_proj(intermediate) + self.energy_gate.unsqueeze(0).unsqueeze(0)
        
        metrics = {
            "micro_otm_ffn_dormant_ratio": dormant_ratio,
            "ffn_sparsity": self.sparsity,
            "intermediate_dim": self.hidden_dim
        }
        return output, metrics


class StandardSwiGLUFFN(nn.Module):
    def __init__(self, embed_dim: int = 512, hidden_dim: Optional[int] = None, dropout: float = 0.0):
        super().__init__()
        self.embed_dim = embed_dim
        self.hidden_dim = hidden_dim if hidden_dim is not None else int(embed_dim * 4)
        self.gate_proj = nn.Linear(embed_dim, self.hidden_dim, bias=False)
        self.up_proj = nn.Linear(embed_dim, self.hidden_dim, bias=False)
        self.down_proj = nn.Linear(self.hidden_dim, embed_dim, bias=False)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        gate = F.silu(self.gate_proj(x))
        up = self.up_proj(x)
        return self.down_proj(self.dropout(gate * up))
