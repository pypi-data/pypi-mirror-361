# 🎮 AVGCS - Ashwath-Visual Game Control System

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/avgcs.svg)](https://badge.fury.io/py/avgcs)

**AVGCS** is a Python module for real-time motion tracking and game control. It enables you to control game characters using your body movements captured through a camera.

## ✨ Features

- **Real-time Motion Tracking**: Uses OpenCV and MediaPipe for accurate body part detection
- **Flexible Character Mapping**: Map any body part to any character part (humanoid, animals, vehicles, etc.)
- **Custom Action Rules**: Define custom gestures and movements to trigger specific actions
- **Multiple Tracking Modes**: Support for both MediaPipe (advanced) and basic camera tracking
- **Easy Integration**: Simple API for integrating with any game engine or application
- **Cross-platform**: Works on Windows, macOS, and Linux

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install avgcs
```

### Basic Usage

```python
from avgcs import MediaPipeTracker, CharacterMapper, MotionInterpreter

# Initialize motion tracking
tracker = MediaPipeTracker(camera_index=0)
tracker.start_tracking()

# Set up character mapping
mapper = CharacterMapper()
mapper.add_mapping("left_shoulder", "left_arm")
mapper.add_mapping("right_shoulder", "right_arm")
mapper.add_mapping("left_wrist", "left_hand")

# Create motion interpreter
interpreter = MotionInterpreter(mapper.get_part_mapper())

# Main loop
while True:
    motion_data = tracker.get_motion_data()
    if motion_data:
        commands = interpreter.interpret_motion(motion_data)
        for command in commands:
            print(f"{command.character_part}: {command.action}")
```

## 📖 Documentation

### Core Components

#### MotionTracker
Abstract base class for motion tracking systems.

```python
from avgcs import MediaPipeTracker, CameraTracker

# Advanced tracking with MediaPipe
tracker = MediaPipeTracker(camera_index=0)

# Basic tracking with OpenCV
tracker = CameraTracker(camera_index=0)
```

#### CharacterMapper
Manages mappings between body parts and character parts.

```python
from avgcs import CharacterMapper

mapper = CharacterMapper()

# Add mappings
mapper.add_mapping("left_shoulder", "left_arm")
mapper.add_mapping("right_shoulder", "right_arm")
mapper.add_mapping("left_wrist", "left_hand")

# Set movement thresholds
mapper.set_threshold("left_arm", 0.05)
mapper.set_threshold("right_arm", 0.05)
```

#### MotionInterpreter
Interprets motion data and generates game commands.

```python
from avgcs import MotionInterpreter

interpreter = MotionInterpreter(mapper.get_part_mapper())

# Add action rules
interpreter.add_action_rule("left_hand", "wave", {
    "min_movement": 0.1,
    "position_range": {
        "x": [0.0, 0.3],
        "y": [0.0, 0.5],
        "z": [-0.5, 0.5]
    }
})
```

### Character Types

AVGCS supports various character types:

#### Humanoid Characters
```python
mappings = {
    "left_shoulder": "left_arm",
    "right_shoulder": "right_arm",
    "left_wrist": "left_hand",
    "right_wrist": "right_hand",
    "nose": "head"
}
```

#### Dragon/Creature Characters
```python
mappings = {
    "left_shoulder": "left_wing",
    "right_shoulder": "right_wing",
    "left_wrist": "left_claw",
    "right_wrist": "right_claw",
    "nose": "head"
}
```

#### Vehicle/Spaceship Characters
```python
mappings = {
    "left_wrist": "thrust_control",
    "right_wrist": "weapon_control",
    "left_shoulder": "roll_control",
    "right_shoulder": "pitch_control"
}
```

## 🎯 Examples

### Basic Demo
Run the basic demo to see motion tracking in action:

```bash
python examples/basic_demo.py
```

### Pygame Demo
Run the visual Pygame demo:

```bash
python examples/pygame_demo.py
```

### Custom Configuration
Create your own character mapping:

```python
from avgcs import CharacterMapper, MappingConfig

mapper = CharacterMapper()

# Create a custom configuration
config = mapper.create_config(
    name="my_character",
    description="My custom character",
    character_type="custom"
)

# Add your mappings
mapper.add_mapping("left_shoulder", "custom_part_1")
mapper.add_mapping("right_shoulder", "custom_part_2")

# Save configuration
mapper.save_config(config)
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=avgcs

# Run specific test file
pytest tests/test_core.py
```

## 📦 Project Structure

```
avgcs/
├── avgcs/                 # Main package
│   ├── __init__.py       # Package initialization
│   ├── core.py           # Core classes and data structures
│   ├── tracking.py       # Motion tracking implementations
│   ├── mapping.py        # Character mapping system
│   └── utils.py          # Utility functions
├── examples/             # Example applications
│   ├── basic_demo.py     # Basic motion tracking demo
│   └── pygame_demo.py    # Visual Pygame demo
├── tests/                # Test suite
│   └── test_core.py      # Core functionality tests
├── configs/              # Configuration files
├── pyproject.toml        # Project configuration
└── README.md            # This file
```

## 🔧 Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/avgcs/avgcs.git
cd avgcs

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

### Code Quality

```bash
# Format code
black avgcs/ tests/ examples/

# Lint code
flake8 avgcs/ tests/ examples/

# Type checking
mypy avgcs/
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [MediaPipe](https://mediapipe.dev/) for advanced pose detection
- [OpenCV](https://opencv.org/) for computer vision capabilities
- [Pygame](https://www.pygame.org/) for the visual demo

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/avgcs/avgcs/issues)
- **Discussions**: [GitHub Discussions](https://github.com/avgcs/avgcs/discussions)
- **Email**: team@avgcs.dev

## 🗺️ Roadmap

- [ ] GUI mapping tool
- [ ] Gesture learning system
- [ ] Pre-built character profiles
- [ ] Support for multiple cameras
- [ ] Integration with popular game engines
- [ ] Mobile device support
- [ ] VR/AR integration

---

**Made with ❤️ by the AVGCS Team** 