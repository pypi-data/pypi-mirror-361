# dataset_helper.py
# Author: Luke Bechtel (@Marviel)
# Summary: This file will help pull datasets from braintrust and augment them with more synthetic data.
#
# This is the main entry point that uses the new modular structure.
# For the enhanced CLI with iterative workflows, run: python -m cli
# For legacy compatibility, this file maintains the original interface.

import asyncio
import json
import os

from dotenv import load_dotenv

from .augmentation_service import DatasetAugmentationService
from .cli import DatasetAugmentationCLI

# Import from the new modular structure

load_dotenv()

# Interactive CLI components
try:
    import inquirer
except ImportError:
    print("Please install inquirer: pip install inquirer")
    exit(1)

# Constants for backward compatibility
DEFAULT_MODEL = "claude-4-sonnet"


async def main():
    """
    Main CLI application - now uses the enhanced CLI interface
    
    This provides the new interactive workflows:
    - Mode 1: Guided dataset augmentation with iterative refinement
    - Mode 2: Direct JSON file upload
    """

    cli = DatasetAugmentationCLI()
    await cli.run()


# Legacy function for backward compatibility
async def legacy_workflow():
    """
    Legacy workflow for backward compatibility
    (Original simple workflow without the new features)
    """
    print("🧠 Dataset Augmentation CLI Tool (Legacy Mode)")
    print("=" * 50)

    # Get API key
    braintrust_api_key = os.getenv("BRAINTRUST_API_KEY")

    if not braintrust_api_key:
        print("❌ Error: BRAINTRUST_API_KEY environment variable is required!")
        return

    try:
        service = DatasetAugmentationService(braintrust_api_key)

        # Step 1: Get dataset ID from user
        print("\n📊 Dataset Selection")

        # Option to list datasets
        questions = [inquirer.Confirm('list_datasets', message="Would you like to see available datasets first?", default=False)]
        answers = inquirer.prompt(questions)
        list_datasets_choice = answers['list_datasets']

        if list_datasets_choice:
            print("\n🔍 Fetching available datasets...")
            try:
                datasets = await service.braintrust_client.list_datasets()
                if datasets:
                    print("\n📋 Available Datasets:")
                    for i, dataset in enumerate(datasets[:10], 1):  # Show first 10
                        print(f"  {i}. {dataset.get('name', 'Unnamed')} (ID: {dataset.get('id', 'Unknown')})")
                        if dataset.get('description'):
                            print(f"     Description: {dataset['description']}")
                else:
                    print("No datasets found.")
            except Exception as e:
                print(f"⚠️  Could not list datasets: {e}")

        questions = [inquirer.Text('dataset_id', message="Enter the dataset ID to augment")]
        answers = inquirer.prompt(questions)
        dataset_id = answers['dataset_id']
        if not dataset_id.strip():
            print("❌ Dataset ID is required")
            return

        # Step 2: Get number of samples to analyze
        questions = [inquirer.Text('num_samples',
                                   message="How many samples should I analyze? (recommended: 20-50)",
                                   default="30",
                                   validate=lambda _, x: x.isdigit() and int(x) > 0)]
        answers = inquirer.prompt(questions)
        num_samples = int(answers['num_samples'])

        # Step 3: Fetch samples
        print(f"\n📥 Fetching {num_samples} samples from dataset...")
        try:
            samples = await service.braintrust_client.fetch_samples(dataset_id, num_samples)
            if not samples:
                print("❌ No samples found in dataset")
                return
            print(f"✅ Successfully fetched {len(samples)} samples")
        except Exception as e:
            print(f"❌ Failed to fetch samples: {e}")
            return

        # Step 3.5: Fetch dataset metadata
        print(f"\n📊 Fetching dataset information...")
        try:
            dataset_metadata = await service.braintrust_client.get_dataset_info(dataset_id)
            print(f"✅ Dataset info retrieved: {dataset_metadata.get('name', 'Unnamed')}")
            if dataset_metadata.get('description'):
                print(f"   📝 Description: {dataset_metadata['description']}")
        except Exception as e:
            print(f"⚠️  Could not fetch dataset metadata: {e}")
            dataset_metadata = None

        # Step 4: Analyze gaps (legacy method)
        print(f"\n🔍 Analyzing dataset gaps with {DEFAULT_MODEL}...")
        try:
            gap_analysis = await service.analyze_dataset_gaps(samples, dataset_metadata)
            print("✅ Gap analysis complete")
        except Exception as e:
            print(f"❌ Failed to analyze gaps: {e}")
            return

        # Step 5: Show suggestions and get user selection
        print("\n💡 Gap Analysis Results:")
        print(f"Overall Assessment: {gap_analysis.overall_assessment}")
        print("\n📋 Suggestions:")

        choices = []
        for i, suggestion in enumerate(gap_analysis.suggestions, 1):
            print(f"\n{i}. {suggestion.title}")
            print(f"   Description: {suggestion.description}")
            print(f"   Rationale: {suggestion.rationale}")
            choices.append((f"{suggestion.title}", suggestion))

        if not choices:
            print("❌ No suggestions generated")
            return

        # Interactive selection
        questions = [inquirer.Checkbox('suggestions',
                                        message="Select suggestions to generate samples for",
                                        choices=choices)]
        answers = inquirer.prompt(questions)
        selected_suggestions = answers['suggestions']

        if not selected_suggestions:
            print("❌ No suggestions selected")
            return

        # Step 6: Infer dataset schema (Phase 1)
        print("\n🔍 Analyzing dataset schema for precise generation...")
        try:
            schema = await service.infer_dataset_schema(samples, dataset_metadata)
            print("✅ Schema analysis complete")
            print(f"   📋 Input Schema: {len(schema.input_schema.get('properties', {}))} properties")
            print(f"   📋 Expected Schema: {len(schema.expected_schema.get('properties', {}))} properties")
            print(f"   📋 Metadata Schema: {len(schema.metadata_schema.get('properties', {}))} properties")
            print(f"   📋 Observed {len(schema.observed_patterns)} concrete patterns")
        except Exception as e:
            print(f"❌ Failed to analyze schema: {e}")
            return

        # Step 7: Generate samples using documented schema (Phase 2)
        print(f"\n🏭 Generating {len(selected_suggestions)} samples using documented schema...")
        generated_samples = []

        for suggestion in selected_suggestions:
            try:
                print(f"  📝 Generating sample for: {suggestion.title}")
                sample = await service.generate_sample_for_suggestion(suggestion, samples, schema, dataset_metadata)
                generated_samples.append(sample)
                print(f"  ✅ Generated: {suggestion.title}")
            except Exception as e:
                print(f"  ❌ Failed to generate sample for '{suggestion.title}': {e}")

        if not generated_samples:
            print("❌ No samples were successfully generated")
            return

        # Step 8: Preview generated samples
        print(f"\n👀 Preview of {len(generated_samples)} generated samples:")
        print("=" * 60)

        for i, sample in enumerate(generated_samples, 1):
            print(f"\nSample {i}:")
            print(f"Input: {json.dumps(sample.input, indent=2)}")
            print(f"Expected: {json.dumps(sample.expected, indent=2)}")
            print(f"Metadata: {json.dumps(sample.metadata, indent=2)}")
            print("-" * 40)

        # Step 9: Confirm push to dataset
        questions = [inquirer.Confirm('push_confirmed',
                                       message=f"Push these {len(generated_samples)} samples to the dataset?",
                                       default=True)]
        answers = inquirer.prompt(questions)
        push_confirmed = answers['push_confirmed']

        if not push_confirmed:
            print("❌ Operation cancelled by user")
            return

        # Step 10: Push to dataset
        print(f"\n📤 Pushing {len(generated_samples)} samples to dataset...")
        try:
            await service.braintrust_client.insert_samples(dataset_id, generated_samples)
            print("✅ Successfully pushed samples to dataset!")
        except Exception as e:
            print(f"❌ Failed to push samples: {e}")
            return

        # Step 11: Summary
        print("\n🎉 Dataset Augmentation Complete!")
        print(f"   • Dataset ID: {dataset_id}")
        print(f"   • Samples analyzed: {len(samples)}")
        print(f"   • Suggestions generated: {len(gap_analysis.suggestions)}")
        print(f"   • Selected suggestions: {len(selected_suggestions)}")
        print(f"   • New samples created: {len(generated_samples)}")
        print(f"   • Estimated dataset size increase: {len(generated_samples)}/{len(samples)} ({100*len(generated_samples)/len(samples):.1f}%)")

    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    import sys

    # Check for legacy mode flag
    if "--legacy" in sys.argv:
        print("🔄 Running in legacy mode...")
        asyncio.run(legacy_workflow())
    else:
        # Use the new enhanced CLI by default
        asyncio.run(main())
