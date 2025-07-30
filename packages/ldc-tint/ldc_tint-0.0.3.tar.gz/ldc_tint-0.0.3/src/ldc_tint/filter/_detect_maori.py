import argparse
import string
from typing import List, Union, Tuple

from wai.logging import LOGGING_WARNING
from ldc.core import DOMAIN_PRETRAIN, DOMAIN_PAIRS, DOMAIN_CLASSIFICATION
from ldc.core import LOCATION_ANY, LOCATION_INSTRUCTION, LOCATION_INPUT, LOCATION_OUTPUT, LOCATION_CONTENT, \
    LOCATION_TEXT, LOCATIONS, locations_match, add_location_argument
from ldc.api import Filter, FILTER_ACTIONS, FILTER_ACTION_KEEP, FILTER_ACTION_DISCARD
from ldc.api.pretrain import PretrainData
from ldc.api.supervised.classification import ClassificationData
from ldc.api.supervised.pairs import PairData


# https://en.wikipedia.org/wiki/M%C4%81ori_language#Orthography
MAORI_CHARS = [
    # consonants
    "h",
    "k",
    "m",
    "n",
    "p",
    "r",
    "t",
    "w",
    "ng",
    "wh",
    # short vowels
    "a",
    "e",
    "i",
    "o",
    "u",
    # long vowels
    "ā",
    "ē",
    "ī",
    "ō",
    "ū",
]

LONG_VOWELS = [
    "ā",
    "ē",
    "ī",
    "ō",
    "ū",
]


class DetectMaori(Filter):
    """
    Detects whether text is Māori or not, by calculating scores based on encountered characters after
    lower-casing the text and removing all white spaces/punctuation.
    """

    def __init__(self, max_non_maori: float = 1.0, min_maori: float = 0.0, action: str = FILTER_ACTION_KEEP,
                 location: Union[str, List[str]] = LOCATION_ANY,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the filter.

        :param max_non_maori: the maximum allowed ratio of non-Māori characters (0-1)
        :type max_non_maori: float
        :param min_maori: the minimum required ratio of Māori characters, ie long vowels (0-1)
        :type min_maori: float
        :param action: the action to apply to the data records
        :type action: str
        :param location: which part of the data to check
        :type location: str or list
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)

        if action not in FILTER_ACTIONS:
            raise Exception("Invalid action: %s" % action)

        if location not in LOCATIONS:
            raise Exception("Invalid location: %s" % location)

        self.max_non_maori = max_non_maori
        self.min_maori = min_maori
        self.location = location
        self.action = action

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "detect-maori"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Detects whether text is Māori or not, by calculating scores based on encountered characters after lower-casing the text and removing all white spaces/punctuation."

    def domains(self) -> List[str]:
        """
        Returns the domains of the filter.

        :return: the domains
        :rtype: list
        """
        return [DOMAIN_PRETRAIN, DOMAIN_PAIRS, DOMAIN_CLASSIFICATION]

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [PretrainData, PairData, ClassificationData]

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [PretrainData, PairData, ClassificationData]

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-M", "--max_non_maori", type=float, default=1.0, help="The maximum allowed ratio (0-1) of non-Māori characters in the text.")
        parser.add_argument("-m", "--min_maori", type=float, default=0.0, help="The minimum required ratio (0-1) of Māori characters (ie long vowels) in the text.")
        add_location_argument(parser, "Which data to check")
        parser.add_argument("-a", "--action", choices=FILTER_ACTIONS, default=FILTER_ACTION_KEEP, help="How to react when the thresholds are met")
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.max_non_maori = ns.max_non_maori
        self.min_maori = ns.min_maori
        self.location = ns.location
        self.action = ns.action

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()

        if isinstance(self.location, str):
            self.location = [self.location]

    def _calc_non_maori_ratio(self, s: str) -> float:
        """
        Calculates the ratio of non-Māori characters.

        :param s: the string to process (lower-case, no whitespaces)
        :type s: str
        :return: the ratio (0-1); returns 0 if 0-length string
        :rtype: float
        """
        full_len = len(s)
        if full_len == 0.0:
            return 0
        for c in MAORI_CHARS:
            s = s.replace(c, '')
        return len(s) / full_len

    def _calc_maori_ratio(self, s: str) -> float:
        """
        Calculates the ratio of Māori characters (ie long vowels).

        :param s: the string to process (lower-case, no whitespaces)
        :type s: str
        :return: the ratio (0-1); returns 0 if 0-length string
        :rtype: float
        """
        full_len = len(s)
        if full_len == 0.0:
            return 0
        for c in LONG_VOWELS:
            s = s.replace(c, '')
        return 1.0 - len(s) / full_len

    def _evaluate(self, text: str) -> Tuple[float, float]:
        """
        Evaluates the text for Māori/non-Māori characters.

        :param text: the text to evaluate
        :type text: str
        :return: tuple of Māori/non-Māori character ratios
        :rtype: tuple
        """
        if text is None:
            return 0.0, 0.0

        # lower case
        text = text.lower()
        # remove whitespaces and punctuation
        # https://stackoverflow.com/a/33967378/4698227
        text = text.translate(str.maketrans('', '', string.whitespace))
        text = text.translate(str.maketrans('', '', string.punctuation))

        # calc ratios
        non_maori = self._calc_non_maori_ratio(text)
        maori = self._calc_maori_ratio(text)
        return maori, non_maori

    def _do_process(self, data):
        """
        Processes the data record.

        :param data: the record to process
        :return: the potentially updated record or None if to drop
        """
        result = data

        ratios = dict()
        if isinstance(data, PretrainData):
            if locations_match(self.location, LOCATION_CONTENT):
                ratios[LOCATION_CONTENT] = self._evaluate(data.content)
        elif isinstance(data, PairData):
            if locations_match(self.location, LOCATION_INSTRUCTION):
                ratios[LOCATION_INSTRUCTION] = self._evaluate(data.instruction)
            if locations_match(self.location, LOCATION_INPUT):
                ratios[LOCATION_INPUT] = self._evaluate(data.input)
            if locations_match(self.location, LOCATION_OUTPUT):
                ratios[LOCATION_OUTPUT] = self._evaluate(data.output)
        elif isinstance(data, ClassificationData):
            if locations_match(self.location, LOCATION_TEXT):
                ratios[LOCATION_TEXT] = self._evaluate(data.text)
        else:
            raise Exception("Unhandled type of data: %s" % str(type(data)))

        within_thresholds = dict()
        for key in ratios:
            maori, non_maori = ratios[key]

            # within thresholds?
            within_thresholds[key] = True
            if non_maori > self.max_non_maori:
                within_thresholds[key] = False
            if maori < self.min_maori:
                within_thresholds[key] = False

            if within_thresholds[key]:
                if self.action == FILTER_ACTION_DISCARD:
                    result = None
            else:
                if self.action == FILTER_ACTION_KEEP:
                    result = None

        self.logger().info("Māori/non-Māori ratios=%s, within=%s, forward=%s"
                           % (ratios, within_thresholds, (result is not None)))

        return result
