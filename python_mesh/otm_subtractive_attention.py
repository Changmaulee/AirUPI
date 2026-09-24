"""
TimeMeshin-OTM Subtractive Self-Attention & Dynamic Activation Management (v1.1)
================================================================================
Authored by Chandramouli (@Changmaulee) for Project Brahmand & TimeMeshin.

Features:
1. Subtractive Supermask Relational Routing with PO2 Harmonic Bitshifts.
2. Macro-OTM Bitshift Energy Normalization (1 / sqrt(dim)).
3. Strict Causal Playhead Invariance (t <= t_playhead).
4. Micro-OTM Delta Activation Gating.
"""

import math
import time
from typing import Optional, Tuple, Dict
import torch
import torch.nn as nn
import torch.nn.functional as F


class SubtractiveSupermask(nn.Module):
    """
    Subtractive Supermask using continuous causal popup scores.
    Fixed unweighted polarities in {-2, -1, -0.5, +0.5, +1, +2} (PO2 harmonic palette).
    """
    def __init__(self, out_dim: int, in_dim: int, sparsity: float = 0.5):
        super().__init__()
        self.out_dim = out_dim
        self.in_dim = in_dim
        self.sparsity = sparsity
        
        self.scores = nn.Parameter(torch.randn(out_dim, in_dim) * 0.1)
        palette = torch.tensor([-2.0, -1.0, -0.5, 0.5, 1.0, 2.0])
        chosen_indices = torch.randint(0, len(palette), (out_dim, in_dim))
        self.register_buffer('polarity', palette[chosen_indices])

    def get_mask(self) -> torch.Tensor:
        k = max(1, int(self.scores.numel() * (1.0 - self.sparsity)))
        flat_scores = self.scores.flatten()
        threshold = torch.topk(flat_scores, k)[0][-1]
        return (self.scores >= threshold).float()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        mask = self.get_mask()
        eff_mesh = mask * self.polarity
        # PO2 Bitshift Variance Normalization: 1 / sqrt(in_dim)
        return F.linear(x, eff_mesh) / math.sqrt(self.in_dim)


class TimeMeshinOTMSubtractiveAttention(nn.Module):
    def __init__(
        self,
        embed_dim: int = 512,
        num_heads: int = 8,
        sparsity: float = 0.5,
        delta_threshold: float = 0.02,
        dropout: float = 0.0
    ):
        super().__init__()
        assert embed_dim % num_heads == 0, "embed_dim must be divisible by num_heads"
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        self.sparsity = sparsity
        self.delta_threshold = delta_threshold
        
        self.q_proj = SubtractiveSupermask(embed_dim, embed_dim, sparsity=sparsity)
        self.k_proj = SubtractiveSupermask(embed_dim, embed_dim, sparsity=sparsity)
        self.v_proj = SubtractiveSupermask(embed_dim, embed_dim, sparsity=sparsity)
        self.out_proj = SubtractiveSupermask(embed_dim, embed_dim, sparsity=sparsity)
        
        self.energy_gate = nn.Parameter(torch.zeros(embed_dim))
        self.dropout = nn.Dropout(dropout)

    def forward(
        self,
        x: torch.Tensor,
        causal_playhead: bool = True,
        prev_states: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        batch_size, seq_len, embed_dim = x.shape
        
        if prev_states is not None:
            delta = x - prev_states
            dormant_mask = torch.abs(delta) < self.delta_threshold
            eff_x = torch.where(dormant_mask, torch.zeros_like(x), delta)
            dormant_ratio = dormant_mask.float().mean().item()
        else:
            eff_x = x
            dormant_ratio = 0.0
            
        q = self.q_proj(eff_x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(eff_x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(eff_x).view(batch_size, seq_len, self.num_heads, self.head_dim).transpose(1, 2)
        
        relational_scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.head_dim)
        
        if causal_playhead:
            causal_mask = torch.triu(torch.full((seq_len, seq_len), float('-inf'), device=x.device), diagonal=1)
            relational_scores = relational_scores + causal_mask.unsqueeze(0).unsqueeze(0)
            
        relational_weights = F.softmax(relational_scores, dim=-1)
        prune_threshold = 1.0 / (seq_len * 2.0)
        sparse_weights = torch.where(
            relational_weights >= prune_threshold,
            relational_weights,
            torch.zeros_like(relational_weights)
        )
        norm_sparse_weights = self.dropout(sparse_weights / (sparse_weights.sum(dim=-1, keepdim=True) + 1e-8))
        
        context = torch.matmul(norm_sparse_weights, v).transpose(1, 2).contiguous().view(batch_size, seq_len, embed_dim)
        output = self.out_proj(context) + self.energy_gate.unsqueeze(0).unsqueeze(0)
        
        active_edges = (norm_sparse_weights > 0).float().mean().item()
        metrics = {
            'subtracted_attention_sparsity': 1.0 - active_edges,
            'micro_otm_dormant_ratio': dormant_ratio,
            'active_connections': active_edges,
            'causal_playhead_enforced': float(causal_playhead)
        }
        return output, metrics


class StandardTransformerAttention(nn.Module):
    def __init__(self, embed_dim: int = 512, num_heads: int = 8, dropout: float = 0.0):
        super().__init__()
        self.mha = nn.MultiheadAttention(embed_dim, num_heads, dropout=dropout, batch_first=True)
        
    def forward(self, x: torch.Tensor, causal: bool = True) -> torch.Tensor:
        seq_len = x.size(1)
        attn_mask = nn.Transformer.generate_square_subsequent_mask(seq_len, device=x.device) if causal else None
        out, _ = self.mha(x, x, x, attn_mask=attn_mask, is_causal=causal)
        return out
