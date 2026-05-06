import numpy as np
import logging
import os

# Ensure logging is configured
logging.basicConfig(filename="pipeline.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_numpy_tasks():
    logging.info("=== Starting NumPy Tasks ===")
    
    # 1. Create NumPy arrays using 4+ methods
    # Method 1: From list
    arr1 = np.array([1, 2, 3, 4, 5])
    # Method 2: Zeros
    arr2 = np.zeros((3, 3))
    # Method 3: Ones
    arr3 = np.ones((2, 5), dtype=np.float32)
    # Method 4: Arange
    arr4 = np.arange(0, 10, 2)
    # Method 5: Random
    arr5 = np.random.rand(4, 2)
    
    arrays = [arr1, arr2, arr3, arr4, arr5]
    method_names = ["np.array", "np.zeros", "np.ones", "np.arange", "np.random.rand"]
    
    for name, arr in zip(method_names, arrays):
        print(f"\nArray created using {name}:")
        print(arr)
        print(f"Shape: {arr.shape}, Dtype: {arr.dtype}, Ndim: {arr.ndim}")
        logging.info(f"Created array using {name} with shape {arr.shape}")

    # 2. Vectorized arithmetic — no Python loops for math
    logging.info("Performing vectorized arithmetic")
    v1 = np.array([10, 20, 30, 40])
    v2 = np.array([1, 2, 3, 4])
    
    add_res = v1 + v2
    mul_res = v1 * v2
    exp_res = np.exp(v2)
    mean_res = np.mean(v1)
    
    print("\nVectorized Arithmetic Results:")
    print(f"Addition: {add_res}")
    print(f"Multiplication: {mul_res}")
    print(f"Exponential: {exp_res}")
    print(f"Mean of v1: {mean_res}")
    
    logging.info(f"Vectorized Addition Result: {add_res}")
    logging.info("=== NumPy Tasks Completed ===")

if __name__ == "__main__":
    run_numpy_tasks()
