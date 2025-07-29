# pyometrics

A Python library for creating and comparing voice biometrics using Gaussian Mixture Models (GMMs).
You can train a biometric model from a set of audio files and then compare new samples against that model to get a similarity score.

## Features

- MFCC + Delta Feature Extraction  
- GMM Training via scikit-learn  
- User-Defined Minimum Required Audio Files (min_files)  
- Supports .wav, .mp3, .m4a, .flac by default

## Installation

Install from PyPI:

```bash
pip install pyometrics
```

## Usage

1. Train (or create) a voice biometric:

```python
from pyometrics import create_voice_biometric

create_voice_biometric(
    folder_path="path/to/audio/folder",
    model_path="my_biometric.gmm",
    min_files=5  # specify how many audio files must exist
)
```

- The library expects at least ``min_files`` audio files in the folder.
- The GMM model is saved to the file ``my_biometric.gmm``.

2. Compare a new audio sample:

```python
from pyometrics import compare_voice_biometric

score = compare_voice_biometric(
    audio_path="path/to/new_audio.mp3",
    model_path="my_biometric.gmm"
)
print("Similarity Score (log-likelihood):", score)
```

- A higher (less negative) log-likelihood indicates closer similarity.

## Example

Suppose you have at least 10 .mp3 files of the same speaker in ``samples_for_biometric/``. You can do:

```python
from pyometrics import create_voice_biometric, compare_voice_biometric

create_voice_biometric(
    folder_path="samples_for_biometric",
    model_path="example.gmm",
    min_files=10
)

score = compare_voice_biometric(
    audio_path="test_sample.m4a",
    model_path="example.gmm"
)
print("Score:", score)  # The higher, the more similar
```

## Requirements

- Python 3.6+  
- librosa  
- numpy  
- scikit-learn

## License
This project is licensed under the [MIT License](LICENSE).