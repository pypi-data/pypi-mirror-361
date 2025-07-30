# Modern Speech-to-Text (MSTT)

Modern Speech-to-Text (MSTT) is a Python library designed to provide a unified and extensible interface for various Speech-to-Text (STT) models. It aims to simplify the process of integrating different STT services and models into your applications, offering a consistent API regardless of the underlying STT engine.

## Features

- **Unified API**: Interact with multiple STT models through a single, consistent interface.
- **Extensible Design**: Easily add support for new STT models and services.
- **Local and Cloud Support**: Seamlessly switch between local models and cloud-based STT APIs.
- **Plugin System**: Integrate custom STT models or enhance existing functionalities via a flexible plugin system.

## Installation

To install MSTT, you can use `pip`:

```bash
pip install mstt
```

If you want to install with specific STT model backends, you can specify them as extras. For example, to install with `funasr` support:

```bash
pip install mstt[funasr]
```

## Usage

### Basic Transcription

Here's a basic example of how to use MSTT to transcribe an audio file:

```python
from mstt import get_model

asr_model = get_model("openai/whisper-tiny")
result = asr_model.transcribe("examples/test_audio_zh.wav")

print(f"Transcription: {result.text}")
```

### Available Models

MSTT supports various models through its plugin system. You can list available models:

```python
mstt models
```

### Command Line Interface (CLI)

MSTT also provides a command-line interface for quick transcriptions:

```bash
# You can use asr model on huggingface out-of-box
mstt transcribe --model openai/whisper-tiny  path/to/your/audio.wav
```

Run `mstt --help` for more CLI options.

## Creating Custom Plugins

MSTT is designed to be extensible through a plugin system. You can create your own STT model plugins and register them with MSTT.

### Plugin Structure

A plugin typically consists of:

1.  **A Model Implementation**: A Python class that inherits from `mstt.models.STTModel` and implements the `transcribe` method.
2.  **A Registration Module**: A Python module that registers your model with MSTT using the `mstt.register_model` decorator.

### Example: A Simple Custom Plugin

Let's say you want to create a plugin for a hypothetical `MyCustomSTT` model. You would create a Python package (e.g., `mstt_mycustom`):

```
mstt_mycustom/
├── pyproject.toml
├── src/
│   └── mstt_mycustom/
│       ├── __init__.py
│       ├── models.py
│       └── register.py
```

**`src/mstt_mycustom/models.py`**:

```python
from mstt.models import AsrModel
from mstt.types import TranscriptionResult, Segment

class MyCustomSTTModel(AsrModel):
    def __init__(self, model_id: str, device: str = "cpu"):
        super().__init__(model_id, device)
        # Initialize your custom model here
        print(f"Initializing MyCustomSTTModel with ID: {model_id} on device: {device}")

    def transcribe(self, audio_file_path: str) -> TranscriptionResult:
        # Implement your transcription logic here
        # This is a placeholder for demonstration
        print(f"Transcribing {audio_file_path} using MyCustomSTTModel")
        dummy_text = "This is a custom transcription result."
        dummy_segments = [
            {"start": 0.0, "end": 2.0, "text": "This is a custom"},
            {"start": 2.1, "end": 4.0, "text": "transcription result."}
        ]
        return TranscriptionResult(text=dummy_text, segments=dummy_segments)
```

**`src/mstt_mycustom/register.py`**:

```python
from mstt.plugin import hookimpl
from .models import MyCustomSTTModel

@hookimpl
def register_models(registry):
    """Registers Custom models with the central registry."""

    registry.register("funasr/iic/SenseVoiceSmall", MyCustomSTTModel)
    registry.register("alias", MyCustomSTTModel)
```
**`pyproject.toml`** (important for plugin discovery):

```toml
[project.entry-points.mstt]
mycustom = "mstt_mycustom.register"
```

### Installing Your Plugin

After setting up your plugin package, you can install it in editable mode for development:

```bash
pip install -e /path/to/your/mstt_mycustom
```

Or, if you package it, install it like any other Python package:

```bash
pip install mstt-mycustom
```

Once installed, MSTT will automatically discover and load your `mycustom` model, and you can use it like any other built-in model:

```python
from mstt import get_model

asr_model = get_model("mycustom")
result = asr_model.transcribe("path/to/your/audio.wav")
print(result.text)
```

## Contributing

We welcome contributions to MSTT! If you'd like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature-name`).
3. Make your changes.
4. Write and run tests (`pytest`).
5. Commit your changes (`git commit -am 'Add new feature'`).
6. Push to the branch (`git push origin feature/your-feature-name`).
7. Create a new Pull Request.

## License

This project is licensed under the Apache License, Version 2.0 - see the LICENSE file for details.