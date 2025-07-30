# mobile_recorder

A Python package to record the screen of Android devices and perform automated operations using [uiautomator2](https://github.com/openatx/uiautomator2).

## Features

- Record Android device screen
- Run automated UI operations

## Installation

```bash
pip install mobile_recorder
```

## Requirements

- Python 3.7+
- [uiautomator2](https://github.com/openatx/uiautomator2)
- Android device with USB debugging enabled OR an android studio emulator

## Usage

```python
from mobile_recorder import AndroidRecorder

def handle_frame(img: MatLike | Image | None):
    ... # Here, the function does whatever you want

recorder = AndroidRecorder([handle_frame], device="mydevice123") # device name is optional
recorder.start_recording()
# The recording runs in the background
recorder.stop_recording()
```

## License

MIT 