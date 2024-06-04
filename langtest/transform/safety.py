import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List

from ..datahandler.datasource import DataFactory
from langtest.errors import Errors
from langtest.modelhandler.modelhandler import ModelAPI
from langtest.tasks.task import TaskManager
from langtest.transform.base import ITests
from langtest.utils.custom_types.sample import Sample


class SafetyTestFactory(ITests):
    alias_name = "safety"
    supported_tasks = ["text-classification", "question-answering"]

    def __init__(self, data_handler: List[Sample], tests: Dict = None, **kwargs) -> None:
        """Initialize a new SafetyTestFactory instance."""

        self.supported_tests = self.available_tests()
        self._data_handler = data_handler
        self.tests = tests
        self.kwargs = kwargs

        if not isinstance(self.tests, dict):
            raise ValueError(Errors.E048())

        if len(self.tests) == 0:
            self.tests = self.supported_tests

        not_supported_tests = set(self.tests) - set(self.supported_tests)
        if len(not_supported_tests) > 0:
            raise ValueError(
                Errors.E049(
                    not_supported_tests=not_supported_tests,
                    supported_tests=list(self.supported_tests.keys()),
                )
            )

    def transform(self) -> List[Sample]:
        """Execute the Safety test and return resulting `Sample` objects."""
        all_samples = []
        no_transformation_applied_tests = {}
        tests_copy = self.tests.copy()
        for test_name, params in tests_copy.items():
            if test_name not in self.supported_tests:
                no_transformation_applied_tests[test_name] = params
                continue
            test = self.supported_tests[test_name](self._data_handler, **params)
            all_samples.extend(test.transform())
        return all_samples

    @classmethod
    def available_tests(cls) -> Dict:
        """Return a dictionary of available tests."""
        return BaseSafetyTest.registered_tests


class BaseSafetyTest(ABC):
    """Base class for Safety tests."""

    alias_name = None
    supported_tasks = []
    registered_tests = {}

    def __init__(self, data_handler: List[Sample], **kwargs) -> None:
        """Initialize a new BaseSafetyTest instance."""
        self._data_handler = data_handler
        self.kwargs = kwargs

    @abstractmethod
    def transform(self) -> List[Sample]:
        """Execute the Safety test and return resulting `Sample` objects."""
        pass

    @classmethod
    async def run(sample_list: List[Sample], model: ModelAPI, **kwargs) -> List[Sample]:
        """Run the Safety test."""
        pass

    @classmethod
    async def async_run(
        cls, sample_list: List[Sample], model: ModelAPI, **kwargs
    ) -> List[Sample]:
        """Run the Safety test asynchronously."""

        created_task = asyncio.create_task(cls.run(sample_list, model, **kwargs))
        return await created_task

    def __init_subclass__(cls, *args, **kwargs) -> None:
        """Register the Safety test subclass."""
        if isinstance(cls.alias_name, list):
            for alias in cls.alias_name:
                if alias not in cls.registered_tests:
                    cls.registered_tests[alias] = cls
        elif cls.alias_name is not None and cls.alias_name not in cls.registered_tests:
            cls.registered_tests[cls.alias_name] = cls

        super().__init_subclass__(*args, **kwargs)


class Misuse(BaseSafetyTest):
    alias_name = "misuse"
    supported_tasks = ["question-answering"]
    """ Misuse test.
    """

    def transform(self) -> List[Sample]:
        """Execute the Misuse test and return resulting `Sample` objects."""
        data = DataFactory(
            file_path={
                "data_source": "BSS",
                "split": "test",
            },
            task=TaskManager("question-answering"),
        ).load()

        return data
