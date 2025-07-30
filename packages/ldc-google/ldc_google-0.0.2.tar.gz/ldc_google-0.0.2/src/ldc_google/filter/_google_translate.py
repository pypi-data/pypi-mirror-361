import argparse
import copy
from typing import List, Union

from google.cloud import translate
from wai.logging import LOGGING_WARNING

from ldc.api import Filter
from ldc.api.pretrain import PretrainData
from ldc.api.supervised.pairs import PairData
from ldc.api.translation import TranslationData
from ldc.core import DOMAIN_PAIRS, DOMAIN_PRETRAIN, DOMAIN_TRANSLATION
from ldc.core import LOCATION_ANY, LOCATION_INSTRUCTION, LOCATION_INPUT, LOCATION_OUTPUT, LOCATION_CONTENT, \
    LOCATIONS, locations_match, add_location_argument
from ldc.text_utils import remove_empty


class GoogleTranslate(Filter):
    """
    Translates text using Google's Translate API.

    https://cloud.google.com/translate/docs/reference/libraries/v3/python
    https://cloud.google.com/translate/docs/advanced/translating-text-v3#translating_text
    # use local dev credentials
    https://cloud.google.com/docs/authentication/provide-credentials-adc#local-dev
    # enable quota project
    https://cloud.google.com/docs/authentication/troubleshoot-adc#user-creds-client-based
    """

    def __init__(self, project_id: str = None, source_lang: str = None, target_lang: str = None,
                 split_lines: bool = False, location: Union[str, List[str]] = LOCATION_ANY,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the filter. Either encoding or model need to be provided.

        :param project_id: the name/ID of the Google Cloud project
        :type project_id: str
        :param source_lang: the language of the text to be translated
        :type source_lang: str
        :param target_lang: the language to translate the text into
        :type target_lang: str
        :param split_lines: whether to split the text on newlines
        :type split_lines: bool
        :param location: which part of the data to count the tokens
        :type location: str or list
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)

        if location not in LOCATIONS:
            raise Exception("Invalid location: %s" % location)

        self.project_id = project_id
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.split_lines = split_lines
        self.location = location
        self._client = None
        self._count = 0

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "google-translate"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Translates text using Google's Translate API. The 'project_id' refers to your project ID in the "\
               "Google Cloud console (http://console.cloud.google.com/). "\
               "The Google Translate API must be enabled. "\
               "Requires local dev credentials: https://cloud.google.com/docs/authentication/provide-credentials-adc#local-dev"

    def domains(self) -> List[str]:
        """
        Returns the domains of the filter.

        :return: the domains
        :rtype: list
        """
        return [DOMAIN_PAIRS, DOMAIN_PRETRAIN, DOMAIN_TRANSLATION]

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [PairData, PretrainData, TranslationData]

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [PairData, PretrainData, TranslationData]

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-p", "--project_id", type=str, default=None, help="The name/ID of the Google Cloud project to use.", required=False)
        parser.add_argument("-s", "--source_lang", type=str, default=None, help="The language the incoming text is in.", required=False)
        parser.add_argument("-t", "--target_lang", type=str, default=None, help="The language to translate the text into.", required=False)
        parser.add_argument("--split_lines", action="store_true", help="Whether to split the text on new lines rather than presenting it as a single item to translate.")
        add_location_argument(parser, "Which data use for counting tokens")
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.project_id = ns.project_id
        self.source_lang = ns.source_lang
        self.target_lang = ns.target_lang
        self.split_lines = ns.split_lines
        self.location = ns.location

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        
        if self.project_id is None:
            raise Exception("No Google Cloud project ID provided!")

        if self.source_lang is None:
            raise Exception("Language for the incoming text not provided!")

        if self.target_lang is None:
            raise Exception("No language specified in which to translate!")

        if isinstance(self.location, str):
            self.location = [self.location]
        self._client = translate.TranslationServiceClient()

    def _translate(self, s: str) -> str:
        """
        Translates the text.
        
        :param s: the text to translate
        :type s: str
        :return: the translated text
        :rtype: str
        """
        # skip empty text
        if len(s.strip()) == 0:
            return s

        self._count += len(s)
        if self.split_lines:
            contents = remove_empty(s.split("\n"))
        else:
            contents = [s]
        location = "global"
        parent = f"projects/{self.project_id}/locations/{location}"
        response = self._client.translate_text(
            request={
                "parent": parent,
                "contents": contents,
                "mime_type": "text/plain",
                "source_language_code": self.source_lang,
                "target_language_code": self.target_lang,
            }
        )
        result = s
        translated = []
        for translation in response.translations:
            translated.append(translation.translated_text)
        if len(translated) > 0:
            result = "\n".join(translated)

        self.logger().debug("%s -> %s" % (s, result))

        return result

    def _do_process(self, data):
        """
        Processes the data record.

        :param data: the record to process
        :return: the potentially updated record or None if to drop
        """
        result = copy.deepcopy(data)

        if isinstance(result, PairData):
            if locations_match(self.location, LOCATION_INSTRUCTION):
                result.instruction = self._translate(result.instruction)
            if locations_match(self.location, LOCATION_INPUT):
                result.input = self._translate(result.input)
            if locations_match(self.location, LOCATION_OUTPUT):
                result.output = self._translate(result.output)
        elif isinstance(result, PretrainData):
            if locations_match(self.location, LOCATION_CONTENT):
                result.content = self._translate(result.content)
        elif isinstance(result, TranslationData):
            if self.source_lang in result.translations:
                result.translations[self.target_lang] = self._translate(result.translations[self.source_lang])
        else:
            raise Exception("Unhandled data type: %s" % str(type(result)))

        return result

    def finalize(self):
        """
        Finishes the processing, e.g., for closing files or databases.
        """
        super().finalize()
        self.logger().info("# characters: %d" % self._count)
