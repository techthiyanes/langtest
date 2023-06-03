import asyncio
import evaluate
from abc import ABC, abstractmethod
from ..utils.custom_types import Sample
from typing import List


toxicity_metric = evaluate.load("toxicity", module_type="measurement")


class BaseToxicity(ABC):
    alias_name = None
    supported_tasks = ["toxicity"]

    @staticmethod
    @abstractmethod
    def transform(sample_list: List[Sample]):
        return NotImplementedError()

    @staticmethod
    @abstractmethod
    async def run(sample_list: List[Sample], model, *args, **kwargs):
        progress = kwargs.get("progress", False)
        for sample in sample_list:
            if sample.state != "done":
                if hasattr(sample, "run"):
                    sample_status = sample.run(model, *args, **kwargs)
                    if sample_status:
                        sample.state = "done"
                else:
                    sample.completion = model(sample.prompt)
                    global toxicity_metric
                    sample.completion_toxicity = toxicity_metric.compute(
                        predictions=[sample.completion])['toxicity'][0]
                    sample.state = "done"

            if progress:
                progress.update(1)
        return sample_list

    @classmethod
    async def async_run(cls, sample_list: List[Sample], model, *args, **kwargs):
        created_task = asyncio.create_task(
            cls.run(sample_list, model, **kwargs)
        )
        return created_task


class PromptToxicity(BaseToxicity):
    alias_name = "offensive"

    def transform(sample_list: List[Sample]) -> List[Sample]:
        for sample in sample_list:
            global toxicity_metric
            sample.prompt_toxicity = toxicity_metric.compute(
                predictions=[sample.prompt])['toxicity'][0]
            sample.test_type = "offensive"
            sample.category = "toxicity"

        return sample_list
