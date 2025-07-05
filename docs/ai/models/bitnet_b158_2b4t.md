---
author: Knowledge Base Automation System
created_at: '2025-07-04'
description: Documentation on Bitnet B158 2B4T for ai/models
title: Bitnet B158 2B4T
updated_at: '2025-07-04'
version: 1.0.0
---

# Microsoft BITNET B1.58 2B4T

## Overview
BITNET B1.58 2B4T is a highly efficient Large Language Model (LLM) designed to run on standard CPUs with minimal energy consumption. It achieves competitive performance with a unique ternary quantization approach, using only -1, 0, and +1 as weight values, resulting in an average of 1.58 bits of information per weight.

## Key Features
- **Ternary Quantization:** Weights can only be -1, 0, or +1 (log₂(3) ≈ 1.58 bits).
- **No Float Memory:** Model is trained and operates in ternary space; no floating-point weights are used.
- **Post-Training Quantization:** Includes scripts for converting models to ternary after training.
- **Parameter Count:** ~2 billion parameters.
- **Training Data:** 4 trillion tokens.
- **Hardware Efficiency:**
  - Runs on 2–5GB VRAM or ~400MB RAM (with compression).
  - 85–96% lower energy draw than similar float-based models.
  - Demo: Apple M-series chip achieves 5–7 tokens/sec.
- **No Embedding Table:** Reduces memory footprint to 0.4GB.
- **Sub-layer Normalization:** Ensures model stability with simple squared ReLU activations.
- **Tokenizer:** Uses Llama 3's tokenizer for compatibility and efficiency.

## Performance Benchmarks
- **Macro Score (17 benchmarks):** 54.19% (float-based reference)
- **Llama QN 2.5 (comparison):** 55.23%
- **Logical Reasoning:**
  - ARC Challenge: 49.91%
  - ARC Easy: 74.79%
- **Math:**
  - GSM8K: 58.38%
  - Beating other 2B models and quantized models (e.g., Quan's: 56.79%)
- **Memory Footprint:**
  - Quantized: 0.7GB (double BITNET's footprint)
  - Outperforms 4-bit post-training models (e.g., GPTQ, AWQ)

## Model Analogy
Instead of storing information in massive floating-point jars, BITNET uses tiny colored poker chips:
- **Red:** -1
- **White:** 0
- **Blue:** +1

This shrinks the model from gigabytes to the size of a small mobile game download. The quantizer dynamically assigns chips during live inference.

## Training Method
1. **Pretraining:** Reads all available data at maximum speed (4T tokens).
2. **Cooldown:** Slows down to absorb details and prevent skimming.
3. **Fine-Tuning:** Practice exams with clear answers; uses grading points sum for stability.
4. **Direct Preference Optimization:** Two short passes with a microscopic learning rate, focusing on user preference.

## Engineering Details
- **Custom Software:** Bundles four chips into a byte, efficiently slides data across memory.
- **Math Engine:** Multiplies ternary chips with 8-bit bricks for fast inference.
- **Runs on CPUs:** No GPU required; ~400MB RAM.
- **Energy Efficiency:** Outperforms typical models in both memory and power usage.

## Limitations & Future Directions
- **Scaling Laws:** Needs further testing at 7–13B parameters and beyond.
- **Hardware:** Future accelerators may need specialized low-bit logic.
- **Context Window:** Currently 4K tokens; longer contexts under exploration.
- **Multilingual & Multimodal:** Early days for ternary models in these areas.

## Availability
- **Hugging Face:**
  - Ready pack
  - BF-16 master (requires retraining)
  - GGUF file (BITNET cpp)
- **Web Demo:** Available for testing

## References
- [BITNET on Hugging Face](https://huggingface.co/)
- [Benchmarks: MMLU, GSM8K, ARC-CHALLENGE, HELLASWAG, PI TRUTHFLUQA, etc.]

## Related Documents
- [Build & Train Model](../../machine_learning/workflow/build_train_model.md) - General model building concepts
- [Model Deployment](../../../temp_reorg/docs/machine_learning/workflow/deployment.md) - Deploying efficient models
- [Performance Evaluation](../../machine_learning/workflow/evaluate_performance.md) - Benchmarking and evaluation techniques

---

This documentation can be referenced in other areas of your knowledge base, such as deployment, quantization, and efficient model design.
