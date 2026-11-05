"""Authored-input runtime probe. This is not model evaluation."""
import gc
import importlib.metadata
import json
import os
import time
import urllib.request
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = "0"
os.environ["HF_HOME"] = "/kaggle/temp/cutover-hf"
os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN"] = "1"

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

MODEL = "answerdotai/ModernBERT-base"
result = {"mode": "actual_encoder_runtime_probe", "model": MODEL,
          "input_kind": "authored_probe", "task_accuracy": None}
output = Path("/kaggle/working/encoder-probe.json")
try:
    with urllib.request.urlopen("https://huggingface.co/api/models/" + MODEL, timeout=30) as r:
        metadata = json.load(r)
    revision = metadata["sha"]
    license_name = metadata.get("cardData", {}).get("license")
    if license_name != "apache-2.0":
        raise ValueError("model_license_requires_review")
    result.update(revision=revision, license=license_name,
                  transformers=importlib.metadata.version("transformers"),
                  torch=torch.__version__, attention="sdpa", dtype="float16")
    torch.manual_seed(23)
    tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=revision, token=False)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL, revision=revision, token=False, num_labels=3,
        problem_type="multi_label_classification", dtype=torch.float16,
        attn_implementation="sdpa",
    ).to("cuda:0").eval()
    elapsed = []
    for index in range(10):
        started = time.perf_counter()
        inputs = tokenizer(
            "Authored test: smoke appeared near the engine while parking.",
            return_tensors="pt", padding="max_length", max_length=512, truncation=True,
        ).to("cuda:0")
        with torch.inference_mode():
            logits = model(**inputs).logits
        torch.cuda.synchronize()
        if logits.shape != (1, 3) or not torch.isfinite(logits).all():
            raise ValueError("invalid_probe_logits")
        elapsed.append((time.perf_counter() - started) * 1000)
    result.update(status="passed", request_count=len(elapsed), request_ms=elapsed,
                  peak_gpu_bytes=torch.cuda.max_memory_allocated())
    del model
    gc.collect()
    torch.cuda.empty_cache()
except Exception as exc:
    result.update(status="failed", error_type=type(exc).__name__, error=str(exc)[:500])
finally:
    output.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
if result["status"] != "passed":
    raise SystemExit(1)
