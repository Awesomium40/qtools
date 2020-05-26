from . import decoder, abc
from .survey import _Survey
from .questions import *
import json


__all__ = ["MatrixQuestion", "MultiChoiceQuestion", "RankOrderQuestion", "SideBySideQuestion",
           'SliderQuestion', 'TextEntryQuestion', 'Survey']



def Survey(data):
    """
    Survey(path) -> qsf.survey._Survey
    Factory method for creating a Survey object from a qualtrics .qsf export
    :param data: text data to be JSON parsed
    :return: Survey object
    """
    s = json.loads(data, cls=decoder.SurveyObjectDecoder)['result']

    return s