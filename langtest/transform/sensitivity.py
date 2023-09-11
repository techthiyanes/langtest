import asyncio
from abc import ABC, abstractmethod
from typing import List
from langtest.modelhandler.modelhandler import ModelFactory
from ..utils.custom_types import Sample


class BaseSensitivity(ABC):
    """Abstract base class for implementing sensitivity measures.

    Attributes:
        alias_name (str): A name or list of names that identify the sensitivity measure.

    Methods:
        transform(data: List[Sample]) -> Any: Transforms the input data into an output based on the implemented sensitivity measure.
    """

    alias_name = None
    supported_tasks = [
        "sensitivity-test",
    ]

    @staticmethod
    @abstractmethod
    def transform(sample_list: List[Sample]) -> List[Sample]:
        """Abstract method that implements the sensitivity measure.

        Args:
            sample_list (List[Sample]): The input data to be transformed.

        Returns:
            Any: The transformed data based on the implemented sensitivity measure.
        """
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    async def run(
        sample_list: List[Sample], model: ModelFactory, **kwargs
    ) -> List[Sample]:
        """Abstract method that implements the sensitivity measure.

        Args:
            sample_list (List[Sample]): The input data to be transformed.
            model (ModelFactory): The model to be used for evaluation.
            **kwargs: Additional arguments to be passed to the sensitivity measure.

        Returns:
            List[Sample]: The transformed data based on the implemented sensitivity measure.

        """
        progress = kwargs.get("progress_bar", False)
        for sample in sample_list:
            if sample.state != "done":
                if hasattr(sample, "run"):
                    sample_status = sample.run(model, **kwargs)
                    if sample_status:
                        sample.state = "done"
                else:
                    sample.expected_results = model(sample.original)
                    sample.actual_results = model(sample.test_case)
                    sample.state = "done"
            if progress:
                progress.update(1)
        return sample_list

    @classmethod
    async def async_run(cls, sample_list: List[Sample], model: ModelFactory, **kwargs):
        """Creates a task to run the sensitivity measure.

        Args:
            sample_list (List[Sample]): The input data to be transformed.
            model (ModelFactory): The model to be used for evaluation.
            **kwargs: Additional arguments to be passed to the sensitivity measure.

        Returns:
            asyncio.Task: The task that runs the sensitivity measure.

        """
        created_task = asyncio.create_task(cls.run(sample_list, model, **kwargs))
        return created_task