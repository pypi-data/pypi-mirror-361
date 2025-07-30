"""
Client for interacting with Braintrust REST API.
"""

from typing import Any, Dict, List

import httpx

from .models import DatasetSample, GeneratedSample

# Constants
BRAINTRUST_API_BASE = "https://api.braintrust.dev/v1"


class BraintrustClient:
    """Client for interacting with Braintrust REST API"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def list_datasets(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List available datasets"""
        try:
            async with httpx.AsyncClient() as client:
                url = f"{BRAINTRUST_API_BASE}/dataset"
                params = {"limit": limit}

                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )

                if response.status_code != 200:
                    error_text = response.text
                    raise Exception(f"API returned {response.status_code}: {error_text}")

                data = response.json()
                datasets = data.get("objects", [])

                return datasets

        except httpx.TimeoutException:
            raise Exception("Request timed out - check your internet connection")
        except httpx.RequestError as e:
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            if "API returned" in str(e):
                raise  # Re-raise API errors as-is
            raise Exception(f"Unexpected error listing datasets: {str(e)}")

    async def get_dataset_info(self, dataset_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific dataset"""
        try:
            async with httpx.AsyncClient() as client:
                url = f"{BRAINTRUST_API_BASE}/dataset/{dataset_id}"

                response = await client.get(
                    url,
                    headers=self.headers,
                    timeout=30.0
                )

                if response.status_code != 200:
                    error_text = response.text
                    raise Exception(f"API returned {response.status_code}: {error_text}")

                data = response.json()
                return data

        except httpx.TimeoutException:
            raise Exception("Request timed out - check your internet connection")
        except httpx.RequestError as e:
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            if "API returned" in str(e):
                raise  # Re-raise API errors as-is
            raise Exception(f"Unexpected error fetching dataset info: {str(e)}")

    async def fetch_samples(self, dataset_id: str, limit: int) -> List[DatasetSample]:
        """Fetch samples from a dataset"""
        try:
            async with httpx.AsyncClient() as client:
                url = f"{BRAINTRUST_API_BASE}/dataset/{dataset_id}/fetch"
                payload = {"limit": limit}

                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )

                if response.status_code != 200:
                    error_text = response.text
                    raise Exception(f"API returned {response.status_code}: {error_text}")

                data = response.json()
                events = data.get("events", [])

                samples = []
                for event in events:
                    # Handle missing fields gracefully
                    metadata = event.get("metadata")
                    if metadata is None:
                        metadata = {}

                    sample = DatasetSample(
                        id=event.get("id", ""),
                        input=event.get("input"),
                        expected=event.get("expected"),
                        metadata=metadata
                    )
                    samples.append(sample)

                return samples

        except httpx.TimeoutException:
            raise Exception("Request timed out - check your internet connection")
        except httpx.RequestError as e:
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            if "API returned" in str(e):
                raise  # Re-raise API errors as-is
            raise Exception(f"Unexpected error fetching samples: {str(e)}")

    async def insert_samples(self, dataset_id: str, samples: List[GeneratedSample]) -> bool:
        """Insert generated samples into dataset"""
        events = []
        for sample in samples:
            events.append({
                "input": sample.input,
                "expected": sample.expected,
                "metadata": sample.metadata
            })

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BRAINTRUST_API_BASE}/dataset/{dataset_id}/insert",
                headers=self.headers,
                json={"events": events}
            )

            if response.status_code != 200:
                raise Exception(f"Failed to insert samples: {response.status_code} {response.text}")

            return True

    async def insert_samples_from_dict(self, dataset_id: str, samples: List[Dict[str, Any]]) -> bool:
        """Insert samples from dictionary format (for JSON file uploads)"""
        events = []
        for sample in samples:
            # Ensure required fields are present
            if "input" not in sample or "expected" not in sample:
                raise ValueError(f"Sample missing required 'input' or 'expected' fields: {sample}")

            # Ensure metadata exists and has test_name
            metadata = sample.get("metadata", {})
            if "test_name" not in metadata:
                # Generate a default test_name if missing
                metadata["test_name"] = f"imported_sample_{len(events) + 1}"

            events.append({
                "input": sample["input"],
                "expected": sample["expected"],
                "metadata": metadata
            })

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BRAINTRUST_API_BASE}/dataset/{dataset_id}/insert",
                headers=self.headers,
                json={"events": events}
            )

            if response.status_code != 200:
                raise Exception(f"Failed to insert samples: {response.status_code} {response.text}")

            return True
