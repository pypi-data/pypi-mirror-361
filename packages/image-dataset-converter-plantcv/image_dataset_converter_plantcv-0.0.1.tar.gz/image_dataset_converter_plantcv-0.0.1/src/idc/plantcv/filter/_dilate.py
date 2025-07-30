import argparse
from typing import List

import numpy as np
from plantcv import plantcv as pcv
from wai.logging import LOGGING_WARNING

from idc.api import ImageClassificationData, ObjectDetectionData, ImageSegmentationData, grayscale_required_info
from ._morphological_filter import MorphologicalFilter, REQUIRED_FORMAT_GRAYSCALE


class Dilate(MorphologicalFilter):
    """
    Performs morphological 'dilation' filtering. Adds pixel to center of kernel if conditions set in kernel are true.
    """

    def __init__(self, kernel_size: int = None, num_iterations: int = None,
                 logger_name: str = None, logging_level: str = LOGGING_WARNING):
        """
        Initializes the filter.

        :param kernel_size: the kernel size to use
        :type kernel_size: int
        :param num_iterations: the number of iterations to perform
        :type num_iterations: int
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)
        self.kernel_size = kernel_size
        self.num_iterations = num_iterations

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "pcv-dilate"

    def description(self) -> str:
        """
        Returns a description of the filter.

        :return: the description
        :rtype: str
        """
        return "Performs morphological 'dilation' filtering. Adds pixel to center of kernel if conditions set in kernel are true. " + grayscale_required_info()

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
        parser.add_argument("-k", "--kernel_size", type=int, help="The kernel size, must greater than 1 to have an effect.", default=3, required=False)
        parser.add_argument("-i", "--num_iterations", type=int, help="The number of iterations to perform.", default=1, required=False)
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.kernel_size = ns.kernel_size
        self.num_iterations = ns.num_iterations

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        if self.kernel_size is None:
            self.kernel_size = 3
        if self.kernel_size < 1:
            raise Exception("Kernel size must be at least 1, current: %s" % str(self.kernel_size))
        if self.num_iterations is None:
            self.num_iterations = 1
        if self.num_iterations < 1:
            raise Exception("# iterations must be at least 1, current: %s" % str(self.num_iterations))

    def _nothing_to_do(self, data) -> bool:
        """
        Checks whether there is nothing to do, e.g., due to parameters.

        :param data: the data to process
        :return: whether nothing needs to be done
        :rtype: bool
        """
        return self.kernel_size == 1

    def _required_format(self) -> str:
        """
        Returns what input format is required for applying the filter.

        :return: the type of image
        :rtype: str
        """
        return REQUIRED_FORMAT_GRAYSCALE

    def _apply_filter(self, array: np.ndarray) -> np.ndarray:
        """
        Applies the morphological filter to the image and returns the numpy array.

        :param array: the image the filter to apply to
        :type array: np.ndarray
        :return: the filtered image
        :rtype: np.ndarray
        """
        return pcv.dilate(array, self.kernel_size, self.num_iterations)
