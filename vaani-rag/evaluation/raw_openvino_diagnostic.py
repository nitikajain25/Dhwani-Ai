import time
import sys
from pathlib import Path
import numpy as np
import openvino as ov
import functools

print = functools.partial(print, flush=True)

PROJECT_ROOT = Path("c:/Users/HP/OneDrive/Desktop/Vaani/vaani-rag")
MODEL_XML = PROJECT_ROOT / "models" / "bge-reranker-v2-m3-openvino" / "openvino_model.xml"

def main():
    print("=" * 60)
    print("RAW OPENVINO GPU TEST")
    print("=" * 60)
    
    # 1. Core Info
    core = ov.Core()
    print(f"OpenVINO Version: {ov.get_version()}")
    devices = core.available_devices
    print(f"Available Devices: {devices}")
    
    # 2. Read Model
    print(f"\nReading model from {MODEL_XML}")
    model = core.read_model(str(MODEL_XML))
    
    print("\n[Model Inputs]")
    for i, inp in enumerate(model.inputs):
        print(f"  Input {i}: name='{inp.any_name}', shape={inp.partial_shape}, type={inp.element_type}")
        
    print("\n[Model Outputs]")
    for i, out in enumerate(model.outputs):
        print(f"  Output {i}: name='{out.any_name}', shape={out.partial_shape}, type={out.element_type}")
    
    # Dummy data shape: batch=20, seq_len=179 (as seen in previous trace)
    batch_size = 20
    seq_len = 179
    print(f"\nCreating dummy input: batch={batch_size}, seq_len={seq_len}")
    
    inputs_dict = {}
    for inp in model.inputs:
        name = inp.any_name
        # Typically input_ids, attention_mask
        inputs_dict[name] = np.ones((batch_size, seq_len), dtype=np.int64)

    def benchmark_device(device_name):
        print(f"\n=== Testing Device: {device_name} ===")
        try:
            t0 = time.time()
            compiled = core.compile_model(model, device_name)
            compile_time = time.time() - t0
            print(f"  [SUCCESS] Compiled on {device_name} in {compile_time:.2f}s")
            
            # Check actual execution devices if possible
            try:
                exec_devices = compiled.get_property("EXECUTION_DEVICES")
                print(f"  Actual execution device property: {exec_devices}")
            except Exception as e:
                print(f"  Could not read EXECUTION_DEVICES: {e}")

            # First Inference
            t0 = time.time()
            req = compiled.create_infer_request()
            res = req.infer(inputs_dict)
            first_time = time.time() - t0
            print(f"  First inference (ms): {first_time * 1000:.2f}")
            
            # Warm Inferences
            warm_times = []
            for _ in range(3):
                t0 = time.time()
                res = req.infer(inputs_dict)
                warm_times.append(time.time() - t0)
            
            avg_warm = sum(warm_times) / len(warm_times)
            print(f"  Warm inference avg (ms): {avg_warm * 1000:.2f}")
            
        except Exception as e:
            print(f"  [FAILURE] Compilation/Inference failed on {device_name}:")
            print(f"    Error: {e}")

    # Benchmark CPU first as baseline
    if "CPU" in devices:
        benchmark_device("CPU")
        
    # Benchmark GPU
    if "GPU" in devices:
        benchmark_device("GPU")

if __name__ == "__main__":
    main()
