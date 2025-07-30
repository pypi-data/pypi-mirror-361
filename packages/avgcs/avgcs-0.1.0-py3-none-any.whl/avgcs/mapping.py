"""
Character mapping and configuration management for AVGCS.
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from .core import PartMapper


@dataclass
class MappingConfig:
    """Configuration for character part mappings."""
    name: str
    description: str
    character_type: str  # "humanoid", "animal", "vehicle", "custom"
    mappings: Dict[str, str]  # body_part -> character_part
    thresholds: Dict[str, float]  # character_part -> movement_threshold
    action_rules: Dict[str, Dict[str, Any]]  # character_part -> {action -> conditions}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MappingConfig':
        """Create config from dictionary."""
        return cls(**data)


class CharacterMapper:
    """Manages character mapping configurations."""
    
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = config_dir
        self.configs: Dict[str, MappingConfig] = {}
        self.current_config: Optional[MappingConfig] = None
        self.part_mapper = PartMapper()
        
        # Ensure config directory exists
        os.makedirs(config_dir, exist_ok=True)
        
        # Load existing configs
        self._load_configs()
    
    def create_config(self, name: str, description: str, character_type: str) -> MappingConfig:
        """Create a new mapping configuration."""
        config = MappingConfig(
            name=name,
            description=description,
            character_type=character_type,
            mappings={},
            thresholds={},
            action_rules={}
        )
        self.configs[name] = config
        return config
    
    def save_config(self, config: MappingConfig) -> bool:
        """Save a configuration to file."""
        try:
            config_path = os.path.join(self.config_dir, f"{config.name}.json")
            with open(config_path, 'w') as f:
                json.dump(config.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def load_config(self, name: str) -> Optional[MappingConfig]:
        """Load a configuration by name."""
        if name in self.configs:
            self.current_config = self.configs[name]
            # Apply mappings to part mapper
            self.part_mapper.clear_mappings()
            for body_part, character_part in self.current_config.mappings.items():
                self.part_mapper.add_mapping(body_part, character_part)
            return self.current_config
        return None
    
    def delete_config(self, name: str) -> bool:
        """Delete a configuration."""
        try:
            if name in self.configs:
                del self.configs[name]
                config_path = os.path.join(self.config_dir, f"{name}.json")
                if os.path.exists(config_path):
                    os.remove(config_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting config: {e}")
            return False
    
    def get_config_names(self) -> List[str]:
        """Get list of available configuration names."""
        return list(self.configs.keys())
    
    def get_current_config(self) -> Optional[MappingConfig]:
        """Get the currently loaded configuration."""
        return self.current_config
    
    def add_mapping(self, body_part: str, character_part: str) -> bool:
        """Add a mapping to the current configuration."""
        if not self.current_config:
            return False
        
        self.current_config.mappings[body_part] = character_part
        self.part_mapper.add_mapping(body_part, character_part)
        return True
    
    def remove_mapping(self, body_part: str) -> bool:
        """Remove a mapping from the current configuration."""
        if not self.current_config or body_part not in self.current_config.mappings:
            return False
        
        del self.current_config.mappings[body_part]
        self.part_mapper.remove_mapping(body_part)
        return True
    
    def set_threshold(self, character_part: str, threshold: float) -> bool:
        """Set movement threshold for a character part."""
        if not self.current_config:
            return False
        
        self.current_config.thresholds[character_part] = threshold
        return True
    
    def add_action_rule(self, character_part: str, action: str, 
                       conditions: Dict[str, Any]) -> bool:
        """Add an action rule for a character part."""
        if not self.current_config:
            return False
        
        if character_part not in self.current_config.action_rules:
            self.current_config.action_rules[character_part] = {}
        
        self.current_config.action_rules[character_part][action] = conditions
        return True
    
    def get_part_mapper(self) -> PartMapper:
        """Get the current part mapper."""
        return self.part_mapper
    
    def _load_configs(self) -> None:
        """Load all configuration files from the config directory."""
        if not os.path.exists(self.config_dir):
            return
        
        for filename in os.listdir(self.config_dir):
            if filename.endswith('.json'):
                try:
                    config_path = os.path.join(self.config_dir, filename)
                    with open(config_path, 'r') as f:
                        data = json.load(f)
                    
                    config = MappingConfig.from_dict(data)
                    self.configs[config.name] = config
                except Exception as e:
                    print(f"Error loading config {filename}: {e}")
    
    def create_preset_configs(self) -> None:
        """Create some preset configurations for common use cases."""
        presets = [
            {
                "name": "humanoid_basic",
                "description": "Basic humanoid character mapping",
                "character_type": "humanoid",
                "mappings": {
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
                "thresholds": {
                    "left_arm": 0.05,
                    "right_arm": 0.05,
                    "left_leg": 0.05,
                    "right_leg": 0.05,
                    "head": 0.03
                },
                "action_rules": {
                    "left_hand": {
                        "wave": {
                            "min_movement": 0.1,
                            "position_range": {
                                "x": [0.0, 0.3],
                                "y": [0.0, 0.5],
                                "z": [-0.5, 0.5]
                            }
                        }
                    },
                    "right_hand": {
                        "wave": {
                            "min_movement": 0.1,
                            "position_range": {
                                "x": [0.7, 1.0],
                                "y": [0.0, 0.5],
                                "z": [-0.5, 0.5]
                            }
                        }
                    }
                }
            },
            {
                "name": "dragon_creature",
                "description": "Dragon-like creature mapping",
                "character_type": "animal",
                "mappings": {
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
                "thresholds": {
                    "left_wing": 0.03,
                    "right_wing": 0.03,
                    "head": 0.02,
                    "tail_base": 0.04
                },
                "action_rules": {
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
            },
            {
                "name": "spaceship_control",
                "description": "Spaceship control mapping",
                "character_type": "vehicle",
                "mappings": {
                    "left_wrist": "thrust_control",
                    "right_wrist": "weapon_control",
                    "left_shoulder": "roll_control",
                    "right_shoulder": "pitch_control",
                    "nose": "targeting_system"
                },
                "thresholds": {
                    "thrust_control": 0.02,
                    "weapon_control": 0.02,
                    "roll_control": 0.03,
                    "pitch_control": 0.03,
                    "targeting_system": 0.01
                },
                "action_rules": {
                    "thrust_control": {
                        "fire_thrusters": {
                            "min_movement": 0.1,
                            "position_range": {
                                "y": [0.7, 1.0],
                                "x": [0.0, 1.0],
                                "z": [-0.5, 0.5]
                            }
                        }
                    },
                    "weapon_control": {
                        "fire_weapons": {
                            "min_movement": 0.05,
                            "position_range": {
                                "x": [0.7, 1.0],
                                "y": [0.0, 1.0],
                                "z": [-0.5, 0.5]
                            }
                        }
                    }
                }
            }
        ]
        
        for preset in presets:
            config = MappingConfig(**preset)
            self.configs[config.name] = config
            self.save_config(config) 