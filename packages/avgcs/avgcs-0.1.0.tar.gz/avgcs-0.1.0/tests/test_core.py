"""
Unit tests for AVGCS core functionality.
"""

import unittest
import time
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add the parent directory to the path so we can import avgcs
sys.path.insert(0, str(Path(__file__).parent.parent))

from avgcs.core import MotionData, GameCommand, PartMapper, MotionInterpreter


class TestMotionData(unittest.TestCase):
    """Test MotionData class."""
    
    def test_motion_data_creation(self):
        """Test creating MotionData objects."""
        timestamp = time.time()
        body_parts = {"left_hand": (0.5, 0.3, 0.0)}
        confidence = {"left_hand": 0.8}
        
        motion_data = MotionData(timestamp, body_parts, confidence)
        
        self.assertEqual(motion_data.timestamp, timestamp)
        self.assertEqual(motion_data.body_parts, body_parts)
        self.assertEqual(motion_data.confidence, confidence)
    
    def test_motion_data_empty(self):
        """Test creating empty MotionData."""
        timestamp = time.time()
        motion_data = MotionData(timestamp, {}, {})
        
        self.assertEqual(motion_data.timestamp, timestamp)
        self.assertEqual(motion_data.body_parts, {})
        self.assertEqual(motion_data.confidence, {})


class TestGameCommand(unittest.TestCase):
    """Test GameCommand class."""
    
    def test_game_command_creation(self):
        """Test creating GameCommand objects."""
        timestamp = time.time()
        command = GameCommand(
            timestamp=timestamp,
            character_part="left_arm",
            action="move",
            parameters={"movement": 0.1},
            confidence=0.8
        )
        
        self.assertEqual(command.timestamp, timestamp)
        self.assertEqual(command.character_part, "left_arm")
        self.assertEqual(command.action, "move")
        self.assertEqual(command.parameters, {"movement": 0.1})
        self.assertEqual(command.confidence, 0.8)


