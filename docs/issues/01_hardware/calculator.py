"""Lower-bound arithmetic for an explicitly specified Atlas workload.

Does not include quantization metadata, runtime buffers, index structures,
activations, optimizer state or operating-system memory. It is not a fit test.
"""

import json
import sys
from pathlib import Path


def nonnegative_number(data, key):
    value = data[key]
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise ValueError(f"{key} must be a nonnegative number")
    return value


def main(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    p = nonnegative_number(data, "parameters")
    bits = nonnegative_number(data, "weight_bits")
    l = nonnegative_number(data, "layers")
    h = nonnegative_number(data, "kv_heads")
    d = nonnegative_number(data, "head_dim")
    s = nonnegative_number(data, "context_tokens")
    b = nonnegative_number(data, "active_sequences")
    kv_size = nonnegative_number(data, "kv_bytes_per_element")
    n = nonnegative_number(data, "vector_count")
    dim = nonnegative_number(data, "vector_dimensions")
    vec_size = nonnegative_number(data, "vector_bytes_per_element")

    estimates = {
        "raw_weights": p * bits / 8,
        "full_kv_cache": 2 * l * h * d * s * b * kv_size,
        "raw_vectors": n * dim * vec_size,
    }
    print(data.get("label", "Workload"))
    for name, value in estimates.items():
        print(f"{name}: {value:,.0f} bytes; {value / 1e9:.3f} GB; "
              f"{value / 2**30:.3f} GiB")
    print("Lower bounds only; confirm the architecture and measure the runtime.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 calculator.py workload.json")
    main(sys.argv[1])
