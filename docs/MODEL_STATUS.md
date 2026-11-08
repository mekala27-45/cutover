# Model and source status

The TF-IDF floor is implemented and passes synthetic fit, calibration and serialization tests. Full intake and actual baseline evaluation completed. The aggregate results and source provenance are published in public_results/floor.json and report/baseline.md. They are not evidence of a live model deployment.

ModernBERT-base executed successfully on one visible Tesla T4 using Transformers 5.22.1, PyTorch 2.11.0+cu130, fp16 and SDPA. The exact revision is 8949b909ec900327062f0ebf497f51aef5e6f0c8, with Apache-2.0 metadata verified before loading. Ten authored-input forward passes produced finite outputs. The classification head was newly initialized, so this proves runtime compatibility only. See public_results/encoder-probe.json. Fine-tuning, calibration, ONNX export, INT8 parity and held-out task evaluation remain outstanding.

The bounded Qwen3-1.7B and Qwen3-8B-AWQ probes were launched with isolated vLLM dependencies and authored inputs. Their final output was not retrieved because the local browser connection failed. They are not counted as passed. No language-model arm has completed the registered task evaluation, and no model is promoted to the API.

NHTSA complaint data is public source material. Filed labels are not engineering safety findings. Public artifacts contain aggregates, not complaint narratives or case identifiers. Source archive digests and post-deduplication counts are recorded separately from complete training evidence.

Code is Apache-2.0. Each additional model license must be checked against its exact revision before loading or promotion. The project does not relicense third-party weights or data.
