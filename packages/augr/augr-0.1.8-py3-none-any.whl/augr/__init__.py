"""
Dataset augmentation package for Braintrust datasets.

This package provides tools for intelligently augmenting Braintrust datasets
with synthetic data using LLM analysis and generation.

Main modules:
- cli: Enhanced CLI interface with iterative workflows
- models: Pydantic models for data structures
- braintrust_client: Braintrust API client
- augmentation_service: LLM-based augmentation service
- dataset_helper: Main entry point (backward compatible)
"""

from .augmentation_service import DatasetAugmentationService
from .braintrust_client import BraintrustClient
from .cli import DatasetAugmentationCLI
from .models import (
    CaseAbstract,
    CaseAbstractList,
    DatasetSample,
    GapAnalysisResult,
    GapAnalysisSuggestion,
    GeneratedSample,
    InferredSchema,
)

__all__ = [
    'DatasetSample',
    'GapAnalysisSuggestion',
    'GapAnalysisResult',
    'InferredSchema',
    'GeneratedSample',
    'CaseAbstract',
    'CaseAbstractList',
    'BraintrustClient',
    'DatasetAugmentationService',
    'DatasetAugmentationCLI'
]
