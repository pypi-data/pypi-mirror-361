"""
Enhanced CLI interface for dataset augmentation with iterative workflows and multi-project support.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

# Interactive CLI components
try:
    import inquirer
except ImportError:
    print("Please install inquirer: pip install inquirer")
    exit(1)

from .augmentation_service import DatasetAugmentationService
from .braintrust_client import BraintrustClient
from .config import get_project_api_key, select_or_create_project
from .models import CaseAbstract, DatasetSample, GeneratedSample


class DatasetAugmentationCLI:
    """Enhanced CLI for dataset augmentation with multiple workflows and projects"""

    def __init__(self, project_name: str):
        self.project_name = project_name
        self.service: Optional[DatasetAugmentationService] = None
        self.braintrust_client: Optional[BraintrustClient] = None

    def _setup_service(self) -> bool:
        """Initialize the service with API keys for the selected project"""
        try:
            # Get API key for the specific project
            braintrust_api_key = get_project_api_key(self.project_name)
            
            # Initialize services
            self.service = DatasetAugmentationService(braintrust_api_key)
            self.braintrust_client = BraintrustClient(braintrust_api_key)
            return True
            
        except Exception as e:
            print(f"❌ Failed to set up project '{self.project_name}': {e}")
            return False

    async def run(self):
        """Main CLI application entry point"""
        print("🧠 Dataset Augmentation CLI Tool")
        print("=" * 50)
        print(f"📂 Project: {self.project_name}")
        print()

        if not self._setup_service():
            return

        try:
            # Mode selection
            questions = [
                inquirer.List(
                    'mode',
                    message="Select operation mode",
                    choices=[
                        ('🔧 Augment Dataset (Interactive)', 'augment'),
                        ('📁 Upload JSON File', 'upload'),
                    ],
                )
            ]
            answers = inquirer.prompt(questions)

            if answers['mode'] == 'augment':
                await self._run_augmentation_workflow()
            elif answers['mode'] == 'upload':
                await self._run_upload_workflow()

        except KeyboardInterrupt:
            print("\n❌ Operation cancelled by user")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")

    async def _run_upload_workflow(self):
        """Simple JSON file upload workflow"""
        print("\n📁 JSON File Upload Mode")
        print("=" * 30)

        # Get dataset ID
        dataset_id = await self._get_dataset_id()
        if not dataset_id:
            return

        # Get JSON file path
        questions = [
            inquirer.Text(
                'file_path',
                message="Enter path to JSON file containing samples",
                validate=lambda _, x: Path(x).exists() and Path(x).is_file()
            )
        ]
        answers = inquirer.prompt(questions)
        file_path = answers['file_path']

        # Load and validate JSON file
        try:
            with open(file_path, 'r') as f:
                samples_data = json.load(f)

            if not isinstance(samples_data, list):
                print("❌ JSON file must contain a list of samples")
                return

            print(f"📋 Loaded {len(samples_data)} samples from {file_path}")

            # Preview samples
            print("\n👀 Sample preview:")
            for i, sample in enumerate(samples_data[:3], 1):
                print(f"Sample {i}: {json.dumps(sample, indent=2)[:200]}{'...' if len(str(sample)) > 200 else ''}")

            if len(samples_data) > 3:
                print(f"... and {len(samples_data) - 3} more samples")

        except Exception as e:
            print(f"❌ Failed to load JSON file: {e}")
            return

        # Confirm upload
        questions = [
            inquirer.Confirm(
                'confirm_upload',
                message=f"Upload {len(samples_data)} samples to dataset {dataset_id}?",
                default=True
            )
        ]
        answers = inquirer.prompt(questions)

        if not answers['confirm_upload']:
            print("❌ Operation cancelled")
            return

        # Upload samples
        try:
            print(f"\n📤 Uploading {len(samples_data)} samples...")
            await self.braintrust_client.insert_samples_from_dict(dataset_id, samples_data)
            print("✅ Samples uploaded successfully!")

        except Exception as e:
            print(f"❌ Failed to upload samples: {e}")

    async def _run_augmentation_workflow(self):
        """Interactive dataset augmentation workflow"""
        print("\n🔧 Dataset Augmentation Mode")
        print("=" * 35)

        # Get dataset ID and samples
        dataset_id = await self._get_dataset_id()
        if not dataset_id:
            return

        # Fetch dataset metadata
        print(f"\n📊 Fetching dataset information...")
        try:
            dataset_metadata = await self.braintrust_client.get_dataset_info(dataset_id)
            print(f"✅ Dataset info retrieved: {dataset_metadata.get('name', 'Unnamed')}")
            if dataset_metadata.get('description'):
                print(f"   📝 Description: {dataset_metadata['description']}")
        except Exception as e:
            print(f"⚠️  Could not fetch dataset metadata: {e}")
            dataset_metadata = None

        samples = await self._fetch_samples(dataset_id)
        if not samples:
            return

        # Infer schema first (with dataset metadata)
        print("\n🔍 Analyzing dataset schema...")
        try:
            schema = await self.service.infer_dataset_schema(samples, dataset_metadata)
            print("✅ Schema analysis complete")
        except Exception as e:
            print(f"❌ Failed to analyze schema: {e}")
            return

        # Get user guidance and generate case abstracts iteratively (with dataset metadata)
        case_abstracts = await self._get_case_abstracts_iteratively(samples, dataset_metadata)
        if not case_abstracts:
            return

        # Generate samples for approved abstracts with immediate upload (with dataset metadata)
        uploaded_count = await self._generate_samples_with_review(
            case_abstracts, samples, schema, dataset_id, dataset_metadata
        )
        
        if uploaded_count == 0:
            print("❌ No samples were approved and uploaded")
        else:
            print(f"\n🎉 Dataset Augmentation Complete!")
            print(f"   • Dataset ID: {dataset_id}")
            print(f"   • Samples uploaded: {uploaded_count}")

    async def _get_dataset_id(self) -> Optional[str]:
        """Get dataset ID from user with scrollable dataset selection"""
        print("\n📊 Dataset Selection")

        # Option to browse datasets or enter manually
        questions = [
            inquirer.List(
                'selection_method',
                message="How would you like to select a dataset?",
                choices=[
                    ('📋 Browse available datasets (recommended)', 'browse'),
                    ('✏️  Enter dataset ID manually', 'manual'),
                ],
                default='browse'
            )
        ]
        answers = inquirer.prompt(questions)

        if answers['selection_method'] == 'browse':
            print("\n🔍 Fetching available datasets...")
            try:
                datasets = await self.braintrust_client.list_datasets()
                if not datasets:
                    print("No datasets found. You'll need to create one first.")
                    return None

                # Create choices for inquirer with dataset info
                choices = []
                for dataset in datasets:
                    name = dataset.get('name', 'Unnamed')
                    dataset_id = dataset.get('id', 'Unknown')
                    description = dataset.get('description', '')
                    
                    # Create display string with name, ID, and description
                    if description:
                        display = f"{name} ({dataset_id}) - {description[:60]}{'...' if len(description) > 60 else ''}"
                    else:
                        display = f"{name} ({dataset_id})"
                    
                    choices.append((display, dataset_id))

                # Add option to enter manually as fallback
                choices.append(('✏️  Enter dataset ID manually instead', 'manual'))

                questions = [
                    inquirer.List(
                        'selected_dataset',
                        message=f"Select dataset to augment ({len(datasets)} available)",
                        choices=choices,
                        carousel=True  # Enable scrolling for long lists
                    )
                ]
                answers = inquirer.prompt(questions)

                if answers['selected_dataset'] == 'manual':
                    # Fall through to manual entry
                    pass
                else:
                    return answers['selected_dataset']

            except Exception as e:
                print(f"⚠️  Could not list datasets: {e}")
                print("Falling back to manual entry...")

        # Manual entry (either chosen directly or as fallback)
        questions = [
            inquirer.Text('dataset_id', message="Enter the dataset ID to augment")
        ]
        answers = inquirer.prompt(questions)
        dataset_id = answers['dataset_id']

        if not dataset_id.strip():
            print("❌ Dataset ID is required")
            return None

        return dataset_id.strip()

    async def _fetch_samples(self, dataset_id: str) -> Optional[List[DatasetSample]]:
        """Fetch samples from dataset"""
        questions = [
            inquirer.Text(
                'num_samples',
                message="How many samples should I analyze? (recommended: 20-50)",
                default="30",
                validate=lambda _, x: x.isdigit() and int(x) > 0
            )
        ]
        answers = inquirer.prompt(questions)
        num_samples = int(answers['num_samples'])

        print(f"\n📥 Fetching {num_samples} samples from dataset...")
        try:
            samples = await self.braintrust_client.fetch_samples(dataset_id, num_samples)
            if not samples:
                print("❌ No samples found in dataset")
                return None
            print(f"✅ Successfully fetched {len(samples)} samples")
            return samples
        except Exception as e:
            print(f"❌ Failed to fetch samples: {e}")
            return None

    async def _get_case_abstracts_iteratively(self, samples: List[DatasetSample], dataset_metadata: Optional[Dict[str, Any]]) -> Optional[List[CaseAbstract]]:
        """Iteratively refine case abstracts based on user guidance"""
        print("\n💡 Test Case Generation")
        print("=" * 25)

        # Get initial user guidance
        questions = [
            inquirer.Text(
                'guidance',
                message="What kinds of test cases would you like me to generate?\n(e.g., 'edge cases for date parsing', 'error handling scenarios', 'boundary conditions')"
            )
        ]
        answers = inquirer.prompt(questions)
        user_guidance = answers['guidance']

        if not user_guidance.strip():
            print("❌ User guidance is required")
            return None

        # Iterative refinement loop
        feedback = ""
        while True:
            print("\n🔍 Generating case abstracts based on your guidance...")
            try:
                case_abstract_list = await self.service.generate_case_abstracts_with_guidance(
                    samples, user_guidance, feedback, dataset_metadata
                )
                print("✅ Case abstracts generated")
            except Exception as e:
                print(f"❌ Failed to generate case abstracts: {e}")
                return None

            # Show generated abstracts
            print(f"\n📋 Generated {len(case_abstract_list.abstracts)} case abstracts:")
            print("-" * 60)

            for i, abstract in enumerate(case_abstract_list.abstracts, 1):
                print(f"\n{i}. {abstract.title}")
                print(f"   Description: {abstract.description}")
                print(f"   Input: {abstract.expected_input_characteristics}")
                print(f"   Output: {abstract.expected_output_characteristics}")

            if case_abstract_list.generation_notes:
                print(f"\n📝 Notes: {case_abstract_list.generation_notes}")

            # User feedback/approval
            questions = [
                inquirer.List(
                    'action',
                    message="What would you like to do?",
                    choices=[
                        ('✅ Approve these abstracts and generate samples', 'approve'),
                        ('📝 Provide feedback to refine the list', 'feedback'),
                        ('❌ Cancel', 'cancel'),
                    ],
                )
            ]
            answers = inquirer.prompt(questions)

            if answers['action'] == 'approve':
                return case_abstract_list.abstracts
            elif answers['action'] == 'feedback':
                questions = [
                    inquirer.Text(
                        'feedback',
                        message="What changes would you like? (e.g., 'add more error cases', 'focus on edge cases', 'remove abstract #3')"
                    )
                ]
                answers = inquirer.prompt(questions)
                feedback = answers['feedback']
                if not feedback.strip():
                    print("⚠️  No feedback provided, keeping current list")
                    return case_abstract_list.abstracts
                print(f"\n🔄 Incorporating feedback: {feedback}")
            else:  # cancel
                print("❌ Operation cancelled")
                return None

    async def _generate_samples_with_review(
        self,
        case_abstracts: List[CaseAbstract],
        reference_samples: List[DatasetSample],
        schema,
        dataset_id: str,
        dataset_metadata: Optional[Dict[str, Any]]
    ) -> int:
        """Generate samples with individual review and immediate upload to Braintrust"""
        print(f"\n🏭 Generating {len(case_abstracts)} samples...")
        print(f"💡 Approved samples will be immediately uploaded to dataset: {dataset_id}")
        print(f"⚡ Pre-generating next sample while you review for faster workflow!")

        uploaded_count = 0
        exported_samples = []  # Keep track for potential export

        # Generate first sample
        if not case_abstracts:
            return 0

        print(f"\n📝 Generating sample 1/{len(case_abstracts)}: {case_abstracts[0].title}")
        try:
            current_sample = await self.service.generate_sample_for_case_abstract(
                case_abstracts[0], reference_samples, schema, dataset_metadata
            )
            print(f"✅ Generated sample for: {case_abstracts[0].title}")
        except Exception as e:
            print(f"❌ Failed to generate sample for '{case_abstracts[0].title}': {e}")
            return uploaded_count

        # Process samples with pre-generation
        for i, abstract in enumerate(case_abstracts):
            next_sample_task = None
            
            # Start generating next sample in background (if there is one)
            if i + 1 < len(case_abstracts):
                next_abstract = case_abstracts[i + 1]
                print(f"🔄 Pre-generating next sample: {next_abstract.title}")
                next_sample_task = asyncio.create_task(
                    self.service.generate_sample_for_case_abstract(
                        next_abstract, reference_samples, schema, dataset_metadata
                    )
                )
                # Give the task a chance to start before the blocking prompt
                # Note: inquirer.prompt() blocks the event loop, so background task
                # will pause during user input but can resume between prompts
                await asyncio.sleep(0.5)

            # Review loop for this sample
            while True:
                print(f"\n👀 Review Sample {i + 1}/{len(case_abstracts)}: {abstract.title}")
                print("-" * 40)
                print(f"Input: {json.dumps(current_sample.input, indent=2)}")
                print(f"Expected: {json.dumps(current_sample.expected, indent=2)}")
                print(f"Metadata: {json.dumps(current_sample.metadata, indent=2)}")
                print("-" * 40)

                questions = [
                    inquirer.List(
                        'action',
                        message="What would you like to do with this sample?",
                        choices=[
                            ('✅ Accept and upload to Braintrust', 'accept'),
                            ('🔄 Request a variation', 'variation'),
                            ('⏭️  Skip this sample', 'skip'),
                            ('📁 Export generated samples to JSON and exit', 'export'),
                        ],
                    )
                ]
                answers = inquirer.prompt(questions)

                if answers['action'] == 'accept':
                    # Immediately upload to Braintrust
                    try:
                        print(f"📤 Uploading sample to dataset...")
                        await self.service.braintrust_client.insert_samples(dataset_id, [current_sample])
                        uploaded_count += 1
                        exported_samples.append(current_sample)  # Keep for potential export
                        print(f"✅ Sample uploaded successfully! (Total uploaded: {uploaded_count})")
                        break
                    except Exception as e:
                        print(f"❌ Failed to upload sample: {e}")
                        # Ask user what to do
                        questions = [
                            inquirer.List(
                                'retry_action',
                                message="Upload failed. What would you like to do?",
                                choices=[
                                    ('🔄 Try uploading again', 'retry'),
                                    ('💾 Save for later export', 'save'),
                                    ('⏭️  Skip this sample', 'skip'),
                                ],
                            )
                        ]
                        retry_answers = inquirer.prompt(questions)
                        
                        if retry_answers['retry_action'] == 'retry':
                            continue  # Stay in the loop to try upload again
                        elif retry_answers['retry_action'] == 'save':
                            exported_samples.append(current_sample)
                            print("💾 Sample saved for potential export")
                            break
                        else:  # skip
                            break
                elif answers['action'] == 'variation':
                    questions = [
                        inquirer.Text(
                            'variation_request',
                            message="What variation would you like? (e.g., 'make it more complex', 'use different data', 'add edge case')"
                        )
                    ]
                    variation_answers = inquirer.prompt(questions)
                    variation_request = variation_answers['variation_request']

                    if not variation_request.strip():
                        print("⚠️  No variation request provided, keeping current sample")
                        continue

                    print(f"🔄 Generating variation: {variation_request}")
                    try:
                        current_sample = await self.service.generate_sample_variation(
                            current_sample, abstract, variation_request, schema, dataset_metadata
                        )
                        print("✅ Variation generated")
                    except Exception as e:
                        print(f"❌ Failed to generate variation: {e}")
                        print("⚠️  Keeping original sample")
                elif answers['action'] == 'skip':
                    print(f"⏭️  Skipped sample: {abstract.title}")
                    break
                elif answers['action'] == 'export':
                    # Cancel the background task if user wants to exit
                    if next_sample_task and not next_sample_task.done():
                        next_sample_task.cancel()
                        print("🛑 Cancelled background generation")
                    
                    # Include current sample if user wants to export
                    all_samples = exported_samples + [current_sample]
                    await self._export_to_json(all_samples)
                    print(f"📊 Session summary: {uploaded_count} samples uploaded, {len(all_samples)} samples exported")
                    return uploaded_count
            
            # Prepare for next iteration - get the pre-generated sample
            if next_sample_task:
                try:
                    if next_sample_task.done():
                        print(f"⚡ Next sample already ready!")
                        current_sample = await next_sample_task
                    else:
                        print(f"⏳ Waiting for pre-generation to complete...")
                        current_sample = await next_sample_task
                        print(f"✅ Generation complete!")
                    print(f"📋 Next sample: {case_abstracts[i + 1].title}")
                except Exception as e:
                    print(f"❌ Failed to generate next sample '{case_abstracts[i + 1].title}': {e}")
                    # If we can't get the next sample, we'll break out of the loop
                    break

        print(f"\n📊 Sample generation complete!")
        print(f"   • Total samples uploaded: {uploaded_count}")
        return uploaded_count

    async def _export_to_json(self, samples: List[GeneratedSample]):
        """Export samples to JSON file"""
        questions = [
            inquirer.Text(
                'export_path',
                message="Enter path for JSON export file",
                default="generated_samples.json"
            )
        ]
        answers = inquirer.prompt(questions)
        export_path = answers['export_path']

        try:
            export_data = []
            for sample in samples:
                export_data.append({
                    "input": sample.input,
                    "expected": sample.expected,
                    "metadata": sample.metadata
                })

            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)

            print(f"✅ Exported {len(samples)} samples to {export_path}")
            print("💡 You can later upload this file using 'Upload JSON File' mode")

        except Exception as e:
            print(f"❌ Failed to export samples: {e}")




async def main_async():
    """Main async entry point with project selection"""
    parser = argparse.ArgumentParser(
        description="AUGR - AI-powered dataset augmentation tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  augr                    # Use existing project or create default
  augr -p myproject       # Create new project 'myproject'
  augr --help            # Show this help message
  augr uninstall         # Remove AUGR and all projects

Projects allow you to organize different datasets and API configurations.
Each project maintains its own Braintrust API key and settings.

For more information, visit: https://github.com/Marviel/augr
        """
    )
    
    parser.add_argument(
        "-p", "--project",
        help="Create a new project with the given name",
        metavar="PROJECT_NAME"
    )
    
    # Handle special case: if only --help or -h, show help and exit
    if len(sys.argv) == 2 and sys.argv[1] in ['-h', '--help']:
        parser.print_help()
        return
    
    try:
        args = parser.parse_args()
        
        # Project selection logic
        if args.project:
            # Create new project
            try:
                project_name = select_or_create_project(create_new=True, new_project_name=args.project)
                print(f"✅ Creating new project: {project_name}")
            except Exception as e:
                print(f"❌ {e}")
                return
        else:
            # Select existing project or create default
            try:
                project_name = select_or_create_project(create_new=False)
            except Exception as e:
                print(f"❌ {e}")
                return
        
        # Run the CLI with the selected project
        cli = DatasetAugmentationCLI(project_name)
        await cli.run()
        
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
    except SystemExit:
        # This happens when argparse encounters --help or invalid args
        pass


def main():
    """Main entry point"""
    # Handle special commands that don't require async
    if len(sys.argv) > 1:
        if sys.argv[1] == "uninstall":
            from .uninstall import main as uninstall_main
            uninstall_main()
            return
        elif sys.argv[1] in ["--help", "-h"]:
            # Let argparse handle this in main_async
            pass
    
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
