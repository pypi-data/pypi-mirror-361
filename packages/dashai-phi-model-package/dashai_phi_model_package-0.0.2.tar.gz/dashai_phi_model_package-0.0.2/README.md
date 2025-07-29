# Phi Model Plugin for DashAI

This plugin integrates Microsoft's **Phi** language models into the DashAI framework using the `llama.cpp` backend. It provides a lightweight, efficient text generation system with support for quantized GGUF models.

## Included Models

### 1. Phi-3 Mini 4K Instruct

- 3.8B parameter lightweight model from the Phi-3 family
- Designed for high-quality output with strong reasoning abilities
- Trained on synthetic and filtered public datasets
- Fine-tuned with supervised techniques and direct preference optimization
- Based on [`microsoft/Phi-3-mini-4k-instruct-gguf`](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf)
- Uses GGUF file: `Phi-3-mini-4k-instruct-q4.gguf`

### 2. Phi-4

- State-of-the-art open model developed by Microsoft Research
- Trained on high-quality public domain content, academic books, and Q&A datasets
- Emphasizes precise instruction-following and strong safety alignment
- Based on [`microsoft/phi-4-gguf`](https://huggingface.co/microsoft/phi-4-gguf)
- Uses GGUF file: `phi-4-IQ3_M.gguf`

Both models use the **GGUF** format and are compatible with CPU and GPU inference.

## Components

### PhiModel

- Implements the `TextToTextGenerationTaskModel` interface from DashAI
- Uses the `llama.cpp` backend with GGUF support
- Automatically loads the correct quantized model file based on the selected model
- Performs chat-style completion with system/user/assistant messages

## Features

- Configurable text generation with:

  - `max_tokens`: Number of tokens to generate
  - `temperature`: Controls output randomness
  - `frequency_penalty`: Reduces repetition
  - `context_window`: Max tokens per forward pass
  - `device`: `"cpu"` or `"gpu"` (auto-detected)

- Efficient memory usage with quantized GGUF format
- Automatic model loading from Hugging Face
- Compatible with chat-style prompts (role-based message format)

## Model Parameters

| Parameter           | Description                                      | Default                                   |
| ------------------- | ------------------------------------------------ | ----------------------------------------- |
| `model_name`        | Model ID from Hugging Face                       | `"microsoft/Phi-3-mini-4k-instruct-gguf"` |
| `max_tokens`        | Maximum number of tokens to generate             | 100                                       |
| `temperature`       | Sampling temperature (higher = more random)      | 0.7                                       |
| `frequency_penalty` | Penalizes repeated tokens to encourage diversity | 0.1                                       |
| `context_window`    | Maximum context window (tokens in prompt)        | 512                                       |
| `device`            | Device for inference (`"gpu"` or `"cpu"`)        | Auto-detected                             |

## Requirements

- `DashAI`
- `llama-cpp-python`
- Model files from Hugging Face:
  - [`microsoft/Phi-3-mini-4k-instruct-gguf`](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf)
  - [`microsoft/phi-4-gguf`](https://huggingface.co/microsoft/phi-4-gguf)

## Notes

This plugin uses the **GGUF** format, introduced by the `llama.cpp` team in August 2023.  
GGUF replaces the older **GGML** format and is optimized for fast inference and low memory usage.

Both Phi-3 Mini and Phi-4 models have undergone **supervised fine-tuning** and **preference optimization** to improve instruction adherence and safety.

> ⚠️ These models are designed for **inference only** and are **not intended for fine-tuning**.
