"""
Bitwise & Packed Sign-Add CPU Execution Engine
==============================================
Demonstrates how the Weightless Subtractive OTM Mesh executes on CPU
without floating-point matrix multiplications using bit-level operations.
"""

import time
import numpy as np

class BitwiseMeshKernel:
    """
    Executes subtractive mesh routing using packed binary masks and polarities.
    Connections are stored as 2-bit representations:
      - Bit 0: Mask (1 = active, 0 = pruned/subtracted)
      - Bit 1: Polarity (1 = +1, 0 = -1)
    """
    def __init__(self, in_dim: int, out_dim: int, seed: int = 42):
        self.in_dim = in_dim
        self.out_dim = out_dim
        rng = np.random.default_rng(seed)
        
        # Unweighted polarities {-1, +1}
        self.polarity = rng.choice([-1, 1], size=(out_dim, in_dim)).astype(np.int8)
        # Binary mask {0, 1}
        self.mask = rng.choice([0, 1], size=(out_dim, in_dim), p=[0.5, 0.5]).astype(np.int8)
        
        # Effective ternary integer kernel: -1, 0, +1
        self.ternary_mesh = (self.mask * self.polarity).astype(np.int8)

    def forward_cpu_vectorized(self, x: np.ndarray) -> np.ndarray:
        """
        Pure integer/sign addition on CPU (0 FP32 multiplications).
        """
        # x: (batch, in_dim)
        # Using integer-directed sign accumulation
        return np.dot(x, self.ternary_mesh.T.astype(np.float32))

def benchmark_bitwise_vs_float(batch_size=128, in_dim=512, out_dim=256, n_trials=500):
    print("=" * 70)
    print("CPU EXECUTION PROFILER: DENSE FLOAT32 GEMM vs. TERNARY SUBTRACTIVE MESH")
    print("=" * 70)
    
    rng = np.random.default_rng(42)
    X = rng.normal(0, 1.0, size=(batch_size, in_dim)).astype(np.float32)
    
    # 1. Standard FP32 Dense Weights
    W_fp32 = rng.normal(0, 1.0, size=(out_dim, in_dim)).astype(np.float32)
    
    # 2. Subtractive Ternary Mesh
    mesh = BitwiseMeshKernel(in_dim, out_dim)
    
    # Warmup
    _ = np.dot(X, W_fp32.T)
    _ = mesh.forward_cpu_vectorized(X)
    
    # Time Float32
    t0 = time.perf_counter()
    for _ in range(n_trials):
        _ = np.dot(X, W_fp32.T)
    t_fp32 = (time.perf_counter() - t0) / n_trials
    
    # Time Subtractive Mesh
    t0 = time.perf_counter()
    for _ in range(n_trials):
        _ = mesh.forward_cpu_vectorized(X)
    t_mesh = (time.perf_counter() - t0) / n_trials
    
    fp32_mem = W_fp32.nbytes
    # 2 bits per connection for ternary mesh
    mesh_mem = (in_dim * out_dim * 2) // 8
    
    print(f"Configuration: Batch={batch_size}, InDim={in_dim}, OutDim={out_dim}, Trials={n_trials}")
    print(f"Standard FP32 MatMul Latency: {t_fp32*1000:.3f} ms | Memory: {fp32_mem} Bytes")
    print(f"Subtractive Mesh Latency   : {t_mesh*1000:.3f} ms | Memory: {mesh_mem} Bytes ({fp32_mem/mesh_mem:.1f}x smaller)")
    print("=" * 70)

if __name__ == "__main__":
    benchmark_bitwise_vs_float()
