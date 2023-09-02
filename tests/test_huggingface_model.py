import unittest
from langtest.modelhandler import ModelAPI


class HuggingFaceTestCase(unittest.TestCase):
    """
    A test case for Hugging Face models.

    This test case performs tests related to loading and handling Hugging Face models using the `ModelAPI` class.

    Attributes:
        models (List[str]): A list of Hugging Face model names.
        tasks (List[str]): A list of tasks associated with the models.
    """

    def setUp(self) -> None:
        """
        Set up the test case.

        This method initializes the list of Hugging Face model names and the associated tasks.
        """
        self.models = [
            "dslim/bert-base-NER",
            "Jean-Baptiste/camembert-ner",
            "d4data/biomedical-ner-all",
        ]

        self.tasks = ["ner", "text-classifier"]

    def test_transformers_ner_models(self):
        """
        Test loading Hugging Face models.

        This method tests the loading of a Hugging Face model using the `ModelAPI` class.
        It asserts that the loaded model is an instance of `ModelAPI`.
        """
        model = ModelAPI.load_model(
            task=self.tasks[0], hub="huggingface", path=self.models[0]
        )
        self.assertIsInstance(model, ModelAPI)

    def test_transformers_QA_models(self):
        """
        Test loading Hugging Face models.

        This method tests the loading of a Hugging Face model using the `ModelAPI` class.
        It asserts that the loaded model is an instance of `ModelAPI`.
        """
        model = ModelAPI.load_model(
            task="question-answering", hub="huggingface", path="gpt2"
        )
        self.assertIsInstance(model, ModelAPI)

    def test_unsupported_task(self):
        """
        Test unsupported task.

        This method tests the behavior of `ModelAPI` when an unsupported task is provided.
        It expects an `AssertionError` to be raised when attempting to create a model with an unsupported task.
        """
        # Raises with unsupported task to model Factory
        with self.assertRaises(AssertionError):
            ModelAPI(self.models[0], self.tasks[1], hub="huggingface")
