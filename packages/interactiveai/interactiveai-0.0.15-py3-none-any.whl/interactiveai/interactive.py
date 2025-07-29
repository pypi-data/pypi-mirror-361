import time
from typing import Dict, Any, List, Optional, Callable, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
from packages.langfuse import Langfuse
from langfuse.langchain import CallbackHandler
from interactiveai.evaluators import Evaluator


class Interactive(Langfuse):
    """
    A comprehensive manager class for InteractiveAI utilities including initialization,
    observation, scoring, dataset management, and parallel processing.
    """

    def __init__(self,
                 public_key: str,
                 secret_key: str,
                 host: Optional[str] = "https://app.interactiveai.com",
                 **kwargs):
        """
        Initialize the InteractiveAI Client

        To get your keys go to https://app.interactiveai.com/settings/api-keys

        Args:
            public_key: InteractiveAI public key
            secret_key: InteractiveAI secret key
            host: InteractiveAI host (defaults to https://app.interactiveai.com)
        """
        # Initialize InteractiveAI client
        super().__init__(
            public_key=public_key,
            secret_key=secret_key,
            host=host,
            **kwargs
        )

    def generate_thread_id(self) -> str:
        """Generate a unique thread ID"""
        thread_id = f"thread_{int(time.time() * 1000)}"
        return thread_id


    def create_or_get_dataset(self, dataset_name: str, description: str = "") -> Any:
        """
        Create a dataset or get existing one

        Args:
            dataset_name: Name of the dataset
            description: Dataset description

        Returns:
            Dataset object
        """
        try:
            dataset = self.get_dataset(dataset_name)
            return dataset
        except Exception as e:
            try:
                dataset = self.create_dataset(
                    name=dataset_name,
                    description=description or "Dataset for response evaluation",
                )
                return dataset
            except Exception as create_error:
                raise

    def add_dataset_item(self, dataset_name: str, item_id: str, input_data: Dict[str, Any],
                        expected_output: Dict[str, Any], metadata: Dict[str, Any]):
        """
        Add an item to a dataset

        Args:
            dataset_name: Name of the dataset
            item_id: Unique identifier for the item
            input_data: Input data
            expected_output: Expected output
            metadata: Additional metadata
        """
        try:
            self.create_dataset_item(
                dataset_name=dataset_name,
                input=input_data,
                expected_output=expected_output,
                metadata=metadata,
                id=item_id
            )
        except Exception as e:
            raise

    def add_dataset_items_parallel(self, dataset_name: str, data: List[tuple[str, Any]], max_workers: int = 4):
        """
        Add multiple items to a dataset in parallel

        Args:
            dataset_name: Name of the dataset
            data: List of tuples containing (item_id, input_data, expected_output, metadata)
            max_workers: Maximum number of parallel workers (default: 4)
        """
        try:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for item_id, input_data, expected_output, metadata in data:
                    futures.append(
                        executor.submit(
                            self.add_dataset_item,
                            dataset_name,
                            item_id,
                            input_data,
                            expected_output,
                            metadata
                        )
                    )
                for future in as_completed(futures):
                    future.result()  # Wait for all tasks to complete
        except Exception as e:
            raise

    def process_single_item(
            self,
            idx: int,
            item: Any,
            experiment_name: str,
            handler: CallbackHandler,
            workflow: Any,
            evaluations: List[Evaluator]
    ) -> Dict[str, Union[str, Dict[str, Any]]]:
        """Process a single dataset item through the workflow and evaluate results.

        Args:
            idx: Index of the item in the dataset
            item: Dataset item containing input and expected output
            experiment_name: Name of the experiment for tracking
            handler: InteractiveAI callback handler for logging
            workflow: The workflow/model to process the item
            evaluations: List of evaluation functions to apply

        Returns:
            Dictionary containing processing status and results or error information
        """
        try:
            # Create a separate trace for each item using the item.run() context manager
            with item.run(run_name=experiment_name) as root_span:
                # Process the item through the workflow
                output = workflow.invoke(
                    state=item.input,
                    config={
                        "callbacks": [handler],
                        "configurable": {"thread_id": idx}  # Use idx as thread_id for uniqueness
                    }
                )

                # Update the trace with input/output information
                root_span.update_trace(
                    name=f"{experiment_name}_{idx}",
                    input=item.input,
                    output=output,
                    tags=[experiment_name],
                    metadata=item.metadata
                )

                # Apply all evaluation functions to the output
                for evaluation in evaluations:
                    try:
                        evaluation_result = evaluation.function(output, item.expected_output)
                        root_span.score_trace(
                            name=evaluation.name,
                            value=evaluation_result.score,
                            data_type=evaluation.data_type,
                            comment=evaluation_result.reasoning
                        )
                    except Exception as eval_error:
                        # Continue with other evaluations even if one fails
                        pass

                return {"status": "success", "output": output}

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def run_langchain_experiment_multi(
            self,
            experiment_name: str,
            dataset: Any,
            workflow: Any,
            evaluations: List[Evaluator],
            max_workers: int = 4,
            start_index: int = 0,
            end_index: Optional[int] = None,
            process_single_item_func: Optional[Callable] = None
    ) -> List[Dict[str, Union[str, Dict[str, Any]]]]:
        """Run an experiment with parallel processing using ThreadPool.

        This function processes multiple dataset items in parallel, applies evaluations,
        and tracks results using InteractiveAI for monitoring and analysis.

        Args:
            experiment_name: Name of the experiment for tracking and logging
            dataset: Dataset containing items to process
            workflow: The workflow/model to process items
            evaluations: List of evaluation functions to apply to results
            max_workers: Maximum number of parallel workers (default: 4)
            start_index: Index to start processing from (default: 0)
            end_index: Index to stop processing at (default: None for all items)
            process_single_item_func: Optional custom processing function (default: None)

        Returns:
            List of result dictionaries containing status and output/error information

        Raises:
            ValueError: If start_index >= end_index or if indices are out of bounds
        """
        # Set end_index to dataset length if not provided
        if end_index is None:
            end_index = len(dataset.items)

        # Validate indices
        if start_index >= end_index:
            raise ValueError(f"start_index ({start_index}) must be less than end_index ({end_index})")

        if start_index < 0 or end_index > len(dataset.items):
            raise ValueError(f"Indices out of bounds: dataset has {len(dataset.items)} items")

        # Use provided processing function or default
        if process_single_item_func:
            processing_func = process_single_item_func
        else:
            processing_func = self.process_single_item

        # Calculate actual number of items to process
        items_to_process = end_index - start_index


        # Initialize InteractiveAI handler for tracking
        handler = CallbackHandler()

        # Process items in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=max_workers) as executor:

            # Prepare arguments for each item to process
            process_args = [
                (idx, item, experiment_name, handler, workflow, evaluations)
                for idx, item in enumerate(dataset.items[start_index:end_index], start=start_index)
            ]

            # Submit all tasks to the executor
            future_to_args = {
                executor.submit(processing_func, *args): args
                for args in process_args
            }


            # Collect results as they complete
            results: List[Dict[str, Union[str, Dict[str, Any]]]] = []
            completed_count = 0

            for future in as_completed(future_to_args):
                args = future_to_args[future]
                item_idx = args[0]  # First argument is the index

                try:
                    result = future.result()
                    results.append(result)
                    completed_count += 1

                except Exception as e:
                    results.append({"status": "exception", "error": str(e)})
                    completed_count += 1

        # Calculate and log summary statistics
        successful = sum(1 for r in results if r["status"] == "success")
        failed = len(results) - successful
        success_rate = (successful / len(results)) * 100 if results else 0



        if failed > 0:
            pass

        return results

    def run_langchain_experiment_sequential(
            self,
            experiment_name: str,
            dataset: Any,
            workflow: Any,
            evaluations: List[Evaluator],
            start_index: int = 0,
            end_index: Optional[int] = None,
            process_single_item_func: Optional[Callable] = None
    ) -> List[Dict[str, Union[str, Dict[str, Any]]]]:
        """Run an experiment with sequential processing (no parallel processing).

        This function processes multiple dataset items sequentially, applies evaluations,
        and tracks results using InteractiveAI for monitoring and analysis.

        Args:
            experiment_name: Name of the experiment for tracking and logging
            dataset: Dataset containing items to process
            workflow: The workflow/model to process items
            evaluations: List of evaluation functions to apply to results
            start_index: Index to start processing from (default: 0)
            end_index: Index to stop processing at (default: None for all items)
            process_single_item_func: Optional custom processing function (default: None)

        Returns:
            List of result dictionaries containing status and output/error information

        Raises:
            ValueError: If start_index >= end_index or if indices are out of bounds
        """
        # Set end_index to dataset length if not provided
        if end_index is None:
            end_index = len(dataset.items)

        # Validate indices
        if start_index >= end_index:
            raise ValueError(f"start_index ({start_index}) must be less than end_index ({end_index})")

        if start_index < 0 or end_index > len(dataset.items):
            raise ValueError(f"Indices out of bounds: dataset has {len(dataset.items)} items")

        # Use provided processing function or default
        if process_single_item_func:
            processing_func = process_single_item_func
        else:
            processing_func = self.process_single_item

        # Calculate actual number of items to process
        items_to_process = end_index - start_index


        # Initialize InteractiveAI handler for tracking
        handler = CallbackHandler()

        # Process items sequentially
        results: List[Dict[str, Union[str, Dict[str, Any]]]] = []
        completed_count = 0

        for idx, item in enumerate(dataset.items[start_index:end_index], start=start_index):
            try:
                result = processing_func(idx, item, experiment_name, handler, workflow, evaluations)
                results.append(result)
                completed_count += 1

            except Exception as e:
                results.append({"status": "exception", "error": str(e)})
                completed_count += 1

        # Calculate and log summary statistics
        successful = sum(1 for r in results if r["status"] == "success")
        failed = len(results) - successful
        success_rate = (successful / len(results)) * 100 if results else 0



        if failed > 0:
            pass

        return results


    def flush(self):
        """Flush any pending InteractiveAI operations"""
        try:
            self.flush()
        except Exception as e:
            pass
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - flush operations"""
        if exc_type:
            pass
        self.flush()

















