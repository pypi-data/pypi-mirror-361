import argparse
import os
from typing import List

from wai.logging import LOGGING_WARNING

from seppl.placeholders import placeholder_list, InputBasedPlaceholderSupporter
from idc.api import ImageSegmentationData, SplittableStreamWriter, make_list, AnnotationsOnlyWriter, \
    add_annotations_only_param, save_image, imgseg_to_indexedpng
from simple_palette_utils import generate_palette_list, PALETTE_AUTO, palettes

DEFAULT_FILE_LIST = "data.txt"

DEFAULT_LABELS_LIST = "labels.txt"

DEFAULT_IMAGES_RELATIVE_PATH = "img"

DEFAULT_ANNOTATIONS_RELATIVE_PATH = "ann"


class PaddleImageSegmentationWriter(SplittableStreamWriter, AnnotationsOnlyWriter, InputBasedPlaceholderSupporter):

    def __init__(self, output_dir: str = None, files: str = None, labels: str = None, img_relative_path: str = None,
                 ann_relative_path: str = None, palette: str = None, annotations_only: bool = None, separator: str = None,
                 split_names: List[str] = None, split_ratios: List[int] = None, split_group: str = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the reader.

        :param output_dir: the output directory to save the data in
        :type output_dir: str
        :param files: the name of the file (no path) to store the images/annotations association in, uses DEFAULT_FILE_LIST if missing
        :type files: str
        :param labels: the name of the file (no path) to store the labels list in, uses DEFAULT_LABELS_LIST if missing
        :type labels: str
        :param img_relative_path: the relative path to use for the images, uses DEFAULT_IMAGES_RELATIVE_PATH if missing
        :type img_relative_path: str
        :param ann_relative_path: the relative path to use for the annotations, uses DEFAULT_ANNOTATIONS_RELATIVE_PATH if missing
        :type ann_relative_path: str
        :param palette: the palette to use, either a supported palette name (auto|x11|light|dark) or comma-separated list of R,G,B values
        :type palette: str
        :param annotations_only: whether to output only the annotations
        :type annotations_only: bool
        :param separator: the separator to use in the txt file (default is space)
        :type separator: str
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
        self.files = files
        self.labels = labels
        self.img_relative_path = img_relative_path
        self.ann_relative_path = ann_relative_path
        self.palette = palette
        self.annotations_only = annotations_only
        self.separator = separator
        self._files = None
        self._palette_list = None
        self._labels = None
        self._output_dir_created = False

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "to-paddle-is"

    def description(self) -> str:
        """
        Returns a description of the writer.

        :return: the description
        :rtype: str
        """
        return "Saves the image segmentation in the specified text files listing image (with relative path) and annotation (with relative path). The labels get stored in a separate text file (one per line). When splitting, the split names get appended to the '--files' name (before the extension) separated by '-'."

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-o", "--output", type=str, help="The directory to store the data in. Any defined splits get added beneath there. " + placeholder_list(obj=self), required=True)
        parser.add_argument("-f", "--files", metavar="NAME", type=str, default=DEFAULT_FILE_LIST, help="The text file to store the relation of images with their label indices in, e.g., 'data.txt'", required=False)
        parser.add_argument("-i", "--img_relative_path", metavar="PATH", type=str, default=DEFAULT_IMAGES_RELATIVE_PATH, help="The relative path to store the images under, e.g., 'img'", required=False)
        parser.add_argument("-a", "--ann_relative_path", metavar="PATH", type=str, default=DEFAULT_ANNOTATIONS_RELATIVE_PATH, help="The relative path to store the annotations under, e.g., 'ann'", required=False)
        parser.add_argument("-p", "--palette", metavar="PALETTE", type=str, default=PALETTE_AUTO, help="The palette to use; either palette name (%s) or comma-separated list of R,G,B values." % "|".join(palettes()), required=False)
        parser.add_argument("--labels", metavar="NAME", type=str, default=DEFAULT_LABELS_LIST, help="The name of the labels text file (no path), e.g., 'labels.txt'.", required=False)
        parser.add_argument("--separator", metavar="SEP", type=str, default=' ', help="The separator to use for reading the text files.", required=False)
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
        self.files = ns.files
        self.labels = ns.labels
        self.img_relative_path = ns.img_relative_path
        self.ann_relative_path = ns.ann_relative_path
        self.palette = ns.palette
        self.separator = ns.separator
        self.annotations_only = ns.annotations_only

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [ImageSegmentationData]

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        self._output_dir_created = False
        if self.files is None:
            self.files = DEFAULT_FILE_LIST
        if self.labels is None:
            self.labels = DEFAULT_LABELS_LIST
        if self.img_relative_path is None:
            self.img_relative_path = DEFAULT_IMAGES_RELATIVE_PATH
        if self.ann_relative_path is None:
            self.ann_relative_path = DEFAULT_ANNOTATIONS_RELATIVE_PATH
        self._palette_list = generate_palette_list(self.palette)
        if self.annotations_only is None:
            self.annotations_only = False
        if self.separator is None:
            self.separator = ' '
        self._files = dict()
        self._labels = list()

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
            split = ''
            if self.splitter is not None:
                split = self.splitter.next(item=item.image_name)
            if not self.annotations_only:
                path = os.path.join(output_dir, self.img_relative_path)
                if not os.path.exists(path):
                    self.logger().info("Creating image dir: %s" % path)
                    os.makedirs(path)
            if split not in self._files:
                self._files[split] = list()

            # records labels
            if len(self._labels) == 0:
                self._labels.extend(item.annotation.labels)

            # relative file names
            img_relative_name = os.path.join(self.img_relative_path, item.image_name)
            ann_relative_name = os.path.join(self.ann_relative_path, os.path.splitext(item.image_name)[0] + ".png")

            # is separator part of file name?
            if self.separator in img_relative_name:
                raise Exception("Found separator '%s' in image name '%s'! This would create an unparsable dataset, use a custom separator instead!" % (self.separator, img_relative_name))
            if self.separator in ann_relative_name:
                raise Exception("Found separator '%s' in image name '%s'! This would create an unparsable dataset, use a custom separator instead!" % (self.separator, ann_relative_name))

            # update file map
            self._files[split].append(img_relative_name + self.separator + ann_relative_name)

            path = os.path.join(output_dir, img_relative_name)
            if not self.annotations_only:
                self.logger().info("Writing image to: %s" % path)
                item.save_image(path)
            path = os.path.join(output_dir, ann_relative_name)
            ann = imgseg_to_indexedpng(item.image_width, item.image_height, item.annotation, self._palette_list, background=0)
            self.logger().info("Writing annotations to: %s" % path)
            save_image(ann, path, make_dirs=True)

    def finalize(self):
        """
        Finishes the processing, e.g., for closing files or databases.
        """
        super().finalize()
        first = True
        output_dir = self.session.expand_placeholders(self.output_dir)
        for sub_set in self._files:
            # write label list
            if first:
                first = False
                path = os.path.join(output_dir, self.labels)
                self.logger().info("Writing label list: %s" % path)
                with open(path, "w") as fp:
                    for label in self._labels:
                        fp.write(label)
                        fp.write("\n")

            # write file list
            if len(sub_set) > 0:
                path = os.path.join(output_dir, os.path.splitext(self.files)[0] + "-" + sub_set + os.path.splitext(self.files)[1])
            else:
                path = os.path.join(output_dir, self.files)
            self.logger().info("Writing file list: %s" % path)
            with open(path, "w") as fp:
                for line in self._files[sub_set]:
                    fp.write(line)
                    fp.write("\n")
