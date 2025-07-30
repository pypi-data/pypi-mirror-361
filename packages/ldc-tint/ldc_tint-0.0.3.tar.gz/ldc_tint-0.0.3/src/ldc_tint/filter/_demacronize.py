import argparse
import copy
from typing import List, Union

from wai.logging import LOGGING_WARNING
from ldc.core import DOMAIN_PAIRS, DOMAIN_PRETRAIN, DOMAIN_TRANSLATION, DOMAIN_CLASSIFICATION
from ldc.core import LOCATION_ANY, LOCATION_INSTRUCTION, LOCATION_INPUT, LOCATION_OUTPUT, LOCATION_CONTENT, \
    LOCATION_TEXT, LOCATIONS, locations_match, add_location_argument
from ldc.api import Filter
from ldc.api.pretrain import PretrainData
from ldc.api.supervised.classification import ClassificationData
from ldc.api.supervised.pairs import PairData
from ldc.api.translation import TranslationData


DEMACRONIZE_STRIP = "strip"
DEMACRONIZE_DOUBLE = "double"
DEMACRONIZE_TRIPLE = "triple"
DEMCRONIZATION = [
    DEMACRONIZE_STRIP,
    DEMACRONIZE_DOUBLE,
    DEMACRONIZE_TRIPLE,
]


class Demacronize(Filter):
    """
    Removes macrons from text.
    """

    def __init__(self, demacronization: str = DEMACRONIZE_DOUBLE, location: Union[str, List[str]] = LOCATION_ANY,
                 languages: List[str] = None, logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the filter.

        :param demacronization: how to process the macrons
        :type demacronization: str
        :param location: in which part of the data to look for the macrons
        :type location: str or list
        :param languages: the languages to restrict the check to, None to check all
        :type languages: list
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)

        if demacronization not in DEMCRONIZATION:
            raise Exception("Invalid demacronization: %s" % demacronization)

        if location not in LOCATIONS:
            raise Exception("Invalid location: %s" % location)

        self.demacronization = demacronization
        self.location = location
        self.languages = languages

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "de-macronize"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Removes macrons from text, e.g., Ā -> Aa and ā -> aa"

    def domains(self) -> List[str]:
        """
        Returns the domains of the filter.

        :return: the domains
        :rtype: list
        """
        return [DOMAIN_PAIRS, DOMAIN_PRETRAIN, DOMAIN_TRANSLATION, DOMAIN_CLASSIFICATION]

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [PairData, PretrainData, TranslationData, ClassificationData]

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [PairData, PretrainData, TranslationData, ClassificationData]

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-d", "--demacronization", choices=DEMCRONIZATION, default=DEMACRONIZE_DOUBLE, help="How to process the macrons")
        add_location_argument(parser, "Where to look for the macrons")
        parser.add_argument("-g", "--language", type=str, help="The languages to inspect; inspects all if not specified", required=False, nargs="*")
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.demacronization = ns.demacronization
        self.location = ns.location
        self.languages = ns.language

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()

        if self.languages is not None:
            self.languages = [x.lower() for x in self.languages]
        if isinstance(self.location, str):
            self.location = [self.location]

    def _strip(self, s: str) -> str:
        """
        Just removes the macrons.

        :param s: the string to process
        :type s: str
        :return: the processed string
        :rtype: str
        """
        s = s.replace("Ā", "A")
        s = s.replace("ā", "a")
        s = s.replace("Ē", "E")
        s = s.replace("ē", "e")
        s = s.replace("Ī", "I")
        s = s.replace("ī", "i")
        s = s.replace("Ō", "O")
        s = s.replace("ō", "o")
        s = s.replace("Ū", "U")
        s = s.replace("ū", "u")
        return s

    def _double(self, s: str) -> str:
        """
        Replaces the macrons with doubled-up vowels.

        :param s: the string to process
        :type s: str
        :return: the processed string
        :rtype: str
        """
        s = s.replace("Ā", "Aa")
        s = s.replace("ā", "aa")
        s = s.replace("Ē", "Ee")
        s = s.replace("ē", "ee")
        s = s.replace("Ī", "Ii")
        s = s.replace("ī", "ii")
        s = s.replace("Ō", "Oo")
        s = s.replace("ō", "oo")
        s = s.replace("Ū", "Uu")
        s = s.replace("ū", "uu")
        return s

    def _triple(self, s: str) -> str:
        """
        Replaces the macrons with tripled vowels.

        :param s: the string to process
        :type s: str
        :return: the processed string
        :rtype: str
        """
        s = s.replace("Ā", "Aaa")
        s = s.replace("ā", "aaa")
        s = s.replace("Ē", "Eee")
        s = s.replace("ē", "eee")
        s = s.replace("Ī", "Iii")
        s = s.replace("ī", "iii")
        s = s.replace("Ō", "Ooo")
        s = s.replace("ō", "ooo")
        s = s.replace("Ū", "Uuu")
        s = s.replace("ū", "uuu")
        return s

    def _process_macrons(self, s: str) -> str:
        """
        Processes the macrons.

        :param s: the string to process
        :type s: str
        :return: the processed string
        :rtype: str
        """
        if self.demacronization == DEMACRONIZE_STRIP:
            return self._strip(s)
        elif self.demacronization == DEMACRONIZE_DOUBLE:
            return self._double(s)
        elif self.demacronization == DEMACRONIZE_TRIPLE:
            return self._triple(s)
        else:
            raise Exception("Unhandled demacronization: %s" % self.demacronization)

    def _do_process(self, data):
        """
        Processes the data record.

        :param data: the record to process
        :return: the potentially updated record or None if to drop
        """
        result = copy.deepcopy(data)

        if isinstance(result, PairData):
            if locations_match(self.location, LOCATION_INSTRUCTION):
                result.instruction = self._process_macrons(result.instruction)
            if locations_match(self.location, LOCATION_INPUT):
                result.input = self._process_macrons(result.input)
            if locations_match(self.location, LOCATION_OUTPUT):
                result.output = self._process_macrons(result.output)
        elif isinstance(result, ClassificationData):
            if locations_match(self.location, LOCATION_TEXT):
                result.text = self._process_macrons(result.text)
        elif isinstance(result, PretrainData):
            if locations_match(self.location, LOCATION_CONTENT):
                result.content = self._process_macrons(result.content)
        elif isinstance(result, TranslationData):
            if self.languages is None:
                for k in result.translations:
                    result.translations[k] = self._process_macrons(result.translations[k])
            else:
                for lang in self.languages:
                    if lang in result.translations:
                        result.translations[lang] = self._process_macrons(result.translations[lang])
        else:
            raise Exception("Unhandled data type: %s" % str(type(result)))

        return result
