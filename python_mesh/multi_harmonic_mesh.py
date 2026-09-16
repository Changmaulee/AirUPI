"""
Multi-Harmonic Subtractive OTM Mesh Engine
==========================================
Supports both Classification and Non-Linear Continuous Regression.
Uses discrete power-of-two harmonic polarities (±0.5, ±1.0, ±2.0)
which map to hardware BITSHIFTS and SIGN-ADDS (Zero FP32 Multiplications).
"""

import numpy as np
from typing import List, Tuple, Dict, Union

class MultiHarmonicLayer:
    """
    Multi-Harmonic Subtractive Layer:
    Connections possess discrete harmonic polarities P ∈ {-2.0, -1.0, -0.5, 0.5, 1.0, 2.0}.
    In hardware, multiplying by P is just a bitshift >> 1 (or << 1) + sign negation!
    """
    def __init__(self, in_dim: int, out_dim: int, delta_threshold: float = 0.015, seed: int = 42):
        self.in_dim = in_dim
        self.out_dim = out_dim
        self.delta_threshold = delta_threshold
        
        rng = np.random.default_rng(seed)
        # Discrete power-of-two harmonic palette:
        harmonic_palette = np.array([-2.0, -1.0, -0.5, 0.5, 1.0, 2.0], dtype=np.float32)
        self.polarity = rng.choice(harmonic_palette, size=(out_dim, in_dim))
        
        # Continuous Causal Pop Scores (used to dynamically carve the top-k% mask)
        self.scores = rng.normal(0, 1.0, size=(out_dim, in_dim)).astype(np.float32)
        self.threshold = np.zeros((out_dim, 1), dtype=np.float32)
        
        self.prev_input_state = np.zeros(in_dim, dtype=np.float32)
        self.total_evals = 0
        self.active_evals = 0

    def get_mask(self, sparsity: float = 0.40) -> np.ndarray:
        k = max(1, int(self.scores.size * (1.0 - sparsity)))
        thresh = np.partition(self.scores.flatten(), -k)[-k]
        return (self.scores >= thresh).astype(np.float32)

    def forward(self, x: np.ndarray, is_streaming: bool = False, sparsity: float = 0.40) -> Tuple[np.ndarray, np.ndarray]:
        if x.ndim == 1:
            x = x.reshape(1, -1)
        n_steps, dim = x.shape
        
        if is_streaming:
            deltas = np.zeros_like(x)
            prev = self.prev_input_state.copy()
            for t in range(n_steps):
                deltas[t] = x[t] - prev
                prev = x[t].copy()
            self.prev_input_state = prev
            
            active_mask = (np.abs(deltas) >= self.delta_threshold).astype(np.float32)
            eff_x = deltas * active_mask
            self.total_evals += n_steps * dim
            self.active_evals += int(np.sum(active_mask))
        else:
            eff_x = x
            self.total_evals += n_steps * dim
            self.active_evals += n_steps * dim
            
        mask = self.get_mask(sparsity=sparsity)
        # Effective unweighted harmonic routing (Bitshifts + Sign-adds only)
        eff_mesh = mask * self.polarity # Shape: (out_dim, in_dim)
        
        raw_z = np.dot(eff_mesh, eff_x.T) + self.threshold # (out_dim, n_steps)
        return raw_z, mask


class MultiHarmonicMeshNet:
    def __init__(self, layer_dims: List[int], is_regression: bool = False, delta_threshold: float = 0.015, seed: int = 42):
        self.layer_dims = layer_dims
        self.is_regression = is_regression
        self.layers: List[MultiHarmonicLayer] = []
        
        for i in range(len(layer_dims) - 1):
            self.layers.append(
                MultiHarmonicLayer(
                    in_dim=layer_dims[i],
                    out_dim=layer_dims[i+1],
                    delta_threshold=delta_threshold,
                    seed=seed + i * 23
                )
            )

    def forward(self, x: np.ndarray, is_streaming: bool = False, sparsity: float = 0.40):
        curr = x.T # (in_dim, batch)
        activations = [curr]
        masks = []
        
        for idx, layer in enumerate(self.layers):
            z, mask = layer.forward(curr.T, is_streaming=is_streaming, sparsity=sparsity)
            masks.append(mask)
            
            if idx < len(self.layers) - 1:
                # Macro I-Frame Energy Normalization + Non-linear Activation (Leaky ReLU)
                std = np.std(z, axis=0, keepdims=True) + 1e-5
                mean = np.mean(z, axis=0, keepdims=True)
                z_norm = (z - mean) / std
                curr = np.where(z_norm > 0, z_norm, 0.05 * z_norm) # LeakyReLU
            else:
                if self.is_regression:
                    # Continuous linear projection for regression
                    curr = z
                else:
                    # Softmax for classification
                    exp_z = np.exp(z - np.max(z, axis=0, keepdims=True))
                    curr = exp_z / np.sum(exp_z, axis=0, keepdims=True)
            activations.append(curr)
            
        return curr.T, activations, masks

    def train_subtractive(self, X: np.ndarray, Y: np.ndarray, epochs: int = 80, lr: float = 0.12, sparsity: float = 0.40, batch_size: int = 32):
        num_samples = X.shape[0]
        for epoch in range(epochs):
            perm = np.random.permutation(num_samples)
            X_shuf = X[perm]
            Y_shuf = Y[perm]
            
            for b in range(0, num_samples, batch_size):
                xb = X_shuf[b:b+batch_size]
                yb = Y_shuf[b:b+batch_size]
                
                preds, activations, masks = self.forward(xb, is_streaming=False, sparsity=sparsity)
                
                # Output delta
                if self.is_regression:
                    # MSE loss derivative
                    dz = 2.0 * (activations[-1] - yb.T) / len(xb)
                else:
                    # Cross-Entropy derivative
                    dz = (activations[-1] - yb.T) / len(xb)
                    
                curr_delta = dz
                for idx in reversed(range(len(self.layers))):
                    layer = self.layers[idx]
                    a_prev = activations[idx]
                    
                    # Subtractive causal score alignment
                    d_scores = np.dot(curr_delta, a_prev.T) * layer.polarity
                    d_th = np.sum(curr_delta, axis=1, keepdims=True)
                    
                    if idx > 0:
                        eff_mesh = masks[idx] * layer.polarity
                        da_prev = np.dot(eff_mesh.T, curr_delta)
                        # Leaky ReLU derivative
                        curr_delta = np.where(a_prev > 0, da_prev, 0.05 * da_prev)
                        
                    # Update causal scores (governs subtractive pruning) and thresholds
                    layer.scores -= lr * d_scores
                    layer.threshold -= lr * d_th
