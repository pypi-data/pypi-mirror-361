"""
AI-powered assistant for providing intelligent insights and root cause analysis.
"""

import json
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
import os
from .llm_provider import (
    LLMProvider, OpenAIProvider, HuggingFaceProvider, CustomAPIProvider, LocalModelProvider, UserSuppliedProvider
)

@dataclass
class AIAnalysis:
    """Result of an AI analysis."""
    
    query: str
    response: str
    confidence: float
    analysis_type: str
    metadata: Dict[str, Any]
    timestamp: float

class AIAssistant:
    """
    AI-powered assistant for providing intelligent insights.
    Now supports pluggable LLM providers (OpenAI, Hugging Face, custom, local, user-supplied).
    """
    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        custom_generate_fn: Optional[Callable[[str], str]] = None,
        **kwargs
    ):
        """
        Initialize the AI assistant.
        Args:
            provider: Which LLM provider to use ('openai', 'huggingface', 'custom', 'local', 'user').
            model: Model name or path.
            api_key: API key for provider (if needed).
            custom_generate_fn: User-supplied function for LLM (if provider='user').
            kwargs: Extra config for provider.
        """
        self.provider_name = provider or os.getenv("AURATRACE_LLM_PROVIDER", "huggingface")
        self.model = model or os.getenv("AURATRACE_LLM_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")
        self.api_key = api_key or os.getenv("AURATRACE_LLM_API_KEY")
        self.kwargs = kwargs
        self.llm_provider = self._init_provider(custom_generate_fn)

    def _init_provider(self, custom_generate_fn=None):
        if self.provider_name == "openai":
            return OpenAIProvider(model=self.model, api_key=self.api_key, **self.kwargs)
        elif self.provider_name == "huggingface":
            return HuggingFaceProvider(model=self.model, api_key=self.api_key, **self.kwargs)
        elif self.provider_name == "custom":
            return CustomAPIProvider(model=self.model, api_key=self.api_key, **self.kwargs)
        elif self.provider_name == "local":
            return LocalModelProvider(model=self.model, **self.kwargs)
        elif self.provider_name == "user" and custom_generate_fn:
            return UserSuppliedProvider(generate_fn=custom_generate_fn, model=self.model, **self.kwargs)
        else:
            # Default to Hugging Face
            return HuggingFaceProvider(model=self.model, api_key=self.api_key, **self.kwargs)

    def _ensure_ready(self):
        if not self.llm_provider.is_available() or not self.llm_provider.ensure_ready():
            print("\n[AuraTrace] The selected LLM provider is not ready.")
            print(self.llm_provider.info())
            print("\nTo use AI features, you may need to install dependencies, download a model, or provide an API key.")
            print("Provider: ", self.provider_name)
            print("Model: ", self.model)
            if self.provider_name in ("huggingface", "local"):
                print("You can change the model by setting the 'model' argument or the AURATRACE_LLM_MODEL env var.")
            if self.provider_name in ("openai", "claude", "gemini"):
                print("You can set your API key via the 'api_key' argument or the AURATRACE_LLM_API_KEY env var.")
            # Prompt user for permission to proceed
            try:
                resp = input("\nWould you like to install missing dependencies or provide an API key now? [y/N]: ").strip().lower()
            except Exception:
                resp = "n"
            if resp == "y":
                print("\nPlease follow the instructions above, then re-run your command.")
            else:
                print("\nAborting AI operation. No model or API key provided.")
            return False
        return True

    def analyze_lineage(self, lineage_data: Dict[str, Any], question: str) -> AIAnalysis:
        if not self._ensure_ready():
            return AIAnalysis(
                query=question,
                response="AI analysis not available. Please install dependencies, download a model, or provide an API key.",
                confidence=0.0,
                analysis_type="error",
                metadata={},
                timestamp=time.time()
            )
        try:
            context = self._prepare_lineage_context(lineage_data)
            prompt = f"Context:\n{context}\n\nQuestion: {question}"
            response = self.llm_provider.generate(prompt)
            return AIAnalysis(
                query=question,
                response=response,
                confidence=0.8,
                analysis_type="lineage_analysis",
                metadata={"context_length": len(context)},
                timestamp=time.time()
            )
        except Exception as e:
            return AIAnalysis(
                query=question,
                response=f"Error during analysis: {str(e)}",
                confidence=0.0,
                analysis_type="error",
                metadata={"error": str(e)},
                timestamp=time.time()
            )

    def analyze_quality_issues(self, issues: List[Dict[str, Any]], lineage_data: Dict[str, Any]) -> AIAnalysis:
        if not self._ensure_ready():
            return AIAnalysis(
                query="Analyze quality issues",
                response="AI analysis not available. Please install dependencies, download a model, or provide an API key.",
                confidence=0.0,
                analysis_type="error",
                metadata={},
                timestamp=time.time()
            )
        try:
            context = self._prepare_quality_context(issues, lineage_data)
            prompt = f"Context:\n{context}\n\nPlease analyze these quality issues and provide root cause analysis."
            response = self.llm_provider.generate(prompt)
            return AIAnalysis(
                query="Analyze quality issues",
                response=response,
                confidence=0.8,
                analysis_type="quality_analysis",
                metadata={"issue_count": len(issues)},
                timestamp=time.time()
            )
        except Exception as e:
            return AIAnalysis(
                query="Analyze quality issues",
                response=f"Error during analysis: {str(e)}",
                confidence=0.0,
                analysis_type="error",
                metadata={"error": str(e)},
                timestamp=time.time()
            )

    def suggest_optimizations(self, performance_data: Dict[str, Any]) -> AIAnalysis:
        if not self._ensure_ready():
            return AIAnalysis(
                query="Suggest optimizations",
                response="AI analysis not available. Please install dependencies, download a model, or provide an API key.",
                confidence=0.0,
                analysis_type="error",
                metadata={},
                timestamp=time.time()
            )
        try:
            context = self._prepare_performance_context(performance_data)
            prompt = f"Context:\n{context}\n\nPlease suggest optimizations for this data pipeline."
            response = self.llm_provider.generate(prompt)
            return AIAnalysis(
                query="Suggest optimizations",
                response=response,
                confidence=0.8,
                analysis_type="optimization_suggestions",
                metadata={"bottleneck_count": len(performance_data.get('bottlenecks', []))},
                timestamp=time.time()
            )
        except Exception as e:
            return AIAnalysis(
                query="Suggest optimizations",
                response=f"Error during analysis: {str(e)}",
                confidence=0.0,
                analysis_type="error",
                metadata={"error": str(e)},
                timestamp=time.time()
            )
    
    def _prepare_lineage_context(self, lineage_data: Dict[str, Any]) -> str:
        """Prepare lineage data for AI analysis."""
        context_parts = []
        
        if 'operations' in lineage_data:
            ops = lineage_data['operations']
            context_parts.append(f"Operations ({len(ops)}):")
            for op in ops[:10]:  # Limit to first 10 operations
                context_parts.append(f"- {op.get('operation_name', 'unknown')}: {op.get('execution_time', 0):.2f}s")
        
        if 'dataframes' in lineage_data:
            dfs = lineage_data['dataframes']
            context_parts.append(f"\nDataFrames ({len(dfs)}):")
            for df_id, df_info in list(dfs.items())[:5]:  # Limit to first 5 dataframes
                shape = df_info.get('schema', {}).get('shape', (0, 0))
                context_parts.append(f"- {df_id[:8]}: {shape[0]} rows, {shape[1]} columns")
        
        if 'summary' in lineage_data:
            summary = lineage_data['summary']
            context_parts.append(f"\nSummary:")
            context_parts.append(f"- Total operations: {summary.get('total_operations', 0)}")
            context_parts.append(f"- Total execution time: {summary.get('total_execution_time', 0):.2f}s")
            context_parts.append(f"- Memory delta: {summary.get('total_memory_delta', 0)} bytes")
        
        return "\n".join(context_parts)
    
    def _prepare_quality_context(self, issues: List[Dict[str, Any]], 
                               lineage_data: Dict[str, Any]) -> str:
        """Prepare quality issues for AI analysis."""
        context_parts = []
        
        context_parts.append(f"Quality Issues ({len(issues)}):")
        for issue in issues[:5]:  # Limit to first 5 issues
            context_parts.append(f"- {issue.get('issue_type', 'unknown')}: {issue.get('description', 'No description')}")
            context_parts.append(f"  Severity: {issue.get('severity', 'unknown')}")
            context_parts.append(f"  Affected rows: {issue.get('affected_rows', 0)}")
        
        # Add lineage context if available
        if lineage_data:
            context_parts.append("\nLineage Context:")
            context_parts.append(self._prepare_lineage_context(lineage_data))
        
        return "\n".join(context_parts)
    
    def _prepare_performance_context(self, performance_data: Dict[str, Any]) -> str:
        """Prepare performance data for AI analysis."""
        context_parts = []
        
        summary = performance_data.get('summary', {})
        context_parts.append("Performance Summary:")
        context_parts.append(f"- Total operations: {summary.get('total_operations', 0)}")
        context_parts.append(f"- Total execution time: {summary.get('total_execution_time', '0s')}")
        context_parts.append(f"- Total memory delta: {summary.get('total_memory_delta', '0B')}")
        context_parts.append(f"- Average execution time: {summary.get('average_execution_time', '0s')}")
        
        bottlenecks = performance_data.get('bottlenecks', [])
        if bottlenecks:
            context_parts.append(f"\nBottlenecks ({len(bottlenecks)}):")
            for bottleneck in bottlenecks[:5]:  # Limit to first 5 bottlenecks
                context_parts.append(f"- {bottleneck.get('operation_name', 'unknown')}: {bottleneck.get('execution_time', '0s')}")
        
        return "\n".join(context_parts)
    
    def _get_lineage_system_prompt(self) -> str:
        """Get system prompt for lineage analysis."""
        return """You are an expert data engineer analyzing data lineage and pipeline execution. 
Your task is to help users understand their data transformations and answer questions about their pipeline.

When analyzing lineage data:
1. Focus on the relationships between operations and dataframes
2. Identify patterns in the data flow
3. Explain the impact of operations on data shape and content
4. Provide insights about potential optimizations
5. Be concise but thorough in your explanations

Use the provided context to answer questions accurately and helpfully."""
    
    def _get_quality_system_prompt(self) -> str:
        """Get system prompt for quality analysis."""
        return """You are an expert data quality analyst. Your task is to analyze data quality issues 
and provide root cause analysis.

When analyzing quality issues:
1. Identify the most likely causes of each issue
2. Consider the data lineage and transformation history
3. Suggest specific fixes or improvements
4. Prioritize issues by severity and impact
5. Provide actionable recommendations

Focus on practical solutions that can be implemented immediately."""
    
    def _get_optimization_system_prompt(self) -> str:
        """Get system prompt for optimization suggestions."""
        return """You are an expert data pipeline optimization specialist. Your task is to analyze 
performance data and suggest optimizations.

When suggesting optimizations:
1. Focus on the biggest performance bottlenecks first
2. Consider both execution time and memory usage
3. Suggest specific code changes or configuration improvements
4. Consider the trade-offs between different optimization strategies
5. Provide practical, implementable recommendations

Be specific about what changes to make and why they will help."""
    
    def is_available(self) -> bool:
        """Check if AI analysis is available."""
        return self.llm_provider.is_available()
    
    def get_capabilities(self) -> List[str]:
        """Get list of available AI capabilities."""
        if not self.llm_provider.is_available():
            return []
        
        return [
            "lineage_analysis",
            "quality_analysis", 
            "optimization_suggestions",
            "root_cause_analysis"
        ] 