"""
Tests for the AuraTrace CLI module.
"""

import pytest
import pandas as pd
import tempfile
import os
import json
import yaml
from unittest.mock import Mock, patch, MagicMock
from typer.testing import CliRunner
from pathlib import Path

from auratrace.cli import app


class TestCLI:
    """Test cases for the CLI module."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI runner for testing."""
        return CliRunner()
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield tmp_dir
    
    def test_cli_app_creation(self):
        """Test CLI app creation."""
        assert app is not None
        assert hasattr(app, 'get_help')
    
    def test_run_command_basic(self, runner, temp_dir):
        """Test basic run command."""
        # Create a simple Python script
        script_path = os.path.join(temp_dir, "test_script.py")
        with open(script_path, 'w') as f:
            f.write("""
import pandas as pd
df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
print("Script executed successfully")
""")
        
        result = runner.invoke(app, ["run", script_path])
        
        assert result.exit_code == 0
        assert "Script executed successfully" in result.stdout
    
    def test_run_command_with_output(self, runner, temp_dir):
        """Test run command with output directory."""
        # Create a simple Python script
        script_path = os.path.join(temp_dir, "test_script.py")
        output_dir = os.path.join(temp_dir, "output")
        
        with open(script_path, 'w') as f:
            f.write("""
import pandas as pd
df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
print("Script executed successfully")
""")
        
        result = runner.invoke(app, ["run", script_path, "--output", output_dir])
        
        assert result.exit_code == 0
        assert "Script executed successfully" in result.stdout
        assert os.path.exists(output_dir)
    
    def test_run_command_nonexistent_script(self, runner):
        """Test run command with nonexistent script."""
        result = runner.invoke(app, ["run", "nonexistent_script.py"])
        
        assert result.exit_code != 0
        assert "Error" in result.stdout or "not found" in result.stdout
    
    def test_view_command(self, runner, temp_dir):
        """Test view command."""
        # Create a session file
        session_file = os.path.join(temp_dir, "session.json")
        session_data = {
            "dataframes": {
                "df1": {
                    "dataframe_id": "df1",
                    "shape": [3, 2],
                    "columns": ["A", "B"],
                    "row_count": 3,
                    "column_count": 2
                }
            },
            "operations": [
                {
                    "operation_id": "op1",
                    "operation_name": "merge",
                    "execution_time": 1.5,
                    "memory_delta": 500
                }
            ]
        }
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        
        result = runner.invoke(app, ["view", session_file])
        
        assert result.exit_code == 0
        assert "df1" in result.stdout
        assert "merge" in result.stdout
    
    def test_view_command_nonexistent_file(self, runner):
        """Test view command with nonexistent file."""
        result = runner.invoke(app, ["view", "nonexistent_session.json"])
        
        assert result.exit_code != 0
        assert "Error" in result.stdout or "not found" in result.stdout
    
    def test_ask_command(self, runner, temp_dir):
        """Test ask command."""
        # Create a session file
        session_file = os.path.join(temp_dir, "session.json")
        session_data = {
            "dataframes": {
                "df1": {
                    "dataframe_id": "df1",
                    "shape": [3, 2],
                    "columns": ["A", "B"],
                    "row_count": 3,
                    "column_count": 2
                }
            }
        }
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        
        # Mock AI assistant
        with patch('auratrace.cli.AIAssistant') as mock_assistant_class:
            mock_assistant = Mock()
            mock_assistant.ask_question.return_value = Mock(
                query="What is the data shape?",
                response="The dataframe has 3 rows and 2 columns.",
                timestamp=1234567890.0
            )
            mock_assistant.is_available.return_value = True
            mock_assistant_class.return_value = mock_assistant
            
            result = runner.invoke(app, ["ask", session_file, "What is the data shape?", "--provider", "huggingface", "--model", "mistralai/Mistral-7B-Instruct-v0.2"])
            
            assert result.exit_code == 0
            assert "3 rows and 2 columns" in result.stdout

    def test_ask_command_no_ai(self, runner, temp_dir):
        """Test ask command without AI configuration."""
        # Create a session file
        session_file = os.path.join(temp_dir, "session.json")
        session_data = {"dataframes": {}}
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        
        with patch('auratrace.cli.AIAssistant') as mock_assistant_class:
            mock_assistant = Mock()
            mock_assistant.is_available.return_value = False
            mock_assistant_class.return_value = mock_assistant
            result = runner.invoke(app, ["ask", session_file, "Test question"])
            # Should handle gracefully without AI
            assert result.exit_code == 1
            assert "AI assistant is not ready" in result.stdout

    def test_ask_command_with_api_key(self, runner, temp_dir):
        """Test ask command with API key option."""
        session_file = os.path.join(temp_dir, "session.json")
        session_data = {"dataframes": {}}
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        with patch('auratrace.cli.AIAssistant') as mock_assistant_class:
            mock_assistant = Mock()
            mock_assistant.ask_question.return_value = Mock(
                query="Test?",
                response="Test response.",
                timestamp=1234567890.0
            )
            mock_assistant.is_available.return_value = True
            mock_assistant_class.return_value = mock_assistant
            result = runner.invoke(app, ["ask", session_file, "Test?", "--provider", "openai", "--api-key", "sk-test"])
            assert result.exit_code == 0
            assert "Test response." in result.stdout
    
    def test_compare_command(self, runner, temp_dir):
        """Test compare command."""
        # Create two session files
        session1_file = os.path.join(temp_dir, "session1.json")
        session2_file = os.path.join(temp_dir, "session2.json")
        
        session1_data = {
            "dataframes": {
                "df1": {"shape": [3, 2], "row_count": 3}
            },
            "operations": [
                {"operation_name": "merge", "execution_time": 1.0}
            ]
        }
        
        session2_data = {
            "dataframes": {
                "df1": {"shape": [5, 2], "row_count": 5}
            },
            "operations": [
                {"operation_name": "merge", "execution_time": 2.0}
            ]
        }
        
        with open(session1_file, 'w') as f:
            json.dump(session1_data, f)
        
        with open(session2_file, 'w') as f:
            json.dump(session2_data, f)
        
        result = runner.invoke(app, ["compare", session1_file, session2_file])
        
        assert result.exit_code == 0
        assert "session1" in result.stdout
        assert "session2" in result.stdout
    
    def test_check_command(self, runner, temp_dir):
        """Test check command."""
        # Create a session file with quality issues
        session_file = os.path.join(temp_dir, "session.json")
        session_data = {
            "dataframes": {
                "df1": {"shape": [3, 2], "row_count": 3}
            },
            "quality_issues": [
                {
                    "rule_name": "null_check",
                    "issue_type": "null_check",
                    "severity": "warning",
                    "description": "High null percentage"
                }
            ]
        }
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        
        result = runner.invoke(app, ["check", session_file])
        
        assert result.exit_code == 0
        assert "null_check" in result.stdout
        assert "warning" in result.stdout
    
    def test_init_command(self, runner, temp_dir):
        """Test init command."""
        result = runner.invoke(app, ["init", "--output", temp_dir])
        
        assert result.exit_code == 0
        assert "Initialized" in result.stdout
        
        # Check that files were created
        expected_files = [
            "auratrace_config.yaml",
            "quality_rules.yaml",
            "example_pipeline.py"
        ]
        
        for file_name in expected_files:
            file_path = os.path.join(temp_dir, file_name)
            assert os.path.exists(file_path)
    
    def test_init_command_default_output(self, runner):
        """Test init command with default output."""
        result = runner.invoke(app, ["init"])
        
        assert result.exit_code == 0
        assert "Initialized" in result.stdout
    
    def test_help_command(self, runner):
        """Test help command."""
        result = runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        assert "AuraTrace" in result.stdout
        assert "run" in result.stdout
        assert "view" in result.stdout
        assert "ask" in result.stdout
    
    def test_run_command_help(self, runner):
        """Test run command help."""
        result = runner.invoke(app, ["run", "--help"])
        
        assert result.exit_code == 0
        assert "script" in result.stdout
        assert "output" in result.stdout
    
    def test_view_command_help(self, runner):
        """Test view command help."""
        result = runner.invoke(app, ["view", "--help"])
        
        assert result.exit_code == 0
        assert "session" in result.stdout
    
    def test_ask_command_help(self, runner):
        """Test ask command help."""
        result = runner.invoke(app, ["ask", "--help"])
        
        assert result.exit_code == 0
        assert "session" in result.stdout
        assert "question" in result.stdout
    
    def test_compare_command_help(self, runner):
        """Test compare command help."""
        result = runner.invoke(app, ["compare", "--help"])
        
        assert result.exit_code == 0
        assert "session1" in result.stdout
        assert "session2" in result.stdout
    
    def test_check_command_help(self, runner):
        """Test check command help."""
        result = runner.invoke(app, ["check", "--help"])
        
        assert result.exit_code == 0
        assert "session" in result.stdout
    
    def test_init_command_help(self, runner):
        """Test init command help."""
        result = runner.invoke(app, ["init", "--help"])
        
        assert result.exit_code == 0
        assert "output" in result.stdout


