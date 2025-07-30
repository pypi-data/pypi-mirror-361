"""
Core AVGCS classes for motion tracking, part mapping, and interpretation.
"""

import json
import time
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class MotionData:
    """Standardized motion data structure."""
    timestamp: float
    body_parts: Dict[str, Tuple[float, float, float]]  # part_name -> (x, y, z)
    confidence: Dict[str, float]  # part_name -> confidence_score


@dataclass
class GameCommand:
    """Standardized game command output."""
    timestamp: float
    character_part: str
    action: str
    parameters: Dict[str, Any]
    confidence: float


class MotionTracker(ABC):
    """Abstract base class for motion tracking systems."""
    
    @abstractmethod
    def start_tracking(self) -> bool:
        """Start the motion tracking system."""
        pass
    
    @abstractmethod
    def stop_tracking(self) -> None:
        """Stop the motion tracking system."""
        pass
    
    @abstractmethod
    def get_motion_data(self) -> Optional[MotionData]:
        """Get current motion data."""
        pass
    
    @abstractmethod
    def is_tracking(self) -> bool:
        """Check if tracking is active."""
        pass


class PartMapper:
    """Maps human body parts to character parts."""
    
    def __init__(self):
        self.mappings: Dict[str, str] = {}
        self.character_parts: List[str] = []
    
    def add_mapping(self, body_part: str, character_part: str) -> None:
        """Add a mapping from body part to character part."""
        self.mappings[body_part] = character_part
        if character_part not in self.character_parts:
            self.character_parts.append(character_part)
    
    def remove_mapping(self, body_part: str) -> None:
        """Remove a mapping."""
        if body_part in self.mappings:
            character_part = self.mappings[body_part]
            del self.mappings[body_part]
            # Remove character part if no other mappings use it
            if not any(cp == character_part for cp in self.mappings.values()):
                self.character_parts.remove(character_part)
    
    def get_character_part(self, body_part: str) -> Optional[str]:
        """Get the character part mapped to a body part."""
        return self.mappings.get(body_part)
    
    def get_all_mappings(self) -> Dict[str, str]:
        """Get all current mappings."""
        return self.mappings.copy()
    
    def clear_mappings(self) -> None:
        """Clear all mappings."""
        self.mappings.clear()
        self.character_parts.clear()
    
    def validate_mappings(self) -> List[str]:
        """Validate mappings and return any issues."""
        issues = []
        for body_part, character_part in self.mappings.items():
            if not body_part or not character_part:
                issues.append(f"Invalid mapping: {body_part} -> {character_part}")
        return issues


class MotionInterpreter:
    """Interprets motion data and generates game commands."""
    
    def __init__(self, part_mapper: PartMapper):
        self.part_mapper = part_mapper
        self.thresholds: Dict[str, float] = {}
        self.actions: Dict[str, Dict[str, Any]] = {}
        self.previous_positions: Dict[str, Tuple[float, float, float]] = {}
    
    def set_threshold(self, character_part: str, threshold: float) -> None:
        """Set movement threshold for a character part."""
        self.thresholds[character_part] = threshold
    
    def add_action_rule(self, character_part: str, action: str, 
                       conditions: Dict[str, Any]) -> None:
        """Add an action rule for a character part."""
        if character_part not in self.actions:
            self.actions[character_part] = {}
        self.actions[character_part][action] = conditions
    
    def interpret_motion(self, motion_data: MotionData) -> List[GameCommand]:
        """Interpret motion data and generate game commands."""
        commands = []
        
        for body_part, position in motion_data.body_parts.items():
            character_part = self.part_mapper.get_character_part(body_part)
            if not character_part:
                continue
            
            confidence = motion_data.confidence.get(body_part, 0.0)
            
            # Check for movement
            if body_part in self.previous_positions:
                prev_pos = self.previous_positions[body_part]
                movement = self._calculate_movement(prev_pos, position)
                
                # Check thresholds
                threshold = self.thresholds.get(character_part, 0.1)
                if movement > threshold:
                    # Generate movement command
                    command = GameCommand(
                        timestamp=motion_data.timestamp,
                        character_part=character_part,
                        action="move",
                        parameters={"movement": movement, "position": position},
                        confidence=confidence
                    )
                    commands.append(command)
                
                # Check action rules
                if character_part in self.actions:
                    for action, conditions in self.actions[character_part].items():
                        if self._check_action_conditions(position, movement, conditions):
                            command = GameCommand(
                                timestamp=motion_data.timestamp,
                                character_part=character_part,
                                action=action,
                                parameters=conditions.get("parameters", {}),
                                confidence=confidence
                            )
                            commands.append(command)
            
            # Update previous position
            self.previous_positions[body_part] = position
        
        return commands
    
    def _calculate_movement(self, prev_pos: Tuple[float, float, float], 
                          curr_pos: Tuple[float, float, float]) -> float:
        """Calculate movement distance between two positions."""
        dx = curr_pos[0] - prev_pos[0]
        dy = curr_pos[1] - prev_pos[1]
        dz = curr_pos[2] - prev_pos[2]
        return (dx**2 + dy**2 + dz**2)**0.5
    
    def _check_action_conditions(self, position: Tuple[float, float, float],
                               movement: float, conditions: Dict[str, Any]) -> bool:
        """Check if action conditions are met."""
        # Simple condition checking - can be expanded
        if "min_movement" in conditions and movement < conditions["min_movement"]:
            return False
        if "max_movement" in conditions and movement > conditions["max_movement"]:
            return False
        if "position_range" in conditions:
            x, y, z = position
            min_x, max_x = conditions["position_range"]["x"]
            min_y, max_y = conditions["position_range"]["y"]
            min_z, max_z = conditions["position_range"]["z"]
            if not (min_x <= x <= max_x and min_y <= y <= max_y and min_z <= z <= max_z):
                return False
        return True 