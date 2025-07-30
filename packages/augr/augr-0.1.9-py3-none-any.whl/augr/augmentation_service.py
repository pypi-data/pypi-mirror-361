"""
Service for LLM-based dataset augmentation with iterative refinement capabilities.
"""

import json
from typing import List, Dict, Any

from .ai_client import create_ai
from .braintrust_client import BraintrustClient
from .models import (
    CaseAbstract,
    CaseAbstractList,
    DatasetSample,
    GapAnalysisResult,
    GapAnalysisSuggestion,
    GeneratedSample,
    InferredSchema,
)

# Constants
DEFAULT_MODEL = "claude-4-sonnet"


class DatasetAugmentationService:
    """Main service for dataset augmentation with enhanced iterative capabilities"""

    def __init__(self, braintrust_api_key: str):
        self.braintrust_client = BraintrustClient(braintrust_api_key)
        self.ai = create_ai(
            model=DEFAULT_MODEL,
            temperature=0.0,
            braintrust_api_key=braintrust_api_key
        )

    async def analyze_dataset_gaps(self, samples: List[DatasetSample], dataset_metadata: Dict[str, Any] = None) -> GapAnalysisResult:
        """Analyze dataset samples and identify gaps (legacy method for backward compatibility)"""

        # Prepare sample data for analysis
        sample_data = []
        for i, sample in enumerate(samples[:10]):  # Show first 10 for context
            sample_data.append({
                "sample_index": i + 1,
                "input": sample.input,
                "expected": sample.expected,
                "metadata": sample.metadata
            })

        # Format dataset metadata for AI context
        dataset_context = ""
        if dataset_metadata:
            dataset_context = f"""
            <DatasetMetadata description="The dataset metadata">
            {json.dumps(dataset_metadata, indent=2)}
            </DatasetMetadata>
            """

        prompt = f"""You are an expert AI trainer analyzing a dataset to identify gaps in test coverage.

        {dataset_context}

        DATASET SAMPLES TO ANALYZE:
        {json.dumps(sample_data, indent=2)}

        TOTAL SAMPLES IN DATASET: {len(samples)}

        Your task is to identify exactly 5 high-level gaps in test coverage that would be valuable to fill with synthetic data.

        Consider:
        1. Edge cases that aren't covered
        2. Error conditions that might not be tested
        3. Boundary conditions
        4. Different input formats/structures not represented
        5. Logical variations in processing paths

        Focus on gaps that would genuinely improve the robustness and coverage of this dataset.

        You must respond with exactly 5 suggestions. Each suggestion should be:
        - Actionable (can generate a concrete test case)
        - Different from existing samples
        - Valuable for improving dataset coverage
        - Feasible to implement synthetically

        Return your analysis as JSON matching this exact structure:
        {{
            "suggestions": [
                {{
                    "title": "Short descriptive title",
                    "description": "Detailed description of what this gap covers",
                    "rationale": "Why this gap is important to fill"
                }}
            ],
            "overall_assessment": "Brief assessment of current dataset coverage and main gaps"
        }}
        """

        try:
            response = await self.ai.gen_obj(
                schema=GapAnalysisResult,
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )

            return response
        except Exception as e:
            raise Exception(f"Failed to analyze dataset gaps: {str(e)}")

    async def generate_case_abstracts_with_guidance(
        self,
        samples: List[DatasetSample],
        user_guidance: str,
        previous_feedback: str = "",
        dataset_metadata: Dict[str, Any] = None
    ) -> CaseAbstractList:
        """Generate case abstracts based on user guidance and optional feedback"""

        # Prepare sample data for analysis
        sample_data = []
        for i, sample in enumerate(samples[:10]):  # Show first 10 for context
            sample_data.append({
                "sample_index": i + 1,
                "input": sample.input,
                "expected": sample.expected,
                "metadata": sample.metadata
            })

        # Format dataset metadata for AI context
        dataset_context = ""
        if dataset_metadata:
            dataset_context = f"""
            <DatasetMetadata description="The dataset metadata">
            {json.dumps(dataset_metadata, indent=2)}
            </DatasetMetadata>
            """

        feedback_section = ""
        if previous_feedback:
            feedback_section = f"""
PREVIOUS FEEDBACK FROM USER:
{previous_feedback}

Please incorporate this feedback into your new suggestions.
"""

        prompt = f"""You are an expert AI trainer helping to generate test case abstracts for dataset augmentation.

{dataset_context}

DATASET SAMPLES FOR CONTEXT:
{json.dumps(sample_data, indent=2)}

TOTAL SAMPLES IN DATASET: {len(samples)}

USER GUIDANCE ON DESIRED TEST CASES:
{user_guidance}

{feedback_section}

Your task is to generate 5-10 high-level case abstracts that match the user's guidance. Each abstract should describe what kind of test case to generate without actually generating the full input/expected data yet.

Consider:
- The user's specific guidance and requirements
- The existing dataset structure and patterns
- How to create diverse, valuable test cases
- Edge cases and variations within the user's requested domain

Each abstract should be:
- Specific enough to guide sample generation
- Aligned with the user's guidance
- Different from existing dataset samples
- Technically feasible given the dataset structure

Return your response as JSON matching this exact structure:
{{
    "abstracts": [
        {{
            "title": "Short descriptive title",
            "description": "Detailed description of the test case scenario",
            "expected_input_characteristics": "What the input should look like",
            "expected_output_characteristics": "What the expected output should look like"
        }}
    ],
    "generation_notes": "Notes about the generation process and any assumptions made"
}}"""

        try:
            response = await self.ai.gen_obj(
                schema=CaseAbstractList,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return response
        except Exception as e:
            raise Exception(f"Failed to generate case abstracts: {str(e)}")

    async def infer_dataset_schema(self, reference_samples: List[DatasetSample], dataset_metadata: Dict[str, Any] = None) -> InferredSchema:
        """Analyze dataset samples and infer precise JSON Schema for each field (Phase 1)"""

        # Prepare sample data for analysis
        sample_data = []
        for i, sample in enumerate(reference_samples[:20]):  # Analyze up to 20 samples for schema
            sample_data.append({
                "sample_index": i + 1,
                "input": sample.input,
                "expected": sample.expected,
                "metadata": sample.metadata
            })

        # Format dataset metadata for AI context
        dataset_context = ""
        if dataset_metadata:
            dataset_context = f"""
            <DatasetMetadata description="The dataset metadata">
            {json.dumps(dataset_metadata, indent=2)}
            </DatasetMetadata>
            """

        prompt = f"""You are a JSON Schema expert. Analyze these dataset samples and create precise JSON Schema objects for the input, expected, and metadata fields.

{dataset_context}

CRITICAL RULES:
1. Document ONLY what you observe - no guessing or extrapolation
2. If a field is null in one sample and has a value in another, use "anyOf": [null, <actual_type>]
3. If you see only one example of an object like {{"name": "cool"}}, document exactly one property "name" of type string
4. Use "required" only for fields that appear in ALL samples
5. Generate actual JSON Schema objects, not prose descriptions

DATASET SAMPLES:
{json.dumps(sample_data, indent=2)}

Return precise JSON Schema analysis as:
{{
    "input_schema": {{ /* Valid JSON Schema object for input field */ }},
    "expected_schema": {{ /* Valid JSON Schema object for expected field */ }},
    "metadata_schema": {{ /* Valid JSON Schema object for metadata field */ }},
    "observed_patterns": ["Pattern 1", "Pattern 2"],
    "field_relationships": ["Relationship 1", "Relationship 2"]
}}

Remember: Be ruthlessly precise. Only document what you actually see in the data."""

        try:
            response = await self.ai.gen_obj(
                schema=InferredSchema,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return response
        except Exception as e:
            raise Exception(f"Failed to infer dataset schema: {str(e)}")

    async def generate_sample_for_case_abstract(
        self,
        case_abstract: CaseAbstract,
        reference_samples: List[DatasetSample],
        schema: InferredSchema,
        dataset_metadata: Dict[str, Any] = None
    ) -> GeneratedSample:
        """Generate a specific sample based on a case abstract using documented schema (Phase 2)"""

        # Show a few reference samples for context
        reference_context = []
        for i, sample in enumerate(reference_samples[:5]):
            reference_context.append({
                "sample_index": i + 1,
                "input": sample.input,
                "expected": sample.expected,
                "metadata": sample.metadata
            })

        # Format dataset metadata for AI context
        dataset_context = ""
        if dataset_metadata:
            dataset_context = f"""
            <DatasetMetadata description="The dataset metadata">
            {json.dumps(dataset_metadata, indent=2)}
            </DatasetMetadata>
            """

        prompt = f"""You are generating a dataset sample that must EXACTLY match the documented JSON Schema.

        {dataset_context}

        CASE ABSTRACT TO IMPLEMENT:
        Title: {case_abstract.title}
        Description: {case_abstract.description}
        Expected Input: {case_abstract.expected_input_characteristics}
        Expected Output: {case_abstract.expected_output_characteristics}

        REFERENCE SAMPLES FOR CONTEXT:
        {json.dumps(reference_context, indent=2)}

        DOCUMENTED JSON SCHEMAS (MUST FOLLOW EXACTLY):
        Input Schema: {json.dumps(schema.input_schema)}
        Expected Schema: {json.dumps(schema.expected_schema)}
        Metadata Schema: {json.dumps(schema.metadata_schema)}

        OBSERVED PATTERNS: {schema.observed_patterns}
        FIELD RELATIONSHIPS: {schema.field_relationships}

        Generate ONE sample that:
        1. Implements the case abstract scenario
        2. EXACTLY matches all three JSON schemas
        3. Includes a test_name in metadata (REQUIRED)
        4. Creates realistic, coherent input/expected data

        Validate your response against the schemas before returning.

        Return as JSON:
        {{
            "input": /* Must match input_schema exactly */,
            "expected": /* Must match expected_schema exactly */,
            "metadata": {{ /* Must match metadata_schema exactly and include test_name */ }}
        }}
        """

        try:
            response = await self.ai.gen_obj(
                schema=GeneratedSample,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            generated_sample = response

            # Ensure test_name is present in metadata
            if "test_name" not in generated_sample.metadata:
                generated_sample.metadata["test_name"] = case_abstract.title.lower().replace(" ", "_")

            return generated_sample
        except Exception as e:
            raise Exception(f"Failed to generate sample for '{case_abstract.title}': {str(e)}")

    async def generate_sample_variation(
        self,
        original_sample: GeneratedSample,
        case_abstract: CaseAbstract,
        variation_request: str,
        schema: InferredSchema,
        dataset_metadata: Dict[str, Any] = None
    ) -> GeneratedSample:
        """Generate a variation of an existing sample based on user request"""

        # Format dataset metadata for AI context
        dataset_context = ""
        if dataset_metadata:
            dataset_context = f"""
            <DatasetMetadata description="The dataset metadata">
            {json.dumps(dataset_metadata, indent=2)}
            </DatasetMetadata>
            """

        prompt = f"""You are generating a variation of an existing dataset sample.

        {dataset_context}

        ORIGINAL SAMPLE:
        Input: {json.dumps(original_sample.input)}
        Expected: {json.dumps(original_sample.expected)}
        Metadata: {json.dumps(original_sample.metadata)}

        ORIGINAL CASE ABSTRACT:
        {case_abstract.description}

        USER'S VARIATION REQUEST:
        {variation_request}

        DOCUMENTED JSON SCHEMAS (MUST FOLLOW EXACTLY):
        Input Schema: {json.dumps(schema.input_schema)}
        Expected Schema: {json.dumps(schema.expected_schema)}
        Metadata Schema: {json.dumps(schema.metadata_schema)}

        Generate a VARIED sample that:
        1. Addresses the user's variation request
        2. EXACTLY matches all three JSON schemas
        3. Maintains the core concept from the case abstract
        4. Creates realistic, coherent input/expected data
        5. Includes test_name in metadata

        Return as JSON:
        {{
            "input": /* Must match input_schema exactly */,
            "expected": /* Must match expected_schema exactly */,
            "metadata": {{ /* Must match metadata_schema exactly and include test_name */ }}
        }}
        """

        try:
            response = await self.ai.gen_obj(
                schema=GeneratedSample,
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )

            generated_sample = response

            # Ensure test_name is present in metadata
            if "test_name" not in generated_sample.metadata:
                base_name = original_sample.metadata.get("test_name", "variation")
                generated_sample.metadata["test_name"] = f"{base_name}_variation"

            return generated_sample
        except Exception as e:
            raise Exception(f"Failed to generate sample variation: {str(e)}")

    # Legacy method for backward compatibility
    async def generate_sample_for_suggestion(
        self,
        suggestion: GapAnalysisSuggestion,
        reference_samples: List[DatasetSample],
        schema: InferredSchema,
        dataset_metadata: Dict[str, Any] = None
    ) -> GeneratedSample:
        """Legacy method - convert suggestion to case abstract and generate"""
        case_abstract = CaseAbstract(
            title=suggestion.title,
            description=suggestion.description,
            expected_input_characteristics="Based on existing dataset patterns",
            expected_output_characteristics="Based on existing dataset patterns"
        )
        return await self.generate_sample_for_case_abstract(case_abstract, reference_samples, schema, dataset_metadata)
