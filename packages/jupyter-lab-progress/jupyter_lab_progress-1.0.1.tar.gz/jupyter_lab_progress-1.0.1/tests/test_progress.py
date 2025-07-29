"""Tests for progress tracking functionality."""

import pytest
import tempfile
import os
from jupyter_lab_utils import LabProgress


class TestLabProgress:
    """Test cases for LabProgress class."""

    def test_basic_progress_creation(self):
        """Test basic progress tracker creation."""
        steps = ["Step 1", "Step 2", "Step 3"]
        progress = LabProgress(steps, lab_name="Test Lab")
        
        assert progress.lab_name == "Test Lab"
        assert len(progress.steps) == 3
        assert all(not step_info['completed'] for step_info in progress.steps.values())

    def test_mark_done(self):
        """Test marking steps as done."""
        steps = ["Step 1", "Step 2"]
        progress = LabProgress(steps)
        
        progress.mark_done("Step 1", score=95, notes="Great work!")
        
        assert progress.steps["Step 1"]["completed"] is True
        assert progress.steps["Step 1"]["score"] == 95
        assert progress.steps["Step 1"]["notes"] == "Great work!"
        assert progress.steps["Step 2"]["completed"] is False

    def test_completion_rate(self):
        """Test completion rate calculation."""
        steps = ["Step 1", "Step 2", "Step 3", "Step 4"]
        progress = LabProgress(steps)
        
        assert progress.get_completion_rate() == 0.0
        
        progress.mark_done("Step 1")
        assert progress.get_completion_rate() == 25.0
        
        progress.mark_done("Step 2")
        assert progress.get_completion_rate() == 50.0

    def test_average_score(self):
        """Test average score calculation."""
        steps = ["Step 1", "Step 2", "Step 3"]
        progress = LabProgress(steps)
        
        assert progress.get_average_score() is None
        
        progress.mark_done("Step 1", score=90)
        progress.mark_done("Step 2", score=80)
        
        assert progress.get_average_score() == 85.0

    def test_persistence(self):
        """Test progress persistence."""
        with tempfile.TemporaryDirectory() as temp_dir:
            persist_file = os.path.join(temp_dir, "test_progress.json")
            steps = ["Step 1", "Step 2"]
            
            # Create progress and mark one step
            progress1 = LabProgress(steps, persist=True, persist_file=persist_file)
            progress1.mark_done("Step 1", score=95)
            
            # Create new progress instance and verify it loads saved data
            progress2 = LabProgress(steps, persist=True, persist_file=persist_file)
            
            assert progress2.steps["Step 1"]["completed"] is True
            assert progress2.steps["Step 1"]["score"] == 95

    def test_partial_progress(self):
        """Test partial progress tracking."""
        steps = ["Step 1"]
        progress = LabProgress(steps)
        
        progress.mark_partial("Step 1", 0.75, notes="Halfway there")
        
        assert progress.steps["Step 1"]["progress"] == 0.75
        assert progress.steps["Step 1"]["notes"] == "Halfway there"

    def test_reset_functionality(self):
        """Test reset functionality."""
        steps = ["Step 1", "Step 2"]
        progress = LabProgress(steps)
        
        progress.mark_done("Step 1", score=95)
        progress.mark_done("Step 2", score=85)
        
        # Reset single step
        progress.reset_step("Step 1")
        assert progress.steps["Step 1"]["completed"] is False
        assert progress.steps["Step 1"]["score"] is None
        assert progress.steps["Step 2"]["completed"] is True
        
        # Reset all
        progress.reset_all()
        assert all(not step_info['completed'] for step_info in progress.steps.values())

    def test_export_report(self):
        """Test report export functionality."""
        steps = ["Step 1", "Step 2"]
        progress = LabProgress(steps, lab_name="Test Lab")
        
        progress.mark_done("Step 1", score=95)
        
        report = progress.export_report()
        
        assert "Test Lab" in report
        assert "Step 1: ✅ Completed" in report
        assert "Step 2: ⏳ Pending" in report
        assert "50.0%" in report