import argparse
from typing import Iterable, List, Union

from faster_whisper import WhisperModel

from wai.logging import LOGGING_WARNING
from seppl.io import locate_files
from seppl.placeholders import PlaceholderSupporter, placeholder_list
from ldc.core import domain_suffix
from ldc.api.pretrain import PretrainData, PretrainReader


class FasterWhisperAudioPretrainReader(PretrainReader, PlaceholderSupporter):
    """
    Transcribes text from audio files (.wav, .mp3) to use for pretraining.
    """

    def __init__(self, source: Union[str, List[str]] = None, source_list: Union[str, List[str]] = None,
                 combine_segments: bool = None,
                 model_size: str = None, device: str = None, compute_type: str = None, beam_size: int = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the reader.

        :param source: the filename(s)
        :param source_list: the file(s) with filename(s)
        :param combine_segments: whether to combine the segments into a single document or forward them one by one
        :type combine_segments: bool
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
        self.source = source
        self.source_list = source_list
        self.combine_segments = combine_segments
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.beam_size = beam_size
        self._inputs = None
        self._current_input = None
        self._model = None

    def name(self) -> str:
        """
        Returns the name of the reader, used as command-line name.

        :return: the name
        :rtype: str
        """
        return "from-fwaudio-" + domain_suffix(self)

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Transcribes text from audio files (.wav, .mp3) to use for pretraining."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-i", "--input", type=str, help="Path to the audio file(s) to read (.wav, .mp3); glob syntax is supported; " + placeholder_list(obj=self), required=False, nargs="*")
        parser.add_argument("-I", "--input_list", type=str, help="Path to the text file(s) listing the audio files to use (.wav, .mp3); " + placeholder_list(obj=self), required=False, nargs="*")
        parser.add_argument("-1", "--combine_segments", action="store_true", help="Whether to combine the segments into a single document or forward them one-by-one", required=False)
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
        self.source = ns.input
        self.source_list = ns.input_list
        self.combine_segments = ns.combine_segments
        self.model_size = ns.model_size
        self.device = ns.device
        self.compute_type = ns.compute_type
        self.beam_size = ns.beam_size

    def initialize(self):
        """
        Initializes the reading, e.g., for opening files or databases.
        """
        super().initialize()
        self._inputs = locate_files(self.source, input_lists=self.source_list, fail_if_empty=True)
        if self.combine_segments is None:
            self.combine_segments = False
        if self.model_size is None:
            self.model_size = "base"
        if self.device is None:
            self.device = "cpu"
        if self.compute_type is None:
            self.compute_type = "float16"
        if self.beam_size is None:
            self.beam_size = 5
        self._model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)

    def read(self) -> Iterable[PretrainData]:
        """
        Loads the data and returns the items one by one.

        :return: the data
        :rtype: Iterable[PretrainData]
        """
        self._current_input = self._inputs.pop(0)
        self.session.current_input = self._current_input
        self.logger().info("Reading from: " + str(self.session.current_input))

        try:
            segments, info = self._model.transcribe(self.session.current_input, beam_size=self.beam_size)
            if self.combine_segments:
                meta = dict()
                meta["file"] = self.session.current_input
                lines = [segment.text for segment in segments]
                yield PretrainData(
                    content="\n".join(lines),
                    meta=meta,
                )
            else:
                for segment in segments:
                    meta = dict()
                    meta["file"] = self.session.current_input
                    meta["start"] = segment.start
                    meta["end"] = segment.end
                    yield PretrainData(
                        content=segment.text,
                        meta=meta,
                    )
        except:
            self.logger().exception("Failed to read from: %s" % self.session.current_input)
            yield None

    def has_finished(self) -> bool:
        """
        Returns whether reading has finished.

        :return: True if finished
        :rtype: bool
        """
        return len(self._inputs) == 0