class TestCLIWithRealData:
    """Test CLI with real data scenarios."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI runner for testing."""
        return CliRunner()
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield tmp_dir
    
    def test_complex_pipeline_execution(self, runner, temp_dir):
        """Test execution of a complex pipeline."""
        # Create a complex Python script
        script_path = os.path.join(temp_dir, "complex_pipeline.py")
        with open(script_path, 'w') as f:
            f.write("""
import pandas as pd
import numpy as np

# Load data
df1 = pd.DataFrame({
    'id': [1, 2, 3, 4, 5],
    'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
    'age': [25, 30, 35, 40, 45]
})

df2 = pd.DataFrame({
    'id': [1, 2, 3, 4, 5],
    'score': [85, 90, 75, 88, 92],
    'grade': ['A', 'A', 'C', 'B', 'A']
})

# Merge data
merged_df = df1.merge(df2, on='id')

# Group by grade
grouped = merged_df.groupby('grade').agg({
    'age': 'mean',
    'score': 'mean'
}).reset_index()

print("Pipeline completed successfully")
print(f"Final shape: {grouped.shape}")
""")
        
        result = runner.invoke(app, ["run", script_path, "--output", temp_dir])
        
        assert result.exit_code == 0
        assert "Pipeline completed successfully" in result.stdout
        assert "Final shape" in result.stdout
        
        # Check that output files were created
        output_files = [f for f in os.listdir(temp_dir) if f.endswith('.json')]
        assert len(output_files) > 0
    
    def test_quality_check_integration(self, runner, temp_dir):
        """Test quality check integration."""
        # Create a script with quality issues
        script_path = os.path.join(temp_dir, "quality_test.py")
        with open(script_path, 'w') as f:
            f.write("""
import pandas as pd

# Create data with quality issues
df = pd.DataFrame({
    'id': [1, 2, 1, 3, 2],  # Duplicates
    'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
    'age': [25, 30, None, 40, 45],  # Null values
    'email': ['alice@example.com', 'invalid-email', 'charlie@example.com', 'david@example.com', 'eve@example.com']
})

print("Data created with quality issues")
""")
        
        # Run the script
        result = runner.invoke(app, ["run", script_path, "--output", temp_dir])
        assert result.exit_code == 0
        
        # Find the session file
        session_files = [f for f in os.listdir(temp_dir) if f.endswith('.json')]
        assert len(session_files) > 0
        
        session_file = os.path.join(temp_dir, session_files[0])
        
        # Check quality
        result = runner.invoke(app, ["check", session_file])
        assert result.exit_code == 0
    
    def test_ai_analysis_integration(self, runner, temp_dir):
        """Test AI analysis integration."""
        # Create a simple script
        script_path = os.path.join(temp_dir, "ai_test.py")
        with open(script_path, 'w') as f:
            f.write("""
import pandas as pd

df = pd.DataFrame({
    'A': [1, 2, 3, 4, 5],
    'B': [10, 20, 30, 40, 50]
})

print("Data created for AI analysis")
""")
        
        # Run the script
        result = runner.invoke(app, ["run", script_path, "--output", temp_dir])
        assert result.exit_code == 0
        
        # Find the session file
        session_files = [f for f in os.listdir(temp_dir) if f.endswith('.json')]
        assert len(session_files) > 0
        
        session_file = os.path.join(temp_dir, session_files[0])
        
        # Mock AI assistant for ask command
        with patch('auratrace.cli.AIAssistant') as mock_assistant_class:
            mock_assistant = Mock()
            mock_assistant.ask_question.return_value = Mock(
                query="What is the data shape?",
                response="The dataframe has 5 rows and 2 columns.",
                timestamp=1234567890.0
            )
            mock_assistant.is_available.return_value = True
            mock_assistant_class.return_value = mock_assistant
            
            result = runner.invoke(app, ["ask", session_file, "What is the data shape?"])
            assert result.exit_code == 0
            assert "5 rows and 2 columns" in result.stdout


