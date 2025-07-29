import argparse
from typing import List

from faster_whisper import WhisperModel
from seppl.io import Filter
from wai.logging import LOGGING_WARNING
from adc.api import SpeechData, flatten_list, make_list


class FasterWhisperTranscribe(Filter):
    """
    Generates transcriptions for the audio files passing through.
    """

    def __init__(self, model_size: str = None, device: str = None, compute_type: str = None, beam_size: int = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the filter.

        :param model_size: the size of the whisper model to use, e.g., base or large-v3
        :type model_size: str
        :param device: the device to run on, e.g., cuda or cpu
        :type device: str
        :param compute_type: the data type to use, e.g, float16
        :type compute_type: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.beam_size = beam_size
        self._model = None

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "fw-transcribe"

    def description(self) -> str:
        """
        Returns a description of the filter.

        :return: the description
        :rtype: str
        """
        return "Generates transcriptions for the audio files passing through."

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [SpeechData]

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [SpeechData]

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-m", "--model_size", type=str, help="The size of the whisper model to use, e.g., 'base' or 'large-v3'", required=False, default="base")
        parser.add_argument("-d", "--device", type=str, help="The device to run on, e.g., 'cuda' or 'cpu'", required=False, default="cpu")
        parser.add_argument("-c", "--compute_type", type=str, help="The compute type to use, e.g., 'float16' or 'int8'", required=False, default="int8")
        parser.add_argument("-b", "--beam_size", type=int, help="The beam size to use for decoding", required=False, default=5)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.model_size = ns.model_size
        self.device = ns.device
        self.compute_type = ns.compute_type
        self.beam_size = ns.beam_size

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.model_size is None:
            self.model_size = "base"
        if self.device is None:
            self.device = "cpu"
        if self.compute_type is None:
            self.compute_type = "float16"
        if self.beam_size is None:
            self.beam_size = 5
        self._model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)

    def _do_process(self, data):
        """
        Processes the data record(s).

        :param data: the record(s) to process
        :return: the potentially updated record(s)
        """
        result = []

        for item in make_list(data):
            if item.source is not None:
                segments, info = self._model.transcribe(item.source, beam_size=self.beam_size)
            else:
                segments, info = self._model.transcribe(item.audio, beam_size=self.beam_size)
            transcript = []
            for segment in segments:
                transcript.append(segment.text.strip())
            item_new = item.duplicate(annotation=" ".join(transcript).strip())
            result.append(item_new)

        return flatten_list(result)
