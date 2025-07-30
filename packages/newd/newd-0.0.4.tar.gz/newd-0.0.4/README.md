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

---

## Censoring / Redacting Detected Regions

`newd.censor()` masks detected NSFW regions with solid black rectangles. Use it when you need to create a safe-for-work version of an image.

```python
from newd import censor

# Censor all detected areas and write the result
censored_img = censor(
    'image.jpg',
    out_path='image_censored.jpg'  # file will be written to disk
)

# Only censor specific labels (e.g. exposed anus & male genitals)
selected_parts = ['EXPOSED_ANUS_F', 'EXPOSED_GENITALIA_M']
censored_img = censor(
    'image.jpg',
    out_path='image_censored.jpg',
    parts_to_blur=selected_parts
)
```

Function parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `img_path` | str / Path | Source image or path. |
| `out_path` | str / Path, optional | Destination path; if omitted you can still obtain the result via the return value when `visualize=True`. |
| `visualize` | bool, default `False` | If `True`, the censored `numpy.ndarray` image is returned for display (`cv2.imshow`, etc.). |
| `parts_to_blur` | List[str], optional | Restrict censoring to given label names. When empty, all detected labels are censored. |

If neither `out_path` nor `visualize=True` is supplied, the function exits early because there is nowhere to deliver the censored image.

---



