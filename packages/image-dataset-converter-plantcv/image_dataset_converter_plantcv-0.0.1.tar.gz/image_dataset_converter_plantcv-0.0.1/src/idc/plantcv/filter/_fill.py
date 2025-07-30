import argparse
from typing import List

import numpy as np
from plantcv import plantcv as pcv
from wai.logging import LOGGING_WARNING

from idc.api import ImageClassificationData, ObjectDetectionData, ImageSegmentationData, binary_required_info
from ._morphological_filter import MorphologicalFilter, REQUIRED_FORMAT_BINARY


class Fill(MorphologicalFilter):
    """
    Identifies objects and fills objects that are less than the specified 'size' in pixels.
    """

    def __init__(self, size: int = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the filter.

        :param size: the minimum object area size
        :type size: int
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.size = size

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "pcv-fill"

    def description(self) -> str:
        """
        Returns a description of the filter.

        :return: the description
        :rtype: str
        """
        return "Identifies objects and fills objects that are less than the specified 'size' in pixels. " + binary_required_info()

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [ImageClassificationData, ObjectDetectionData, ImageSegmentationData]

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [ImageClassificationData, ObjectDetectionData, ImageSegmentationData]

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-s", "--size", type=int, help="The minimum object area size in pixels.", default=1, required=False)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.size = ns.size

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.size is None:
            self.size = 1
        if self.size < 1:
            raise Exception("Minimum object area size must be at least 1, current: %s" % str(self.size))

    def _required_format(self) -> str:
        """
        Returns what input format is required for applying the filter.

        :return: the type of image
        :rtype: str
        """
        return REQUIRED_FORMAT_BINARY

    def _apply_filter(self, array: np.ndarray) -> np.ndarray:
        """
        Applies the morphological filter to the image and returns the numpy array.

        :param array: the image the filter to apply to
        :type array: np.ndarray
        :return: the filtered image
        :rtype: np.ndarray
        """
        return pcv.fill(array, self.size)
