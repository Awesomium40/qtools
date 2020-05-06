from qsf import decoder
from .survey import _Survey
from .questions import *
import json


__all__ = ["MatrixQuestion", "MultiChoiceQuestion", "RankOrderQuestion", "SideBySideQuestion",
           'SliderQuestion', 'TextEntryQuestion', 'Survey']


def Survey(path):
    """
    Survey(path) -> qsf.survey._Survey
    Factory method for creating a Survey object from a qualtrics .qsf export
    :param path: path to the QSF file for the survey
    :return: Survey object
    """
    with open(path, 'r') as in_file:
        s = json.load(in_file, cls=decoder.SurveyObjectDecoder)

    return s