class TestCLIErrorHandling:
    """Test CLI error handling."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI runner for testing."""
        return CliRunner()
    
    def test_invalid_command(self, runner):
        """Test invalid command."""
        result = runner.invoke(app, ["invalid_command"])
        
        assert result.exit_code != 0
        assert "Error" in result.stdout or "No such command" in result.stdout
    
    def test_missing_arguments(self, runner):
        """Test missing arguments."""
        result = runner.invoke(app, ["run"])
        
        assert result.exit_code != 0
        assert "Error" in result.stdout or "Missing argument" in result.stdout
    
    def test_invalid_file_format(self, runner, temp_dir):
        """Test invalid file format."""
        # Create an invalid JSON file
        invalid_file = os.path.join(temp_dir, "invalid.json")
        with open(invalid_file, 'w') as f:
            f.write("invalid json content")
        
        result = runner.invoke(app, ["view", invalid_file])
        
        assert result.exit_code != 0
        assert "Error" in result.stdout
    
    def test_permission_error(self, runner):
        """Test permission error handling."""
        # Try to write to a protected directory
        result = runner.invoke(app, ["init", "--output", "/root/protected"])
        
        # Should handle gracefully
        assert result.exit_code != 0
        assert "Error" in result.stdout or "Permission" in result.stdout


