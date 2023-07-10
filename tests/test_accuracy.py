import unittest
import pandas as pd
from langtest import Harness


class AccuracyTestCase(unittest.TestCase):
    """
    A test case for accuracy evaluation.

    This test case performs accuracy evaluation using the `Harness` class from `langtest` package.
    It tests the accuracy of a named entity recognition (NER) model using a sample dataset in CoNLL format.

    Attributes:
        h_spacy (Harness): The `Harness` instance for evaluating the model.
        report (pd.DataFrame): The evaluation report generated by the `Harness`.
    """

    def setUp(self) -> None:
        """
        Set up the test case.

        This method initializes the `Harness` instance with the necessary configuration for evaluating the model.
        It configures the test settings, such as the minimum pass rate and minimum F1 score, for accuracy evaluation.
        """

        self.h_spacy = Harness(
            task="ner",
            model="en_core_web_sm",
            data="langtest/data/conll/sample.conll",
            hub="spacy",
        )
        self.h_spacy.configure(
            {
                "tests": {
                    "defaults": {
                        "min_pass_rate": 0.65,
                    },
                    "accuracy": {"min_f1_score": {"min_score": 0.65}},
                }
            }
        )
        self.report = self.h_spacy.generate().run().report()

    def test_report(self):
        """
        Test the evaluation report.

        This method asserts that the evaluation report generated by the `Harness` is an instance of `pd.DataFrame`.
        """

        self.assertIsInstance(self.report, pd.DataFrame)
