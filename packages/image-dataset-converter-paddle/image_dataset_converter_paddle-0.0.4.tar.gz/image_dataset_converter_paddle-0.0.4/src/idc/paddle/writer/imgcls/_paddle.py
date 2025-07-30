import argparse
import os
from typing import List

from wai.logging import LOGGING_WARNING

from seppl.placeholders import placeholder_list, InputBasedPlaceholderSupporter
from idc.api import ImageClassificationData, SplittableStreamWriter, make_list, AnnotationsOnlyWriter, \
    add_annotations_only_param

DEFAULT_ID_LABEL_MAP = "labels.map"

DEFAULT_FILE_LABEL_MAP = "annotations.txt"

DEFAULT_RELATIVE_PATH = "images"


class PaddleImageClassificationWriter(SplittableStreamWriter, AnnotationsOnlyWriter, InputBasedPlaceholderSupporter):

    def __init__(self, output_dir: str = None, file_label_map: str = None, relative_path: str = None,
                 id_label_map: str = None, annotations_only: bool = None,
                 split_names: List[str] = None, split_ratios: List[int] = None, split_group: str = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the reader.

        :param output_dir: the output directory to save the data in
        :type output_dir: str
        :param file_label_map: the name of the file (no path) to store the image file name/label index relation in, uses DEFAULT_FILE_LABEL_MAP if missing
        :type file_label_map: str
        :param relative_path: the relative path to use for the images, uses DEFAULT_RELATIVE_PATH if missing
        :type relative_path: str
        :param id_label_map: the name of the file (no path) to store the label index/label string relation in, uses DEFAULT_ID_LABEL_MAP if missing
        :type id_label_map: str
        :param split_names: the names of the splits, no splitting if None
        :type split_names: list
        :param split_ratios: the integer ratios of the splits (must sum up to 100)
        :type split_ratios: list
        :param split_group: the regular expression with a single group used for keeping items in the same split, e.g., for identifying the base name of a file or the sample ID
        :type split_group: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(split_names=split_names, split_ratios=split_ratios, split_group=split_group, logger_name=logger_name, logging_level=logging_level)
        self.output_dir = output_dir
        self.file_label_map = file_label_map
        self.relative_path = relative_path
        self.id_label_map = id_label_map
        self.annotations_only = annotations_only
        self._file_label_maps = None
        self._id_label_map = None
        self._output_dir_created = False

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "to-paddle-ic"

    def description(self) -> str:
        """
        Returns a description of the writer.

        :return: the description
        :rtype: str
        """
        return "Saves the image classification in the specified text files listing image (with relative path) and the associate label ID. The label ID to text mapping is stored in a separate text file (ID <space> text)."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-o", "--output", type=str, help="The directory to store the data in. Any defined splits get added beneath there. " + placeholder_list(obj=self), required=True)
        parser.add_argument("-f", "--file_label_map", metavar="NAME", type=str, default=DEFAULT_FILE_LABEL_MAP, help="The text file to store the relation of images with their label indices in, e.g., 'annotations.txt'", required=False)
        parser.add_argument("-p", "--relative_path", metavar="PATH", type=str, default=DEFAULT_RELATIVE_PATH, help="The relative path to the annotations text file to store the images under, e.g., 'images'", required=False)
        parser.add_argument("-m", "--id_label_map", metavar="NAME", type=str, default=DEFAULT_ID_LABEL_MAP, help="The name of the ID/label text mapping text file (no path), e.g., 'labels.map'.", required=False)
        add_annotations_only_param(parser)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.output_dir = ns.output
        self.file_label_map = ns.file_label_map
        self.id_label_map = ns.id_label_map
        self.relative_path = ns.relative_path
        self.annotations_only = ns.annotations_only

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [ImageClassificationData]

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        self._output_dir_created = False
        if self.file_label_map is None:
            self.file_label_map = DEFAULT_FILE_LABEL_MAP
        if self.id_label_map is None:
            self.id_label_map = DEFAULT_ID_LABEL_MAP
        if self.relative_path is None:
            self.relative_path = DEFAULT_RELATIVE_PATH
        if self.annotations_only is None:
            self.annotations_only = False
        self._file_label_maps = dict()
        self._id_label_map = dict()

    def write_stream(self, data):
        """
        Saves the data one by one.

        :param data: the data to write (single record or iterable of records)
        """
        output_dir = self.session.expand_placeholders(self.output_dir)
        if (not self._output_dir_created) and (not os.path.exists(output_dir)):
            self._output_dir_created = True
            self.logger().info("Creating output dir: %s" % output_dir)
            os.makedirs(output_dir)
        for item in make_list(data):
            sub_dir = output_dir
            if self.splitter is not None:
                split = self.splitter.next(item=item.image_name)
                sub_dir = os.path.join(sub_dir, split)
            if not os.path.exists(sub_dir):
                self.logger().info("Creating dir: %s" % sub_dir)
                os.makedirs(sub_dir)
            if not self.annotations_only:
                path = os.path.join(sub_dir, self.relative_path)
                if not os.path.exists(path):
                    self.logger().info("Creating image dir: %s" % path)
                    os.makedirs(path)
            if sub_dir not in self._file_label_maps:
                self._file_label_maps[sub_dir] = dict()

            # relative file name
            relative_name = os.path.join(self.relative_path, item.image_name)

            # space in file name?
            if " " in relative_name:
                raise Exception("Image name cannot contain space(s): %s" % relative_name)

            # update label map
            if item.has_annotation():
                if item.annotation not in self._id_label_map:
                    self._id_label_map[item.annotation] = len(self._id_label_map)

            # update file map
            self._file_label_maps[sub_dir][relative_name] = self._id_label_map[item.annotation]

            path = os.path.join(sub_dir, self.relative_path, item.image_name)
            if not self.annotations_only:
                self.logger().info("Writing image to: %s" % path)
                item.save_image(path)

    def finalize(self):
        """
        Finishes the processing, e.g., for closing files or databases.
        """
        super().finalize()
        for sub_dir in self._file_label_maps:
            # dict with id as key
            swapped = dict((v, k) for k, v in self._id_label_map.items())
            # write label map
            path = os.path.join(sub_dir, self.id_label_map)
            self.logger().info("Writing label map: %s" % path)
            with open(path, "w") as fp:
                for key in sorted(swapped.keys()):
                    fp.write("%d %s\n" % (key, swapped[key]))

            # write file map
            path = os.path.join(sub_dir, self.file_label_map)
            self.logger().info("Writing file map: %s" % path)
            with open(path, "w") as fp:
                for key in sorted(self._file_label_maps[sub_dir].keys()):
                    fp.write("%s %d\n" % (key, self._file_label_maps[sub_dir][key]))