class TestCLIOutputFormats:
    """Test CLI output formats."""
    
    @pytest.fixture
    def runner(self):
        """Create a CLI runner for testing."""
        return CliRunner()
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield tmp_dir
    
    def test_json_output_format(self, runner, temp_dir):
        """Test JSON output format."""
        # Create a session file
        session_file = os.path.join(temp_dir, "session.json")
        session_data = {
            "dataframes": {
                "df1": {"shape": [3, 2], "row_count": 3}
            }
        }
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        
        result = runner.invoke(app, ["view", session_file, "--format", "json"])
        
        assert result.exit_code == 0
        # Should be valid JSON
        json.loads(result.stdout)
    
    def test_csv_output_format(self, runner, temp_dir):
        """Test CSV output format."""
        # Create a session file
        session_file = os.path.join(temp_dir, "session.json")
        session_data = {
            "dataframes": {
                "df1": {"shape": [3, 2], "row_count": 3}
            }
        }
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        
        result = runner.invoke(app, ["view", session_file, "--format", "csv"])
        
        assert result.exit_code == 0
        assert "," in result.stdout  # Should contain CSV delimiters
    
    def test_table_output_format(self, runner, temp_dir):
        """Test table output format."""
        # Create a session file
        session_file = os.path.join(temp_dir, "session.json")
        session_data = {
            "dataframes": {
                "df1": {"shape": [3, 2], "row_count": 3}
            }
        }
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        
        result = runner.invoke(app, ["view", session_file, "--format", "table"])
        
        assert result.exit_code == 0
        assert "df1" in result.stdout 