class TestPartMapper(unittest.TestCase):
    """Test PartMapper class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mapper = PartMapper()
    
    def test_add_mapping(self):
        """Test adding mappings."""
        self.mapper.add_mapping("left_shoulder", "left_arm")
        self.mapper.add_mapping("right_shoulder", "right_arm")
        
        self.assertEqual(self.mapper.get_character_part("left_shoulder"), "left_arm")
        self.assertEqual(self.mapper.get_character_part("right_shoulder"), "right_arm")
        self.assertIn("left_arm", self.mapper.character_parts)
        self.assertIn("right_arm", self.mapper.character_parts)
    
    def test_remove_mapping(self):
        """Test removing mappings."""
        self.mapper.add_mapping("left_shoulder", "left_arm")
        self.mapper.add_mapping("right_shoulder", "right_arm")
        
        self.mapper.remove_mapping("left_shoulder")
        
        self.assertIsNone(self.mapper.get_character_part("left_shoulder"))
        self.assertEqual(self.mapper.get_character_part("right_shoulder"), "right_arm")
        self.assertNotIn("left_arm", self.mapper.character_parts)
        self.assertIn("right_arm", self.mapper.character_parts)
    
    def test_clear_mappings(self):
        """Test clearing all mappings."""
        self.mapper.add_mapping("left_shoulder", "left_arm")
        self.mapper.add_mapping("right_shoulder", "right_arm")
        
        self.mapper.clear_mappings()
        
        self.assertEqual(self.mapper.get_all_mappings(), {})
        self.assertEqual(self.mapper.character_parts, [])
    
    def test_get_all_mappings(self):
        """Test getting all mappings."""
        self.mapper.add_mapping("left_shoulder", "left_arm")
        self.mapper.add_mapping("right_shoulder", "right_arm")
        
        mappings = self.mapper.get_all_mappings()
        expected = {"left_shoulder": "left_arm", "right_shoulder": "right_arm"}
        
        self.assertEqual(mappings, expected)
    
    def test_validate_mappings(self):
        """Test mapping validation."""
        # Valid mappings
        self.mapper.add_mapping("left_shoulder", "left_arm")
        issues = self.mapper.validate_mappings()
        self.assertEqual(issues, [])
        
        # Invalid mapping (empty string)
        self.mapper.add_mapping("", "invalid")
        issues = self.mapper.validate_mappings()
        self.assertIn("Invalid mapping:  -> invalid", issues)


class TestMotionInterpreter(unittest.TestCase):
    """Test MotionInterpreter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.part_mapper = PartMapper()
        self.part_mapper.add_mapping("left_hand", "left_arm")
        self.part_mapper.add_mapping("right_hand", "right_arm")
        
        self.interpreter = MotionInterpreter(self.part_mapper)
    
    def test_set_threshold(self):
        """Test setting movement thresholds."""
        self.interpreter.set_threshold("left_arm", 0.1)
        self.interpreter.set_threshold("right_arm", 0.2)
        
        self.assertEqual(self.interpreter.thresholds["left_arm"], 0.1)
        self.assertEqual(self.interpreter.thresholds["right_arm"], 0.2)
    
    def test_add_action_rule(self):
        """Test adding action rules."""
        conditions = {"min_movement": 0.1}
        self.interpreter.add_action_rule("left_arm", "wave", conditions)
        
        self.assertIn("left_arm", self.interpreter.actions)
        self.assertIn("wave", self.interpreter.actions["left_arm"])
        self.assertEqual(self.interpreter.actions["left_arm"]["wave"], conditions)
    
    def test_interpret_motion_no_movement(self):
        """Test interpreting motion with no significant movement."""
        # Create motion data with no movement
        motion_data = MotionData(
            timestamp=time.time(),
            body_parts={"left_hand": (0.5, 0.5, 0.0)},
            confidence={"left_hand": 0.8}
        )
        
        # Set a high threshold
        self.interpreter.set_threshold("left_arm", 1.0)
        
        commands = self.interpreter.interpret_motion(motion_data)
        self.assertEqual(len(commands), 0)
    
    def test_interpret_motion_with_movement(self):
        """Test interpreting motion with significant movement."""
        # First frame
        motion_data1 = MotionData(
            timestamp=time.time(),
            body_parts={"left_hand": (0.5, 0.5, 0.0)},
            confidence={"left_hand": 0.8}
        )
        
        # Second frame with movement
        motion_data2 = MotionData(
            timestamp=time.time(),
            body_parts={"left_hand": (0.7, 0.7, 0.0)},
            confidence={"left_hand": 0.8}
        )
        
        # Set a low threshold
        self.interpreter.set_threshold("left_arm", 0.1)
        
        # Process first frame (should not generate commands)
        commands1 = self.interpreter.interpret_motion(motion_data1)
        self.assertEqual(len(commands1), 0)
        
        # Process second frame (should generate movement command)
        commands2 = self.interpreter.interpret_motion(motion_data2)
        self.assertGreater(len(commands2), 0)
        
        # Check command properties
        command = commands2[0]
        self.assertEqual(command.character_part, "left_arm")
        self.assertEqual(command.action, "move")
        self.assertIn("movement", command.parameters)
        self.assertEqual(command.confidence, 0.8)
    
    def test_interpret_motion_with_action_rule(self):
        """Test interpreting motion that triggers action rules."""
        # Set up action rule
        self.interpreter.add_action_rule("left_arm", "wave", {
            "min_movement": 0.1,
            "position_range": {
                "x": [0.0, 1.0],
                "y": [0.0, 1.0],
                "z": [-1.0, 1.0]
            }
        })
        
        # First frame
        motion_data1 = MotionData(
            timestamp=time.time(),
            body_parts={"left_hand": (0.5, 0.5, 0.0)},
            confidence={"left_hand": 0.8}
        )
        
        # Second frame with movement in valid range
        motion_data2 = MotionData(
            timestamp=time.time(),
            body_parts={"left_hand": (0.7, 0.7, 0.0)},
            confidence={"left_hand": 0.8}
        )
        
        # Process frames
        self.interpreter.interpret_motion(motion_data1)  # First frame
        commands = self.interpreter.interpret_motion(motion_data2)  # Second frame
        
        # Should have both movement and wave commands
        self.assertGreaterEqual(len(commands), 1)
        
        # Check for wave command
        wave_commands = [cmd for cmd in commands if cmd.action == "wave"]
        self.assertGreater(len(wave_commands), 0)
    
    def test_calculate_movement(self):
        """Test movement calculation."""
        pos1 = (0.0, 0.0, 0.0)
        pos2 = (3.0, 4.0, 0.0)
        
        movement = self.interpreter._calculate_movement(pos1, pos2)
        self.assertEqual(movement, 5.0)  # 3-4-5 triangle
    
    def test_check_action_conditions(self):
        """Test action condition checking."""
        position = (0.5, 0.5, 0.0)
        movement = 0.2
        
        # Test min_movement condition
        conditions = {"min_movement": 0.1}
        self.assertTrue(self.interpreter._check_action_conditions(position, movement, conditions))
        
        conditions = {"min_movement": 0.3}
        self.assertFalse(self.interpreter._check_action_conditions(position, movement, conditions))
        
        # Test max_movement condition
        conditions = {"max_movement": 0.3}
        self.assertTrue(self.interpreter._check_action_conditions(position, movement, conditions))
        
        conditions = {"max_movement": 0.1}
        self.assertFalse(self.interpreter._check_action_conditions(position, movement, conditions))
        
        # Test position_range condition
        conditions = {
            "position_range": {
                "x": [0.0, 1.0],
                "y": [0.0, 1.0],
                "z": [-1.0, 1.0]
            }
        }
        self.assertTrue(self.interpreter._check_action_conditions(position, movement, conditions))
        
        conditions = {
            "position_range": {
                "x": [0.0, 0.3],
                "y": [0.0, 1.0],
                "z": [-1.0, 1.0]
            }
        }
        self.assertFalse(self.interpreter._check_action_conditions(position, movement, conditions))


if __name__ == "__main__":
    unittest.main() 