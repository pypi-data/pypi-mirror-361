"""
Utility functions for AVGCS.
"""

import json
import os
from typing import Dict, List, Any, Optional
from .mapping import MappingConfig


def load_config(file_path: str) -> Optional[MappingConfig]:
    """Load a mapping configuration from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return MappingConfig.from_dict(data)
    except Exception as e:
        print(f"Error loading config from {file_path}: {e}")
        return None


def save_config(config: MappingConfig, file_path: str) -> bool:
    """Save a mapping configuration to a JSON file."""
    try:
        with open(file_path, 'w') as f:
            json.dump(config.to_dict(), f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config to {file_path}: {e}")
        return False


def validate_mapping(mappings: Dict[str, str]) -> List[str]:
    """Validate mapping configuration and return any issues."""
    issues = []
    
    # Check for empty mappings
    if not mappings:
        issues.append("No mappings defined")
        return issues
    
    # Check for invalid mappings
    for body_part, character_part in mappings.items():
        if not body_part or not character_part:
            issues.append(f"Invalid mapping: {body_part} -> {character_part}")
        
        if not isinstance(body_part, str) or not isinstance(character_part, str):
            issues.append(f"Mapping keys and values must be strings: {body_part} -> {character_part}")
    
    # Check for duplicate body parts
    body_parts = list(mappings.keys())
    if len(body_parts) != len(set(body_parts)):
        issues.append("Duplicate body parts in mappings")
    
    # Check for duplicate character parts (this might be intentional, so just warn)
    character_parts = list(mappings.values())
    if len(character_parts) != len(set(character_parts)):
        issues.append("Warning: Multiple body parts mapped to same character part")
    
    return issues


def create_default_configs() -> Dict[str, MappingConfig]:
    """Create default mapping configurations."""
    configs = {}
    
    # Humanoid basic config
    humanoid_config = MappingConfig(
        name="humanoid_basic",
        description="Basic humanoid character mapping",
        character_type="humanoid",
        mappings={
            "left_shoulder": "left_arm",
            "right_shoulder": "right_arm",
            "left_elbow": "left_forearm",
            "right_elbow": "right_forearm",
            "left_wrist": "left_hand",
            "right_wrist": "right_hand",
            "left_hip": "left_leg",
            "right_hip": "right_leg",
            "left_knee": "left_calf",
            "right_knee": "right_calf",
            "nose": "head"
        },
        thresholds={
            "left_arm": 0.05,
            "right_arm": 0.05,
            "left_leg": 0.05,
            "right_leg": 0.05,
            "head": 0.03
        },
        action_rules={}
    )
    configs["humanoid_basic"] = humanoid_config
    
    # Dragon config
    dragon_config = MappingConfig(
        name="dragon_creature",
        description="Dragon-like creature mapping",
        character_type="animal",
        mappings={
            "left_shoulder": "left_wing",
            "right_shoulder": "right_wing",
            "left_elbow": "left_wing_tip",
            "right_elbow": "right_wing_tip",
            "left_wrist": "left_claw",
            "right_wrist": "right_claw",
            "nose": "head",
            "left_hip": "tail_base",
            "right_hip": "body"
        },
        thresholds={
            "left_wing": 0.03,
            "right_wing": 0.03,
            "head": 0.02,
            "tail_base": 0.04
        },
        action_rules={
            "left_wing": {
                "flap": {
                    "min_movement": 0.15,
                    "max_movement": 0.5
                }
            },
            "right_wing": {
                "flap": {
                    "min_movement": 0.15,
                    "max_movement": 0.5
                }
            }
        }
    )
    configs["dragon_creature"] = dragon_config
    
    return configs


def print_motion_data(motion_data) -> None:
    """Pretty print motion data for debugging."""
    if not motion_data:
        print("No motion data available")
        return
    
    print(f"Motion Data (t={motion_data.timestamp:.3f}):")
    print("  Body Parts:")
    for part, pos in motion_data.body_parts.items():
        conf = motion_data.confidence.get(part, 0.0)
        print(f"    {part}: {pos} (conf: {conf:.2f})")


def print_game_commands(commands: List) -> None:
    """Pretty print game commands for debugging."""
    if not commands:
        print("No game commands generated")
        return
    
    print(f"Game Commands ({len(commands)}):")
    for cmd in commands:
        print(f"  {cmd.character_part}: {cmd.action} (conf: {cmd.confidence:.2f})")
        if cmd.parameters:
            print(f"    Parameters: {cmd.parameters}")


def calculate_fps(start_time: float, frame_count: int) -> float:
    """Calculate frames per second."""
    elapsed_time = time.time() - start_time
    if elapsed_time > 0:
        return frame_count / elapsed_time
    return 0.0


def normalize_coordinates(x: float, y: float, z: float = 0.0) -> tuple:
    """Normalize coordinates to 0-1 range."""
    return (max(0.0, min(1.0, x)), max(0.0, min(1.0, y)), max(0.0, min(1.0, z)))


def calculate_distance(pos1: tuple, pos2: tuple) -> float:
    """Calculate Euclidean distance between two 3D points."""
    if len(pos1) != len(pos2):
        raise ValueError("Positions must have same dimensions")
    
    return sum((a - b) ** 2 for a, b in zip(pos1, pos2)) ** 0.5


def smooth_position(current_pos: tuple, previous_pos: tuple, 
                   smoothing_factor: float = 0.7) -> tuple:
    """Apply smoothing to position data."""
    if not previous_pos:
        return current_pos
    
    smoothed = []
    for curr, prev in zip(current_pos, previous_pos):
        smoothed_val = prev * smoothing_factor + curr * (1 - smoothing_factor)
        smoothed.append(smoothed_val)
    
    return tuple(smoothed)


def detect_gesture(positions: List[tuple], gesture_pattern: List[tuple], 
                  threshold: float = 0.1) -> bool:
    """Detect if a sequence of positions matches a gesture pattern."""
    if len(positions) < len(gesture_pattern):
        return False
    
    # Simple pattern matching - can be enhanced with more sophisticated algorithms
    for i, pattern_pos in enumerate(gesture_pattern):
        if i >= len(positions):
            return False
        
        distance = calculate_distance(positions[i], pattern_pos)
        if distance > threshold:
            return False
    
    return True


# Import time for FPS calculation
import time 