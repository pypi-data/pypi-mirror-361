import argparse
import os.path
from typing import List, Iterable, Union

from seppl.placeholders import PlaceholderSupporter, placeholder_list
from seppl.io import locate_files
from wai.logging import LOGGING_WARNING

from idc.api import ImageSegmentationData, load_image_from_file, imgseg_from_indexedpng
from idc.api import Reader


class PaddleImageSegmentationReader(Reader, PlaceholderSupporter):

    def __init__(self, source: Union[str, List[str]] = None, source_list: Union[str, List[str]] = None,
                 labels_file: str = None, labels: List[str] = None, separator: str = None, resume_from: str = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the reader.

        :param source: the filename(s)
        :param source_list: the file(s) with filename(s)
        :param labels_file: the file with the labels (incl background), one per line
        :type labels_file: str
        :param labels: the list of labels to use
        :type labels: list
        :param resume_from: the file to resume from (glob)
        :type resume_from: str
        :param separator: the separator to use in the txt file (default is space)
        :type separator: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.source = source
        self.source_list = source_list
        self.labels_file = labels_file
        self.labels = labels
        self.separator = separator
        self.resume_from = resume_from
        self._inputs = None
        self._current_input = None
        self._labels = None
        self._label_mapping = None

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "from-paddle-is"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Loads the image segmentation from the specified text files listing image (JPG with relative path) and annotation image (indexed PNG with relative path). The labels (incl background) are specified via a separate text file."

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
        parser.add_argument("--labels_file", metavar="FILE", type=str, default=None, help="The file with the labels associated with the indices (incl. background); " + placeholder_list(obj=self), required=False)
        parser.add_argument("--labels", metavar="LABEL", type=str, default=None, help="The labels that the indices represent (incl background).", nargs="*")
        parser.add_argument("--separator", metavar="SEP", type=str, default=' ', help="The separator to use for reading the text files.", required=False)
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
        self.labels_file = ns.labels_file
        self.labels = ns.labels
        self.resume_from = ns.resume_from
        self.separator = ns.separator

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [ImageSegmentationData]

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()

        self._label_mapping = None
        self._labels = None
        if self.labels_file is not None:
            self._labels = list()
            self._label_mapping = dict()
            labels_file = self.session.expand_placeholders(self.labels_file)
            self.logger().info("Loading labels: %s" % labels_file)
            with (open(labels_file) as fp):
                for line in fp.readlines():
                    line = line.strip()
                    if len(line) > 0:
                        self._labels.append(line)
                        self._label_mapping[len(self._label_mapping)] = line
        elif self.labels is not None:
            self._labels = list()
            self._label_mapping = dict()
            for label in self.labels:
                self._labels.append(label)
                self._label_mapping[len(self._label_mapping)] = label
        if self._labels is None:
            raise Exception("Neither labels file nor explicit labels list specified!")
        if len(self._labels) == 0:
            raise Exception("Empty list of labels (background must be listed explicitly)!")
        self.logger().info("# labels: %d" % len(self._labels))
        self.logger().debug("label mapping: %s" % str(self._label_mapping))

        if self.separator is None:
            self.separator = ' '

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
                if self.separator in line:
                    try:
                        img_file = os.path.join(current_dir, line[0:line.rindex(self.separator)].strip())
                        ann_file = os.path.join(current_dir, line[line.rindex(self.separator)+1:].strip())
                        ann = load_image_from_file(ann_file)
                        annotations = imgseg_from_indexedpng(ann, self._labels, self._label_mapping, self.logger())
                        yield ImageSegmentationData(source=img_file, annotation=annotations)
                    except:
                        self.logger().warning("Failed to parse: %s" % line)

    def has_finished(self) -> bool:
        """
        Returns whether reading has finished.

        :return: True if finished
        :rtype: bool
        """
        return len(self._inputs) == 0
