"""Compute stress tests - Compatible with old GPUs"""

import torch
import time
from typing import Dict


class ComputeStressTest:
    """GPU compute stress tests"""
    
    def __init__(self, device: torch.device):
        self.device = device
        self.is_old_gpu = self._detect_old_gpu()
        
    def _detect_old_gpu(self) -> bool:
        """Detect if we're running on an old GPU"""
        if self.device.type == "cpu":
            return False
            
        try:
            capability = torch.cuda.get_device_capability(self.device.index or 0)
            # Compute capability < 5.0 is considered old (pre-Maxwell)
            if capability[0] < 5:
                return True
                
            # Also check available memory (old GPUs typically have less)
            props = torch.cuda.get_device_properties(self.device.index or 0)
            if props.total_memory < 4 * 1024 * 1024 * 1024:  # Less than 4GB
                return True
                
        except:
            pass
            
        return False
        
    def matrix_multiply_stress(self, size: int = 4096, duration: float = 10) -> Dict[str, float]:
        """Traditional matrix multiplication stress test"""
        # Adjust size for old GPUs or limited memory
        if self.is_old_gpu:
            size = min(size, 2048)  # Smaller matrices for old GPUs
            print(f"Detected old GPU - using matrix size {size}")
            
        if self.device.type == "cpu":
            size = min(size, 512)
        elif self.device.type == "cuda":
            # Check available memory and adjust
            try:
                mem_free = torch.cuda.mem_get_info(self.device.index)[0]
                mem_needed = size * size * 4 * 3  # 3 matrices, 4 bytes per float
                
                if mem_needed > mem_free * 0.8:  # Use only 80% of free memory
                    size = int((mem_free * 0.8 / (4 * 3)) ** 0.5)
                    size = min(size, 4096)  # Cap at original size
                    print(f"Adjusted matrix size to {size} based on available memory")
            except:
                if self.is_old_gpu:
                    size = 2048
        
        # Create matrices
        try:
            a = torch.randn((size, size), device=self.device, dtype=torch.float32)
            b = torch.randn((size, size), device=self.device, dtype=torch.float32)
        except torch.cuda.OutOfMemoryError:
            # If we still run out of memory, try smaller size
            size = size // 2
            print(f"OutOfMemory - reducing to {size}")
            a = torch.randn((size, size), device=self.device, dtype=torch.float32)
            b = torch.randn((size, size), device=self.device, dtype=torch.float32)
        
        start_time = time.time()
        iterations = 0
        flops = 0
        
        while time.time() - start_time < duration:
            try:
                c = torch.matmul(a, b)
                if self.device.type == "cuda":
                    torch.cuda.synchronize()
                iterations += 1
                flops += 2 * size**3  # Approximate FLOPs for matrix multiply
            except torch.cuda.OutOfMemoryError:
                print("Warning: GPU memory pressure during test")
                torch.cuda.empty_cache()
                continue
        
        elapsed = time.time() - start_time
        return {
            "iterations": iterations,
            "tflops": (flops / elapsed) / 1e12,
            "avg_time_per_iter": elapsed / iterations if iterations > 0 else 0,
            "matrix_size": size,
            "is_old_gpu": self.is_old_gpu
        }
