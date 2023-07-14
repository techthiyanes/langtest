import asyncio
import random
import re
import string
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Dict, List, Optional, Union

from langtest.modelhandler.modelhandler import ModelFactory
from langtest.utils.custom_types import SequenceClassificationSample
from .constants import (
    CONTRACTION_MAP,
    Slang_Adjectives,
    Slang_Adverbs,
    Slang_Nouns,
    TYPO_FREQUENCY,
    abbreviation_dict,
    dyslexia_map,
    ocr_typo_dict,
)
from ..utils.SoundsLikeFunctions import Search
from ..utils.custom_types import Sample, Span, Transformation
from ..utils.number_to_word import ConvertNumberToWord


class BaseRobustness(ABC):
    """Abstract base class for implementing robustness measures.

    Attributes:
        alias_name (str): A name or list of names that identify the robustness measure.

    Methods:
        transform(data: List[Sample]) -> Any: Transforms the input data into an output based on the implemented robustness measure.
    """

    alias_name = None
    supported_tasks = [
        "ner",
        "text-classification",
        "question-answering",
        "summarization",
        "translation",
    ]

    @staticmethod
    @abstractmethod
    def transform(sample_list: List[Sample]) -> List[Sample]:
        """Abstract method that implements the robustness measure.

        Args:
            sample_list (List[Sample]): The input data to be transformed.

        Returns:
            Any: The transformed data based on the implemented robustness measure.
        """
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    async def run(
        sample_list: List[Sample], model: ModelFactory, **kwargs
    ) -> List[Sample]:
        """Abstract method that implements the robustness measure.

        Args:
            sample_list (List[Sample]): The input data to be transformed.
            model (ModelFactory): The model to be used for evaluation.
            **kwargs: Additional arguments to be passed to the robustness measure.

        Returns:
            List[Sample]: The transformed data based on the implemented robustness measure.

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
        """Creates a task to run the robustness measure.

        Args:
            sample_list (List[Sample]): The input data to be transformed.
            model (ModelFactory): The model to be used for evaluation.
            **kwargs: Additional arguments to be passed to the robustness measure.

        Returns:
            asyncio.Task: The task that runs the robustness measure.

        """
        created_task = asyncio.create_task(cls.run(sample_list, model, **kwargs))
        return created_task


class UpperCase(BaseRobustness):
    """A class for transforming text samples to uppercase."""

    alias_name = "uppercase"

    @staticmethod
    def transform(sample_list: List[Sample], prob: Optional[float] = 1.0) -> List[Sample]:
        """Transform the text samples in the given sample list to uppercase.

        Args:
            sample_list (List[Sample]): A list of samples to be transformed.
            prob (Optional[float]): The probability of transforming each word to uppercase.
                Defaults to 1.0, which means all words will be transformed.

        Returns:
            List[Sample]: The transformed sample list with text samples in uppercase.
        """
        for idx, sample in enumerate(sample_list):
            if isinstance(sample, str):
                words = sample.split()
                num_transform_words = int(prob * len(words))
                transformed_indices = random.sample(
                    range(len(words)), num_transform_words
                )
                transformed_words = [
                    words[i].upper() if i in transformed_indices else words[i]
                    for i in range(len(words))
                ]
                sample_list[idx] = " ".join(transformed_words)
            else:
                words = sample.original.split()
                num_transform_words = int(prob * len(words))
                transformed_indices = random.sample(
                    range(len(words)), num_transform_words
                )
                transformed_words = [
                    words[i].upper() if i in transformed_indices else words[i]
                    for i in range(len(words))
                ]
                sample.test_case = " ".join(transformed_words)
                sample.category = "robustness"
        return sample_list


class LowerCase(BaseRobustness):
    """A class for transforming text samples to lowercase."""

    alias_name = "lowercase"

    @staticmethod
    def transform(sample_list: List[Sample], prob: Optional[float] = 1.0) -> List[Sample]:
        """Transform the text samples in the given sample list to lowercase.

        Args:
            sample_list (List[Sample]): A list of samples to be transformed.
            prob (Optional[float]): The probability of transforming each word to lowercase.
                                    Defaults to 1.0, which means all words will be transformed.

        Returns:
            List[Sample]: The transformed sample list with text samples in lowercase.
        """
        for idx, sample in enumerate(sample_list):
            if isinstance(sample, str):
                words = sample.split()
                num_transform_words = int(prob * len(words))
                transformed_indices = random.sample(
                    range(len(words)), num_transform_words
                )
                transformed_words = [
                    words[i].lower() if i in transformed_indices else words[i]
                    for i in range(len(words))
                ]
                sample_list[idx] = " ".join(transformed_words)
            else:
                words = sample.original.split()
                num_transform_words = int(prob * len(words))
                transformed_indices = random.sample(
                    range(len(words)), num_transform_words
                )
                transformed_words = [
                    words[i].lower() if i in transformed_indices else words[i]
                    for i in range(len(words))
                ]
                sample.test_case = " ".join(transformed_words)
                sample.category = "robustness"
        return sample_list


class TitleCase(BaseRobustness):
    """A class for transforming text samples to titlecase."""

    alias_name = "titlecase"

    @staticmethod
    def transform(sample_list: List[Sample], prob: Optional[float] = 1.0) -> List[Sample]:
        """Transform the text samples in the given sample list to title case.

        Args:
            sample_list (List[Sample]): A list of samples to be transformed.
            prob (Optional[float]): The probability of transforming each word to title case.
                                    Defaults to 1.0, which means all words will be transformed.

        Returns:
            List[Sample]: The transformed sample list with text samples in title case.
        """
        for idx, sample in enumerate(sample_list):
            if isinstance(sample, str):
                words = sample.split()
                num_transform_words = int(prob * len(words))
                transformed_indices = random.sample(
                    range(len(words)), num_transform_words
                )
                transformed_words = [
                    words[i].title() if i in transformed_indices else words[i]
                    for i in range(len(words))
                ]
                sample_list[idx] = " ".join(transformed_words)
            else:
                words = sample.original.split()
                num_transform_words = int(prob * len(words))
                transformed_indices = random.sample(
                    range(len(words)), num_transform_words
                )
                transformed_words = [
                    words[i].title() if i in transformed_indices else words[i]
                    for i in range(len(words))
                ]
                sample.test_case = " ".join(transformed_words)
                sample.category = "robustness"
        return sample_list


class AddPunctuation(BaseRobustness):
    """A class for adding punctuation to text samples."""

    alias_name = "add_punctuation"

    @staticmethod
    def transform(
        sample_list: List[Sample],
        prob: Optional[float] = 1.0,
        whitelist: Optional[List[str]] = None,
        count: int = 1,
    ) -> List[Sample]:
        """Add punctuation at the end of the string, if there is punctuation at the end skip it

        Args:
            sample_list (List[Sample]): A list of samples to be transformed.
            prob (Optional[float]): The probability of adding punctuation to each sample.
                                    Defaults to 1.0, which means all words will be transformed.
            whitelist (Optional[List[str]]): A list of punctuation characters to consider when adding punctuation.
                If None, the default whitelist ['!', '?', ',', '.', '-', ':', ';'] will be used. Defaults to None.
            count: Number of variations to create.

        Returns:
            List[Sample]: The transformed sample list with added punctuation.
        """
        if whitelist is None:
            whitelist = ["!", "?", ",", ".", "-", ":", ";"]

        def check_whitelist(text, whitelist):
            if text[-1] not in whitelist:
                chosen_punc = random.choice(whitelist)
                return text + chosen_punc
            else:
                return text

        perturbed_samples = []

        for s in sample_list:
            sample = deepcopy(s)
            for i in range(count):
                if isinstance(sample, str):
                    if random.random() < prob:
                        perturbed_samples.append(check_whitelist(sample, whitelist))
                else:
                    if sample.original[-1] not in whitelist and (random.random() < prob):
                        chosen_punc = random.choice(whitelist)
                        sample.test_case = sample.original + chosen_punc
                        if sample.task in ("ner", "text-classification"):
                            sample.transformations = [
                                Transformation(
                                    original_span=Span(
                                        start=len(sample.original),
                                        end=len(sample.original),
                                        word="",
                                    ),
                                    new_span=Span(
                                        start=len(sample.original),
                                        end=len(sample.test_case),
                                        word=chosen_punc,
                                    ),
                                    ignore=True,
                                )
                            ]
                    else:
                        sample.test_case = sample.original
                    sample.category = "robustness"
                    perturbed_samples.append(sample)
        return perturbed_samples


class StripPunctuation(BaseRobustness):
    """A class for stripping punctuation to text samples."""

    alias_name = "strip_punctuation"

    @staticmethod
    def transform(
        sample_list: List[Sample],
        prob: Optional[float] = 1.0,
        whitelist: Optional[List[str]] = None,
    ) -> List[Sample]:
        """Strip punctuation from the text samples in the given sample list.

        Args:
            sample_list (List[Sample]): A list of samples to be transformed.
            prob (Optional[float]): The probability of stripping punctuation from each sample.
                                    Defaults to 1.0, which means all words will be transformed.
            whitelist (Optional[List[str]]): A list of punctuation characters to consider when stripping punctuation.
                If None, the default whitelist ['!', '?', ',', '.', '-', ':', ';'] will be used. Defaults to None.

        Returns:
            List[Sample]: The transformed sample list with punctuation stripped.
        """
        if whitelist is None:
            whitelist = ["!", "?", ",", ".", "-", ":", ";"]

        def check_whitelist(text, whitelist):
            if text[-1] in whitelist:
                return text[:-1]
            else:
                return text

        for idx, sample in enumerate(sample_list):
            if isinstance(sample, str):
                if random.random() < prob:
                    sample_list[idx] = check_whitelist(sample, whitelist)
            else:
                if sample.original[-1] in whitelist and (random.random() < prob):
                    sample.test_case = sample.original[:-1]
                    if sample.task in ("ner", "text-classification"):
                        sample.transformations = [
                            Transformation(
                                original_span=Span(
                                    start=len(sample.original) - 1,
                                    end=len(sample.original),
                                    word=sample.original[-1:],
                                ),
                                new_span=Span(
                                    start=len(sample.test_case),
                                    end=len(sample.test_case),
                                    word="",
                                ),
                                ignore=True,
                            )
                        ]
                else:
                    sample.test_case = sample.original
                sample.category = "robustness"
        return sample_list


class AddTypo(BaseRobustness):
    """A class for adding typos to text samples."""

    alias_name = "add_typo"

    @staticmethod
    def transform(
        sample_list: List[Sample], prob: Optional[float] = 1.0, count: int = 1
    ) -> List[Sample]:
        """Add typos to the text samples in the given sample list.

        Args:
            sample_list (List[Sample]): A list of samples to be transformed.
            prob (Optional[float]): The probability of adding a typo to each sample.
                                    Defaults to 1.0, which means all words will be transformed.

            count: Number of variations to create.

        Returns:
            List[Sample]: The transformed sample list with added typos.
        """

        def keyboard_typo(string):
            if prob is not None and random.random() >= prob:
                return string

            if len(string) < 5:
                return string
            string = list(string)
            if random.random() > 0.1:
                idx_list = list(range(len(TYPO_FREQUENCY)))
                char_list = list(TYPO_FREQUENCY.keys())

                counter, idx = 0, -1
                while counter < 10 and idx == -1:
                    idx = random.randint(0, len(string) - 1)
                    char = string[idx]
                    if TYPO_FREQUENCY.get(char.lower(), None):
                        char_frequency = TYPO_FREQUENCY[char.lower()]

                        if sum(char_frequency) > 0:
                            chosen_char = random.choices(idx_list, weights=char_frequency)
                            difference = ord(char.lower()) - ord(
                                char_list[chosen_char[0]]
                            )
                            char = chr(ord(char) - difference)
                            string[idx] = char
                    else:
                        idx = -1
                        counter += 1
            else:
                string = list(string)
                swap_idx = random.randint(0, len(string) - 2)
                tmp = string[swap_idx]
                string[swap_idx] = string[swap_idx + 1]
                string[swap_idx + 1] = tmp
            return "".join(string)

        perturbed_samples = []
        for sample in sample_list:
            for i in range(count):
                if isinstance(sample, str):
                    perturbed_samples.append(keyboard_typo(sample))
                else:
                    s = deepcopy(sample)
                    s.category = "robustness"
                    s.test_case = keyboard_typo(sample.original)
                    perturbed_samples.append(s)

        return perturbed_samples


class SwapEntities(BaseRobustness):
    """A class for swapping entities in text samples."""

    alias_name = "swap_entities"
    supported_tasks = ["ner"]

    @staticmethod
    def transform(
        sample_list: List[Sample],
        prob: Optional[float] = 1.0,
        labels: List[List[str]] = None,
        terminology: Dict[str, List[str]] = None,
        count: int = 1,
    ) -> List[Sample]:
        """Swap entities in the text samples of the given sample list.

        Args:
            sample_list (List[Sample]): A list of samples to be transformed.
            prob (Optional[float]): The probability of swapping entities in each sample.
                                    Defaults to 1.0, which means all eligible samples will have their entities swapped.
            labels (List[List[str]]):  Corresponding labels to make changes according to sentences.
            terminology (Dict[str, List[str]]): Dictionary of entities and corresponding list of words.

        Returns:
            List[Sample]: The transformed sample list with entities swapped.
        """
        if terminology is None:
            raise ValueError(
                "In order to generate test cases for swap_entities, terminology should be passed!"
            )

        if labels is None:
            raise ValueError(
                "In order to generate test cases for swap_entities, labels should be passed!"
            )

        assert len(sample_list) == len(
            labels
        ), "'labels' and 'sample_list' must have same lengths."

        perturbed_samples = []
        for s, sample_labels in zip(sample_list, labels):
            for i in range(count):
                sample = deepcopy(s)
                sample.category = "robustness"
                if all([label == "O" for label in sample_labels]):
                    sample.test_case = sample.original
                    continue

                sent_tokens = sample.original.split(" ")

                ent_start_pos = [1 if label[0] == "B" else 0 for label in sample_labels]
                ent_idx = [i for i, value in enumerate(ent_start_pos) if value == 1]

                replace_idx = random.choice(ent_idx)
                ent_type = sample_labels[replace_idx][2:]
                replace_idxs = [replace_idx]
                if replace_idx < len(sample_labels) - 1:
                    for i, label in enumerate(sample_labels[replace_idx + 1 :]):
                        if label == f"I-{ent_type}":
                            replace_idxs.append(i + replace_idx + 1)
                        else:
                            break

                replace_token = sent_tokens[replace_idx : replace_idx + len(replace_idxs)]
                replace_token = " ".join(replace_token)

                chosen_ent = random.choice(terminology[ent_type])

                if random.random() < prob:
                    replace_token_pos = re.search(replace_token, sample.original)
                    sample.test_case = sample.original.replace(replace_token, chosen_ent)
                    if sample.task in ("ner", "text-classification"):
                        sample.transformations = [
                            Transformation(
                                original_span=Span(
                                    start=replace_token_pos.start(),
                                    end=replace_token_pos.end(),
                                    word=replace_token,
                                ),
                                new_span=Span(
                                    start=replace_token_pos.start(),
                                    end=replace_token_pos.start() + len(chosen_ent),
                                    word=chosen_ent,
                                ),
                                ignore=False,
                            )
                        ]
                else:
                    sample.test_case = sample.original
                perturbed_samples.append(sample)

        return perturbed_samples


class ConvertAccent(BaseRobustness):
    """A class for converting accents in text samples."""

    alias_name = ["american_to_british", "british_to_american"]

    @staticmethod
    def transform(
        sample_list: List[Sample],
        prob: Optional[float] = 1.0,
        accent_map: Dict[str, str] = None,
    ) -> List[Sample]:
        """Converts accents in the input sentences using a conversion dictionary.

        Args:
            sample_list (List[Sample]): A list of samples to be transformed.
            prob (Optional[float]): The probability of applying accent conversion to each sample.
                                    Defaults to 1.0, which means all samples will have accents converted.
            accent_map (Dict[str, str]): A dictionary with conversion terms mapping source accents to target accents.

        Returns:
            List[Sample]: The transformed sample list with accents converted.
        """

        def convert_accent(string: str, accent_map: Dict[str, str]) -> str:
            tokens = set(string.split(" "))
            replaced_string = string
            transformations = []

            for i, token in enumerate(tokens):
                if random.random() < prob:
                    new_token = accent_map.get(token.lower(), token)
                    if new_token != token:
                        diff_len = len(new_token) - len(token)
                        nb_occurrences = len(re.findall(token, replaced_string))

                        for c in range(nb_occurrences):
                            span = re.search(token, replaced_string)
                            replaced_string = re.sub(
                                token, new_token, replaced_string, count=1
                            )

                            transformations.append(
                                Transformation(
                                    original_span=Span(
                                        start=span.start(), end=span.end(), word=token
                                    ),
                                    new_span=Span(
                                        start=span.start(),
                                        end=span.end() + diff_len,
                                        word=new_token,
                                    ),
                                    ignore=False,
                                )
                            )
            return replaced_string, transformations

        for idx, sample in enumerate(sample_list):
            if isinstance(sample, str):
                sample_list[idx], _ = convert_accent(sample, accent_map)
            else:
                if sample.task in ("ner", "text-classification"):
                    sample.test_case, sample.transformations = convert_accent(
                        sample.original, accent_map
                    )
                else:
                    sample.test_case, _ = convert_accent(sample.original, accent_map)
                sample.category = "robustness"

        return sample_list


class AddContext(BaseRobustness):
    """A class for adding context to text samples."""

    alias_name = "add_context"

    @staticmethod
    def transform(
        sample_list: List[Sample],
        prob: Optional[float] = 1.0,
        starting_context: Optional[List[str]] = None,
        ending_context: Optional[List[str]] = None,
        strategy: str = None,
        count: int = 1,
    ) -> List[Sample]:
        """Adds context to the input sentences.

        Args:
            sample_list (List[Sample]): A list of samples to be transformed.
            prob (Optional[float]): The probability of adding context to each sample.
                                     Defaults to 1.0, which means all samples will have context added.
            starting_context (Optional[List[str]]): A list of terms (context) to be added at the start of sentences.
            ending_context (Optional[List[str]]): A list of terms (context) to be added at the end of sentences.
            strategy (str): Config method to adjust where the context tokens are added. Options: 'start', 'end', or 'combined'.
            count: Number of variations to create.

        Returns:
            List[Sample]: The transformed sample list with context added.
        """

        def context(text, strategy):
            possible_methods = ["start", "end", "combined"]
            if strategy is None:
                strategy = random.choice(possible_methods)
            elif strategy not in possible_methods:
                raise ValueError(
                    f"Add context strategy must be one of 'start', 'end', 'combined'. Cannot be {strategy}."
                )

            transformations = []

            if strategy == "start" or strategy == "combined":
                if random.random() < prob:
                    add_tokens = random.choice(starting_context)
                    add_string = (
                        " ".join(add_tokens)
                        if isinstance(add_tokens, list)
                        else add_tokens
                    )
                    if text != "-":
                        text = add_string + " " + text
                        transformations.append(
                            Transformation(
                                original_span=Span(start=0, end=0, word=""),
                                new_span=Span(
                                    start=0, end=len(add_string) + 1, word=add_string
                                ),
                                ignore=True,
                            )
                        )

            if strategy == "end" or strategy == "combined":
                if random.random() < prob:
                    add_tokens = random.choice(ending_context)
                    add_string = (
                        " ".join(add_tokens)
                        if isinstance(add_tokens, list)
                        else add_tokens
                    )
                    if text != "-":
                        text = text + " " + add_string
                        transformations.append(
                            Transformation(
                                original_span=Span(
                                    start=len(text) - 1, end=len(text), word=""
                                ),
                                new_span=Span(
                                    start=len(text),
                                    end=len(text) + len(add_string) + 1,
                                    word=add_string,
                                ),
                                ignore=True,
                            )
                        )

            return text, transformations

        perturbed_samples = []
        for s in sample_list:
            for i in range(count):
                sample = deepcopy(s)
                if isinstance(sample, str):
                    sample, _ = context(sample, strategy)
                else:
                    if sample.task in ("ner", "text-classification"):
                        sample.test_case, sample.transformations = context(
                            sample.original, strategy
                        )
                    else:
                        sample.test_case, _ = context(sample.original, strategy)

                    sample.category = "robustness"
                perturbed_samples.append(sample)
        return perturbed_samples


class AddContraction(BaseRobustness):
    """A class for adding contractions to text samples."""

    alias_name = "add_contraction"

    @staticmethod
    def transform(sample_list: List[Sample], prob: Optional[float] = 1.0) -> List[Sample]:
        """Adds contractions to the input sentences.

        Args:
            sample_list (List[Sample]): A list of samples to be transformed.
            prob (Optional[float]): The probability of adding contractions to each sample.
                                    Defaults to 1.0, which means all samples will have context added.

        Returns:
            List[Sample]: The transformed sample list with contractions added.
        """

        def custom_replace(match):
            """Regex replace for contraction."""
            token = match.group(0)
            contracted_token = CONTRACTION_MAP.get(
                token, CONTRACTION_MAP.get(token.lower())
            )

            is_upper_case = token[0]
            expanded_contraction = is_upper_case + contracted_token[1:]
            return expanded_contraction

        def search_contraction(text):
            replaced_string = text
            for contraction in CONTRACTION_MAP:
                search = re.search(contraction, text, flags=re.IGNORECASE | re.DOTALL)
                if search and (random.random() < prob):
                    new_string = CONTRACTION_MAP.get(search.group(), search.group())
                    replaced_string = re.sub(
                        contraction,
                        custom_replace,
                        new_string,
                        flags=re.IGNORECASE | re.DOTALL,
                    )

            return replaced_string

        for idx, sample in enumerate(sample_list):
            if isinstance(sample, str):
                sample_list[idx] = search_contraction(sample)
            else:
                replaced_string = sample.original
                transformations = []

                for contraction in CONTRACTION_MAP:
                    search = re.search(
                        contraction, sample.original, flags=re.IGNORECASE | re.DOTALL
                    )
                    if search and (random.random() < prob):
                        new_string = CONTRACTION_MAP.get(search.group(), search.group())

                        diff_len = len(new_string) - len(search.group())
                        replaced_string = re.sub(
                            contraction,
                            custom_replace,
                            replaced_string,
                            flags=re.IGNORECASE | re.DOTALL,
                        )
                        if sample.task in ("ner", "text-classification"):
                            transformations.append(
                                Transformation(
                                    original_span=Span(
                                        start=search.start(),
                                        end=search.end(),
                                        word=search.group(),
                                    ),
                                    new_span=Span(
                                        start=search.start(),
                                        end=search.end() + diff_len,
                                        word=new_string,
                                    ),
                                    ignore=False,
                                )
                            )
                sample.test_case = replaced_string
                if sample.task in ("ner", "text-classification"):
                    sample.transformations = transformations
                sample.category = "robustness"
        return sample_list


class DyslexiaWordSwap(BaseRobustness):
    """A class for simulating dyslexic word swapping."""

    alias_name = "dyslexia_word_swap"

    @staticmethod
    def transform(sample_list: List[Sample], prob: Optional[float] = 1.0) -> List[Sample]:
        """Converts the input sentences by changing some similar words from the dyslexia map and outputs a new string.

        Args:
            sample_list (List[Sample]): A list of samples to be transformed.
            prob (Optional[float]): The probability of adding dyslexia words to each sample.
                                    Defaults to 1.0, which means all samples will be transformed.

        Returns:
            List[Sample]: The transformed sample list with dyslexia words added.
        """

        def dyslexia_word_swap(text):
            transformations = []

            def replace_word(match):
                original_word = match.group()
                transformed_word = dyslexia_map.get(original_word, original_word)
                if transformed_word != original_word and (random.random() < prob):
                    transformations.append(
                        Transformation(
                            original_span=Span(
                                start=match.start(), end=match.end(), word=original_word
                            ),
                            new_span=Span(
                                start=match.start(),
                                end=match.start() + len(transformed_word),
                                word=transformed_word,
                            ),
                            ignore=False,
                        )
                    )
                    return transformed_word
                return original_word

            pattern = r"\b\w+\b"  # Matches whole words using word boundaries
            transformed_text = re.sub(pattern, replace_word, text)

            return transformed_text, transformations

        for idx, sample in enumerate(sample_list):
            if isinstance(sample, str):
                sample_list[idx], _ = dyslexia_word_swap(sample)
            else:
                sample.test_case, transformations = dyslexia_word_swap(sample.original)
                if sample.task in ("ner", "text-classification"):
                    sample.transformations = transformations
                sample.category = "robustness"

        return sample_list


class NumberToWord(BaseRobustness):
    """A class for converting numbers to words."""

    alias_name = "number_to_word"
    num = ConvertNumberToWord()

    @staticmethod
    def transform(sample_list: List[Sample], prob: Optional[float] = 1.0) -> List[Sample]:
        """Converts numbers in the input text to their word representations.

        Args:
            sample_list (List[Sample]): A list of samples to be transformed.
            prob (Optional[float]): The probability of converting numbers to words in each sample.
                                    Defaults to 1.0, which means all samples will be transformed.

        Returns:
            List[Sample]: The transformed sample list.
        """

        def convert_numbers(regex, text):
            results = []
            trans = []
            transformations = []
            start_offset = 0

            for match in re.finditer(regex, text):
                token = match.group()
                words = NumberToWord.num.number_to_words(token, wantlist=True)
                new_words_len = len(" ".join(words))
                trans.append(text[start_offset : match.start()])
                if random.random() < prob:
                    trans.append(" ".join(words))
                    transformations.append(
                        Transformation(
                            original_span=Span(
                                start=match.start(), end=match.end(), word=token
                            ),
                            new_span=Span(
                                start=match.start(),
                                end=match.start() + new_words_len,
                                word=" ".join(words),
                            ),
                            ignore=False,
                        )
                    )
                else:
                    trans.append(token)
                start_offset = match.end()

            trans.append(text[start_offset:])
            results.append("".join(trans))
            return "".join(results), transformations

        for idx, sample in enumerate(sample_list):
            if isinstance(sample, str):
                sample_list[idx], _ = convert_numbers(
                    r"(?<!\S)(\d+(\.\d+)?)(?=(\s|\n|$))", sample
                )
            else:
                sample.test_case, transformations = convert_numbers(
                    r"(?<!\S)(\d+(\.\d+)?)(?=(\s|\n|$))", sample.original
                )
                if sample.task in ("ner", "text-classification"):
                    sample.transformations = transformations
                sample.category = "robustness"
        return sample_list


class AddOcrTypo(BaseRobustness):
    """A class for adding OCR typos to the input text."""

    alias_name = "add_ocr_typo"

    @staticmethod
    def transform(
        sample_list: List[Sample], prob: Optional[float] = 1.0, count: int = 1
    ) -> List[Sample]:
        """Add OCR typos to the input samples.

        Args:
            sample_list (List[Sample]): A list of samples to be transformed.
            prob (Optional[float]): The probability of adding OCR typos to each sample.
                                    Defaults to 1.0, which means all samples will be transformed.
            count: Number of variations to create.

        Returns:
            List[Sample]: The transformed sample list with ocr typos added
        """

        def ocr_typo(regex, text):
            results = []
            trans = []
            transformations = []
            start_offset = 0

            for match in re.finditer(regex, text):
                token = match.group()
                corrected_token = None

                possible_corrections = [
                    key for key, value in ocr_typo_dict.items() if value == token
                ]
                if possible_corrections:
                    corrected_token = random.choice(possible_corrections)
                else:
                    corrected_token = token

                if corrected_token != token and (random.random() < prob):
                    trans.append(text[start_offset : match.start()])
                    trans.append(corrected_token)
                    start_offset = match.end()
                    transformations.append(
                        Transformation(
                            original_span=Span(
                                start=match.start(), end=match.end(), word=token
                            ),
                            new_span=Span(
                                start=match.start(),
                                end=match.start() + len(corrected_token),
                                word=corrected_token,
                            ),
                            ignore=False,
                        )
                    )
                else:
                    trans.append(text[start_offset : match.end()])
                    start_offset = match.end()

            trans.append(text[start_offset:])
            results.append("".join(trans))

            return "".join(results), transformations

        perturbed_samples = []
        for s in sample_list:
            for i in range(count):
                sample = deepcopy(s)
                if isinstance(sample, str):
                    sample, _ = ocr_typo(r"[^,\s.!?]+", sample)
                else:
                    sample.test_case, transformations = ocr_typo(
                        r"[^,\s.!?]+", sample.original
                    )
                    if sample.task in ("ner", "text-classification"):
                        sample.transformations = transformations
                    sample.category = "robustness"
                perturbed_samples.append(sample)
        return perturbed_samples


class AbbreviationInsertion(BaseRobustness):
    """A class for adding abbreviations to the input text."""

    alias_name = "add_abbreviation"

    @staticmethod
    def transform(sample_list: List[Sample], prob: Optional[float] = 1.0) -> List[Sample]:
        """Transforms the given sample list by inserting abbreviations.

        Args:
            sample_list (List[Sample]): The list of samples to transform.
            prob (Optional[float]): The probability controlling the proportion of words to be perturbed.
                                    Defaults to 1.0, which means all samples will be transformed.

        Returns:
            List[Sample]: The transformed list of samples with abbreviations added
        """

        def insert_abbreviation(text):
            perturbed_text = text
            transformations = []

            for abbreviation, expansions in abbreviation_dict.items():
                for expansion in expansions:
                    pattern = r"(?i)\b" + re.escape(expansion) + r"\b"
                    corrected_token = abbreviation
                    matches = re.finditer(pattern, text)
                    for match in matches:
                        start = match.start()
                        end = match.end()
                        token = text[start:end]
                        if corrected_token != token and (random.random() < prob):
                            perturbed_text = (
                                perturbed_text[:start]
                                + corrected_token
                                + perturbed_text[end:]
                            )
                            transformations.append(
                                Transformation(
                                    original_span=Span(start=start, end=end, word=token),
                                    new_span=Span(
                                        start=start,
                                        end=start + len(corrected_token),
                                        word=corrected_token,
                                    ),
                                    ignore=False,
                                )
                            )

            return perturbed_text, transformations

        for idx, sample in enumerate(sample_list):
            if isinstance(sample, str):
                sample_list[idx], _ = insert_abbreviation(sample)
            else:
                sample.test_case, transformations = insert_abbreviation(sample.original)
                if sample.task in ("ner", "text-classification"):
                    sample.transformations = transformations
                sample.category = "robustness"

        return sample_list


class AddSpeechToTextTypo(BaseRobustness):
    """A class for adding common speech to text typos to the input text."""

    alias_name = "add_speech_to_text_typo"

    @staticmethod
    def transform(
        sample_list: List[Sample], prob: Optional[float] = 1.0, count: int = 1
    ) -> List[Sample]:
        """Transforms the given sample list by introducing typos simulating speech-to-text errors.

        Args:
            sample_list (List[Sample]): The list of samples to transform.
            prob (Optional[float]): The probability controlling the proportion of words to be perturbed.
                                    Defaults to 1.0, which means all samples will be transformed.
            count: Number of variations to create.

        Returns:
            List[Sample]: The transformed list of samples with speech to text typos added.
        """

        def convertToSimilarHarmony(sentence):
            words = re.findall(r"\w+(?:'\w+)*|\W", sentence)
            converted_sentence = []
            transformations = []
            index_offset = 0

            for word in words:
                if word.isspace() or all(ch in string.punctuation for ch in word):
                    converted_sentence.append(
                        word
                    )  # Preserve space and punctuation in the reconstructed sentence
                else:
                    try:
                        similar_words = Search.perfectHomophones(word)
                        if similar_words:
                            original_case = word[0].isupper()
                            similar_word = random.choice(similar_words)
                            if original_case and similar_word[0].islower():
                                similar_word = similar_word.capitalize()
                            elif not original_case and similar_word[0].isupper():
                                similar_word = similar_word.lower()

                            if similar_word.lower() == word.lower():
                                similar_word = word

                            if similar_word != word and (random.random() < prob):
                                start_index = sentence.index(word, index_offset)
                                end_index = start_index + len(word)
                                converted_sentence.append(similar_word)
                                new_word_length = len(similar_word)
                                transformations.append(
                                    Transformation(
                                        original_span=Span(
                                            start=start_index, end=end_index, word=word
                                        ),
                                        new_span=Span(
                                            start=start_index,
                                            end=start_index + new_word_length,
                                            word=similar_word,
                                        ),
                                        ignore=False,
                                    )
                                )
                                index_offset = end_index
                            else:
                                converted_sentence.append(word)

                        else:
                            converted_sentence.append(word)

                    except ValueError:
                        converted_sentence.append(word)

            perturbed_text = "".join(converted_sentence)

            return perturbed_text, transformations

        perturbed_samples = []
        for s in sample_list:
            for i in range(count):
                sample = deepcopy(s)
                if isinstance(sample, str):
                    sample, _ = convertToSimilarHarmony(sample)
                else:
                    sample.test_case, transformations = convertToSimilarHarmony(
                        sample.original
                    )
                    if sample.task in ("ner", "text-classification"):
                        sample.transformations = transformations
                    sample.category = "robustness"
                perturbed_samples.append(sample)
        return perturbed_samples


class AddSlangifyTypo(BaseRobustness):
    """A class for adding slangs to text typos to the input text."""

    alias_name = "add_slangs"

    @staticmethod
    def transform(sample_list: List[Sample], prob: Optional[float] = 1.0) -> List[Sample]:
        """Transforms the given sample list by adding slang words.

        Args:
            sample_list (List[Sample]): The list of samples to transform.
            prob (Optional[float]): The probability controlling the proportion of words to be perturbed.
                                    Defaults to 1.0, which means all samples will be transformed.

        Returns:
            List[Sample]: The transformed list of samples with slangs added.
        """

        def slangify_typo(text):
            slang_words = [
                list(map(list, zip(*Slang_Nouns))),
                list(map(list, zip(*Slang_Adverbs))),
                list(map(list, zip(*Slang_Adjectives))),
            ]

            modified_toks = []
            tokens = re.findall(
                r"\w+(?:[-']\w+)*|[^\w\s]|[\s]+", text
            )  # Include hyphenated and possessive words as single tokens
            transformations = []
            start_offset = 0

            for token in tokens:
                if token.isspace() or all(ch in string.punctuation for ch in token):
                    modified_toks.append(
                        token
                    )  # Preserve space and punctuation in the reconstructed text
                    continue
                is_cap = token[0].isupper()
                replaced = False

                for slang in slang_words:
                    if token.lower() in slang[0]:
                        replacements = [
                            i for i, x in enumerate(slang[0]) if x == token.lower()
                        ]
                        chosen_index = random.choice(replacements)
                        temp = slang[1][chosen_index]

                        if is_cap:
                            temp = temp[0].upper() + temp[1:]

                        if temp != token and (random.random() < prob):
                            start_index = text.index(token, start_offset)
                            end_index = start_index + len(token)
                            modified_toks.append(temp)
                            new_word_length = len(temp)
                            transformations.append(
                                Transformation(
                                    original_span=Span(
                                        start=start_index, end=end_index, word=token
                                    ),
                                    new_span=Span(
                                        start=start_index,
                                        end=start_index + new_word_length,
                                        word=temp,
                                    ),
                                    ignore=False,
                                )
                            )
                            start_offset = end_index
                        else:
                            modified_toks.append(token)

                        replaced = True
                        break

                if not replaced:
                    modified_toks.append(token)

            modified_text = "".join(modified_toks)

            return modified_text, transformations

        for idx, sample in enumerate(sample_list):
            if isinstance(sample, str):
                sample_list[idx], _ = slangify_typo(sample)
            else:
                sample.test_case, transformations = slangify_typo(sample.original)
                if sample.task in ("ner", "text-classification"):
                    sample.transformations = transformations
                sample.category = "robustness"

        return sample_list


class MultiplePerturbations(BaseRobustness):
    """A class for applying multiple perturbations to transform a sample list."""

    alias_name = "multiple_perturbations"

    @staticmethod
    def transform(
        sample_list: List[Sample],
        perturbations: List[str],
        prob: Optional[float] = 1.0,
        config=None,
    ) -> List[Sample]:
        """Transforms the given sample list by applying multiple perturbations.

        Args:
            sample_list (List[Sample]): The list of samples to transform.
            perturbations (List[str]): The list of perturbations to apply.
            prob (Optional[float]): The probability controlling the proportion of words to be perturbed.
                                    Defaults to 1.0, which means all samples will be transformed.

        Returns:
            transformed_list: The transformed list of samples.
        """

        def apply_transformation(sample, order, prob):
            if order == "uppercase":
                transformed_list = UpperCase.transform(sample, prob)
            elif order == "lowercase":
                transformed_list = LowerCase.transform(sample, prob)
            elif order == "titlecase":
                transformed_list = TitleCase.transform(sample, prob)
            elif order == "add_punctuation":
                transformed_list = AddPunctuation.transform(sample, prob)
            elif order == "strip_punctuation":
                transformed_list = StripPunctuation.transform(sample, prob)
            elif order == "add_typo":
                transformed_list = AddTypo.transform(sample, prob)
            elif order == "american_to_british":
                transformed_list = ConvertAccent.transform(
                    sample,
                    prob,
                    **config.get("american_to_british", {}).get("parameters", {}),
                )
            elif order == "british_to_american":
                transformed_list = ConvertAccent.transform(
                    sample,
                    prob,
                    **config.get("british_to_american", {}).get("parameters", {}),
                )
            elif next(iter(order)) == "add_context":
                transformed_list = AddContext.transform(
                    sample,
                    prob,
                    order["add_context"]["parameters"]["starting_context"],
                    order["add_context"]["parameters"]["ending_context"],
                )
            elif order == "add_contraction":
                transformed_list = AddContraction.transform(sample, prob)
            elif order == "dyslexia_word_swap":
                transformed_list = DyslexiaWordSwap.transform(sample, prob)
            elif order == "number_to_word":
                transformed_list = NumberToWord.transform(sample, prob)
            elif order == "add_abbreviation":
                transformed_list = AbbreviationInsertion.transform(sample, prob)
            elif order == "add_ocr_typo":
                transformed_list = AddOcrTypo.transform(sample, prob)
            elif order == "add_speech_to_text_typo":
                transformed_list = AddSpeechToTextTypo.transform(sample, prob)
            elif order == "add_slangs":
                transformed_list = AddSlangifyTypo.transform(sample, prob)
            else:
                raise ValueError(f"Unknown transformation: {order}")
            return transformed_list

        if isinstance(sample_list[0], SequenceClassificationSample):
            for idx, transformation in enumerate(perturbations):
                if idx == 0:
                    transformed_list = apply_transformation(
                        sample_list, transformation, prob
                    )
                else:
                    new_list = []
                    for sample in transformed_list:
                        new_sample = SequenceClassificationSample(
                            original=sample.test_case,
                            category="robustness",
                            expected_results=sample.expected_results,
                        )
                        new_list.append(new_sample)
                    transformed_list = apply_transformation(
                        new_list, perturbations[idx], prob
                    )

            for i, sample in enumerate(transformed_list):
                sample.original = sample_list[i].original
                sample.transformations = None

        elif isinstance(sample_list[0], str):
            for idx, transformation in enumerate(perturbations):
                transformed_list = apply_transformation(sample_list, transformation, prob)

        return transformed_list


class StripAllPunctuation(BaseRobustness):
    """A class for stripping punctuation to text samples."""

    alias_name = "strip_punctuation_all"

    @staticmethod
    def transform(
        sample_list: List[Union[Sample, str]],
        prob: Optional[float] = 1.0,
        whitelist: Optional[List[str]] = None,
    ) -> List[Sample]:
        """Transforms the given sample list by stripping all punctuations.

        Args:
            sample_list (List[Union[Sample, str]]): The list of samples to transform.
            prob (Optional[float]): The probability controlling the proportion of samples to be perturbed.
                                    Defaults to 1.0, which means all samples will be transformed
            whitelist (Optional[List[str]]): punctuations to look for.

        Returns:
            transformed_list: The transformed list of samples.
        """
        if whitelist is None:
            whitelist = ["!", "?", ",", ".", "-", ":", ";", "/", "'", '"']

        exceptions = ["s/p", "h/o"]
        letter_letter_pattern = r"\b\w/\w\b"
        decimal_number_pattern = r"\b\d+\.\d+\b"

        exceptions_pattern = "|".join(
            [
                f"(?<!{ex.split('/')[0]})/(?!{ex.split('/')[1]})"
                for ex in exceptions
                if "/" in ex
            ]
        )
        whitelist_pattern = "|".join(
            [f"\\{char}" for char in whitelist if char not in ["/", "."]]
        )

        pattern = "|".join(
            [
                decimal_number_pattern,  # to handle decimal numbers
                exceptions_pattern,
                whitelist_pattern,
                letter_letter_pattern,  # to handle letter/letter
                "(?<!\\d)\\.(?!\\d)",  # to handle non-decimal periods
            ]
        )

        def check_whitelist(text):
            new_text = text
            transformations = []
            offset = 0
            for match in re.finditer(pattern, new_text):
                if (
                    re.match(letter_letter_pattern, match.group())
                    and match.group() not in exceptions
                ):
                    transformations.append(
                        Transformation(
                            original_span=Span(
                                start=match.start() - offset,
                                end=match.end() - offset,
                                word=match.group(),
                            ),
                            new_span=Span(
                                start=match.start() - offset,
                                end=match.start() - offset + 5,
                                word=" and ",
                            ),
                        )
                    )
                    new_text = (
                        new_text[: match.start() - offset]
                        + " and "
                        + new_text[match.end() - offset :]
                    )
                    offset += 1
                elif not re.match(
                    decimal_number_pattern, match.group()
                ):  # Avoid removing punctuation from decimal numbers
                    transformations.append(
                        Transformation(
                            original_span=Span(
                                start=match.start() - offset,
                                end=match.end() - offset,
                                word=match.group(),
                            ),
                            new_span=Span(
                                start=match.start() - offset,
                                end=match.start() - offset,
                                word="",
                            ),
                        )
                    )
                    new_text = (
                        new_text[: match.start() - offset]
                        + new_text[match.end() - offset :]
                    )
                    offset += len(match.group())

            return new_text, transformations

        for idx, sample in enumerate(sample_list):
            if isinstance(sample, str):
                if random.random() < prob:
                    transformed_text, transformations = check_whitelist(sample)
                    sample_list[idx] = transformed_text
                if random.random() < prob:
                    transformed_text, transformations = check_whitelist(sample.original)
                    sample.test_case = transformed_text
                    if sample.task in ("ner", "text-classification"):
                        sample.transformations = transformations
                else:
                    sample.test_case = sample.original
                sample.category = "robustness"

        return sample_list
