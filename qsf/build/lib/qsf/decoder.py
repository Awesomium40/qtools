from .questions import *
from .survey import _Survey
from .abc import SurveyObject, SurveyQuestion
from collections import OrderedDict
import json


class SurveyObjectDecoder(json.JSONDecoder):

    _question_map_ = {'Matrix': MatrixQuestion,
                      'MC': MultiChoiceQuestion,
                      "RO": RankOrderQuestion,
                      "SQ": SliderQuestion,
                      "TE": TextEntryQuestion,
                      'SBS': SideBySideQuestion}

    def __init__(self, *args, **kwargs):
        if 'object_hook' in kwargs:
            kwargs.pop('object_hook')

        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, data):
        if data.get('SurveyEntry') is not None and data.get('SurveyElements') is not None:
            cls = _Survey
        elif data.get('Element', None) == 'SQ':
            cls = self._question_map_.get(data['Payload']['QuestionType'], SurveyQuestion)
        else:
            cls = SurveyObject

        return cls(data)

    def object_pairs_hook(self, data):
        return OrderedDict(data)
