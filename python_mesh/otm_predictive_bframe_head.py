"""
TimeMeshin-OTM Predictive B-Frame Output Head (v1.1)
===================================================
Authored by Chandramouli (@Changmaulee) for Project Brahmand & TimeMeshin.
"""

import math
import time
from typing import Optional, Tuple, Dict
import torch
import torch.nn as nn
import torch.nn.functional as F
from otm_subtractive_attention import SubtractiveSupermask


class PredictiveBFrameOutputHead(nn.Module):
    def __init__(
        self,
        embed_dim: int = 512,
        vocab_size: int = 32000,
        manifold_dim: int = 24,
        sparsity: float = 0.5,
        delta_threshold: float = 0.02
    ):
        super().__init__()
        self.embed_dim = embed_dim
        self.vocab_size = vocab_size
        self.manifold_dim = manifold_dim
        self.sparsity = sparsity
        self.delta_threshold = delta_threshold
        
        self.manifold_proj = SubtractiveSupermask(manifold_dim, embed_dim, sparsity=sparsity)
        self.vocab_head = SubtractiveSupermask(vocab_size, manifold_dim, sparsity=sparsity)
        self.logit_gate = nn.Parameter(torch.zeros(vocab_size))

    def forward(
        self,
        hidden_states: torch.Tensor,
        boundary_targets: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, torch.Tensor, Dict[str, float]]:
        batch_size, seq_len, embed_dim = hidden_states.shape
        manifold_coords = self.manifold_proj(hidden_states)
        
        if boundary_targets is not None:
            alpha = torch.linspace(0.0, 1.0, seq_len, device=hidden_states.device).view(1, seq_len, 1)
            b_frame_trajectory = (1.0 - alpha) * manifold_coords[:, 0:1, :] + alpha * boundary_targets.unsqueeze(1)
            eff_coords = 0.5 * (manifold_coords + b_frame_trajectory)
        else:
            eff_coords = manifold_coords
            
        logits = self.vocab_head(eff_coords) + self.logit_gate.unsqueeze(0).unsqueeze(0)
        metrics = {
            "manifold_dim": self.manifold_dim,
            "vocab_size": self.vocab_size,
            "b_frame_boundary_active": float(boundary_targets is not None)
        }
        return logits, eff_coords, metrics
