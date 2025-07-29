"""
Tests for the AuraTrace AI assistant module.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import json
import os

from auratrace.ai.assistant import AIAssistant, AIAnalysis


class TestAIAssistant:
    """Test cases for the AIAssistant class."""
    
    def test_ai_assistant_initialization(self):
        """Test AI assistant initialization with default (Hugging Face)."""
        assistant = AIAssistant()
        assert assistant.provider_name == "huggingface"
        assert assistant.model == "mistralai/Mistral-7B-Instruct-v0.2"

    def test_ai_assistant_openai(self):
        """Test AI assistant initialization with OpenAI provider and API key."""
        assistant = AIAssistant(provider="openai", api_key="sk-test", model="gpt-3.5-turbo")
        assert assistant.provider_name == "openai"
        assert assistant.api_key == "sk-test"
        assert assistant.model == "gpt-3.5-turbo"

    def test_ai_assistant_huggingface(self):
        """Test AI assistant initialization with Hugging Face provider and custom model."""
        assistant = AIAssistant(provider="huggingface", model="distilbert-base-uncased")
        assert assistant.provider_name == "huggingface"
        assert assistant.model == "distilbert-base-uncased"

    def test_ai_assistant_custom_api(self):
        """Test AI assistant initialization with custom API provider."""
        assistant = AIAssistant(provider="custom", model="my-model", api_key="api-key", endpoint="http://localhost:8000/llm")
        assert assistant.provider_name == "custom"
        assert assistant.model == "my-model"
        assert assistant.api_key == "api-key"
        assert assistant.llm_provider.kwargs["endpoint"] == "http://localhost:8000/llm"

    def test_ai_assistant_user_supplied(self):
        """Test AI assistant initialization with user-supplied function."""
        def dummy_llm(prompt):
            return "dummy response"
        assistant = AIAssistant(provider="user", custom_generate_fn=dummy_llm)
        assert assistant.provider_name == "user"
        assert callable(assistant.llm_provider.generate_fn)

    def test_ai_assistant_not_ready(self, monkeypatch):
        """Test AI assistant not ready (missing dependency or model)."""
        class DummyProvider:
            def is_available(self): return False
            def ensure_ready(self): return False
            def info(self): return "Dummy info"
        monkeypatch.setattr("auratrace.ai.assistant.AIAssistant._init_provider", lambda self, _: DummyProvider())
        assistant = AIAssistant()
        assert not assistant.is_available()

    def test_analyze_lineage(self):
        """Test lineage analysis."""
        assistant = AIAssistant()
        
        # Mock the LLM provider
        mock_provider = Mock()
        mock_provider.is_available.return_value = True
        mock_provider.ensure_ready.return_value = True
        mock_provider.generate.return_value = "Analysis result"
        assistant.llm_provider = mock_provider
        
        lineage_data = {
            'operations': [
                {'operation_name': 'merge', 'execution_time': 1.5}
            ],
            'dataframes': {
                'df1': {'shape': (100, 5), 'memory_usage': 1024}
            }
        }
        
        result = assistant.analyze_lineage(lineage_data, "What happened?")
        
        assert isinstance(result, AIAnalysis)
        assert result.query == "What happened?"
        assert result.response == "Analysis result"
        assert result.analysis_type == "lineage_analysis"

    def test_analyze_quality_issues(self):
        """Test quality issues analysis."""
        assistant = AIAssistant()
        
        # Mock the LLM provider
        mock_provider = Mock()
        mock_provider.is_available.return_value = True
        mock_provider.ensure_ready.return_value = True
        mock_provider.generate.return_value = "Quality analysis"
        assistant.llm_provider = mock_provider
        
        issues = [
            {'rule_name': 'null_check', 'severity': 'warning'}
        ]
        lineage_data = {'operations': []}
        
        result = assistant.analyze_quality_issues(issues, lineage_data)
        
        assert isinstance(result, AIAnalysis)
        assert result.analysis_type == "quality_analysis"
        assert result.response == "Quality analysis"

    def test_suggest_optimizations(self):
        """Test optimization suggestions."""
        assistant = AIAssistant()
        
        # Mock the LLM provider
        mock_provider = Mock()
        mock_provider.is_available.return_value = True
        mock_provider.ensure_ready.return_value = True
        mock_provider.generate.return_value = "Optimization suggestions"
        assistant.llm_provider = mock_provider
        
        performance_data = {
            'bottlenecks': [
                {'operation': 'merge', 'time': 10.5}
            ]
        }
        
        result = assistant.suggest_optimizations(performance_data)
        
        assert isinstance(result, AIAnalysis)
        assert result.analysis_type == "optimization_suggestions"
        assert result.response == "Optimization suggestions"

    def test_ai_assistant_not_available(self):
        """Test AI assistant when provider is not available."""
        assistant = AIAssistant()
        
        # Mock the LLM provider to be unavailable
        mock_provider = Mock()
        mock_provider.is_available.return_value = False
        mock_provider.ensure_ready.return_value = False
        mock_provider.info.return_value = "Provider not available"
        assistant.llm_provider = mock_provider
        
        # Mock input to return 'n' (no)
        with patch('builtins.input', return_value='n'):
            result = assistant.analyze_lineage({}, "Test question")
        
        assert isinstance(result, AIAnalysis)
        assert result.analysis_type == "error"
        assert "not available" in result.response.lower()

    def test_get_capabilities(self):
        """Test getting AI assistant capabilities."""
        assistant = AIAssistant()
        capabilities = assistant.get_capabilities()
        
        assert isinstance(capabilities, list)
        assert len(capabilities) > 0


class TestAIAnalysis:
    """Test cases for the AIAnalysis class."""
    
    def test_ai_analysis_creation(self):
        """Test AIAnalysis creation."""
        analysis = AIAnalysis(
            query="Test question",
            response="Test response",
            confidence=0.8,
            analysis_type="test",
            metadata={"key": "value"},
            timestamp=1234567890.0
        )
        
        assert analysis.query == "Test question"
        assert analysis.response == "Test response"
        assert analysis.confidence == 0.8
        assert analysis.analysis_type == "test"
        assert analysis.metadata == {"key": "value"}
        assert analysis.timestamp == 1234567890.0


@pytest.fixture
def ai_assistant():
    """Fixture for AI assistant with mocked provider."""
    assistant = AIAssistant()
    
    # Mock the LLM provider
    mock_provider = Mock()
    mock_provider.is_available.return_value = True
    mock_provider.ensure_ready.return_value = True
    mock_provider.generate.return_value = "Mock response"
    assistant.llm_provider = mock_provider
    
    return assistant


@pytest.fixture
def sample_dataframe():
    """Fixture for sample dataframe."""
    return pd.DataFrame({
        'A': [1, 2, 3],
        'B': ['a', 'b', 'c'],
        'C': [1.1, 2.2, 3.3]
    })


@pytest.fixture
def sample_operations():
    """Fixture for sample operations."""
    return [
        {
            'operation_id': 'op1',
            'operation_name': 'merge',
            'execution_time': 1.5,
            'memory_delta': 500
        },
        {
            'operation_id': 'op2',
            'operation_name': 'filter',
            'execution_time': 0.5,
            'memory_delta': -200
        }
    ]


@pytest.fixture
def sample_issues():
    """Fixture for sample quality issues."""
    return [
        {
            'rule_name': 'null_check',
            'issue_type': 'null_check',
            'severity': 'warning',
            'affected_rows': 10
        },
        {
            'rule_name': 'duplicate_check',
            'issue_type': 'duplicate_check',
            'severity': 'error',
            'affected_rows': 5
        }
    ]


class TestAIAssistantIntegration:
    """Integration tests for AI assistant."""
    
    def test_comprehensive_ai_analysis(self, ai_assistant, sample_dataframe, sample_operations, sample_issues):
        """Test comprehensive AI analysis workflow."""
        # Test lineage analysis
        lineage_data = {
            'operations': sample_operations,
            'dataframes': {'df1': {'shape': sample_dataframe.shape}}
        }
        
        lineage_result = ai_assistant.analyze_lineage(lineage_data, "What happened in this pipeline?")
        assert isinstance(lineage_result, AIAnalysis)
        assert lineage_result.analysis_type == "lineage_analysis"
        
        # Test quality analysis
        quality_result = ai_assistant.analyze_quality_issues(sample_issues, lineage_data)
        assert isinstance(quality_result, AIAnalysis)
        assert quality_result.analysis_type == "quality_analysis"
        
        # Test optimization suggestions
        performance_data = {
            'bottlenecks': [
                {'operation': 'merge', 'time': 10.5}
            ]
        }
        
        optimization_result = ai_assistant.suggest_optimizations(performance_data)
        assert isinstance(optimization_result, AIAnalysis)
        assert optimization_result.analysis_type == "optimization_suggestions"
    
    def test_ai_assistant_error_handling(self, ai_assistant):
        """Test AI assistant error handling."""
        # Mock provider to raise exception
        ai_assistant.llm_provider.generate.side_effect = Exception("Test error")
        
        result = ai_assistant.analyze_lineage({}, "Test question")
        
        assert isinstance(result, AIAnalysis)
        assert result.analysis_type == "error"
        assert "Error during analysis" in result.response
    
    def test_ai_assistant_capabilities(self, ai_assistant):
        """Test AI assistant capabilities."""
        capabilities = ai_assistant.get_capabilities()
        
        assert isinstance(capabilities, list)
        assert "lineage_analysis" in capabilities
        assert "quality_analysis" in capabilities
        assert "optimization_suggestions" in capabilities 