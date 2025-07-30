import argparse
import os.path
from typing import List, Iterable, Union

from seppl.placeholders import PlaceholderSupporter, placeholder_list
from seppl.io import locate_files
from wai.logging import LOGGING_WARNING

from idc.api import ImageClassificationData
from idc.api import Reader


class PaddleImageClassificationReader(Reader, PlaceholderSupporter):

    def __init__(self, source: Union[str, List[str]] = None, source_list: Union[str, List[str]] = None,
                 id_label_map: str = None, resume_from: str = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the reader.

        :param source: the filename(s)
        :param source_list: the file(s) with filename(s)
        :param id_label_map: the file with the mapping of label ID and label string
        :type id_label_map: str
        :param resume_from: the file to resume from (glob)
        :type resume_from: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.source = source
        self.source_list = source_list
        self.id_label_map = id_label_map
        self.resume_from = resume_from
        self._inputs = None
        self._current_input = None
        self._id_label_map = None

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "from-paddle-ic"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Loads the image classification from the specified text files listing image (with relative path) and the associate label ID. The label ID to text mapping can be supplied as separate text file (ID <space> text)."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-i", "--input", type=str, help="Path to the text file(s) to read; glob syntax is supported; " + placeholder_list(obj=self), required=False, nargs="*")
        parser.add_argument("-I", "--input_list", type=str, help="Path to the text file(s) listing the text files to use; " + placeholder_list(obj=self), required=False, nargs="*")
        parser.add_argument("--resume_from", type=str, help="Glob expression matching the file to resume from, e.g., '*/012345.txt'", required=False)
        parser.add_argument("-m", "--id_label_map", metavar="FILE", type=str, default=None, help="The mapping between label ID and text (ID <space> text); " + placeholder_list(obj=self), required=False)
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
        self.id_label_map = ns.id_label_map
        self.resume_from = ns.resume_from

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [ImageClassificationData]

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()

        self._id_label_map = None
        if self.id_label_map is not None:
            self._id_label_map = dict()
            id_label_map = self.session.expand_placeholders(self.id_label_map)
            self.logger().info("Loading ID/label map: %s" % id_label_map)
            with (open(id_label_map) as fp):
                for line in fp.readlines():
                    line = line.strip()
                    if (len(line) > 0) and (" " in line):
                        try:
                            label_id = str(int(line[0:line.index(" ")].strip()))
                            label_text = line[line.index(" ") + 1:].strip()
                            self._id_label_map[label_id] = label_text
                        except:
                            self.logger().warning("Failed to parse: %s" % line)

        self._inputs = locate_files(self.source, input_lists=self.source_list, fail_if_empty=True, default_glob="*.txt", resume_from=self.resume_from)

    def read(self) -> Iterable:
        """
        Loads the data and returns the items one by one.

        :return: the data
        :rtype: Iterable
        """
        self._current_input = self._inputs.pop(0)
        self.session.current_input = self._current_input
        self.logger().info("Reading from: " + str(self.session.current_input))
        current_dir = os.path.dirname(self.session.current_input)
        with open(self.session.current_input) as fp:
            for line in fp.readlines():
                line = line.strip()
                if len(line) == 0:
                    continue
                if " " in line:
                    try:
                        label = str(int(line[line.rindex(" ")+1:].strip()))
                        if label in self._id_label_map:
                            label = self._id_label_map[label]
                        fname = os.path.join(current_dir, line[0:line.rindex(" ")].strip())
                        yield ImageClassificationData(source=fname, annotation=label)
                    except:
                        self.logger().warning("Failed to parse: %s" % line)

    def has_finished(self) -> bool:
        """
        Returns whether reading has finished.

        :return: True if finished
        :rtype: bool
        """
        return len(self._inputs) == 0
