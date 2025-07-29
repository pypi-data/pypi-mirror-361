"""
AuraTrace - AI-Powered Data Lineage & Observability for Python

AuraTrace is a next-generation, lightweight, and intelligent Python package
engineered to bring complete transparency to data pipelines.
"""

__version__ = "0.1.0"
__author__ = "Rishi Tiwari"
__email__ = "wizard.enterprises.07@gmail.com"

from .core.tracer import Tracer
from .core.profiler import DataProfiler
from .core.lineage import LineageEngine
from .core.quality import QualityEngine
from .core.performance import PerformanceEngine
from .ai.assistant import AIAssistant
from .cli import app

__all__ = [
    "Tracer",
    "DataProfiler", 
    "LineageEngine",
    "QualityEngine",
    "PerformanceEngine",
    "AIAssistant",
    "app",
] 