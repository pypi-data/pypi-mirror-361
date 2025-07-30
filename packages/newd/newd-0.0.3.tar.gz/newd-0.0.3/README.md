## Overview

 `newd` analyzes images and identifies specific NSFW body parts with high accuracy. It can also optionally censor detected areas.

## Installation

```bash
pip install newd
```

## Usage

### Basic Detection

```python
from newd import detect

# Standard detection with default settings
results = detect('path/to/image.jpg')
print(results)
```

### Advanced Options

```python
# Faster detection with slightly reduced accuracy
results = detect('image.jpg', mode="fast")

# Adjust detection sensitivity
results = detect('image.jpg', min_prob=0.3)  # Lower threshold catches more potential matches

# Combine options
results = detect('image.jpg', mode="fast", min_prob=0.3)
```

### Compatible Input Types

The `detect()` function accepts:
- String file paths
- Images loaded with OpenCV (`cv2`)
- Images loaded with PIL/Pillow

## Output Format

Detection results are returned as a list of dictionaries:

```python
[
  {
    'box': [x1, y1, x2, y2],  # Bounding box coordinates (top-left, bottom-right)
    'score': 0.825,           # Confidence score (0-1)
    'label': 'EXPOSED_BREAST_F'  # Classification label
  },
  # Additional detections...
]
```

## First-Time Use

When importing `newd` for the first time, it will download a 139MB model file to your home directory (`~/.newd/`). This happens only once.

## Performance Notes

- Standard mode: Best accuracy, normal processing speed
- Fast mode: ~3x faster processing with slightly reduced accuracy



