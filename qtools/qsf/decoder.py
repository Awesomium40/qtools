from dotted_dict import DottedDict
from .questions import *
from .survey import _Survey
from .abc import SurveyObjectBase, SurveyQuestion
from collections import OrderedDict
import json


class SurveyObjectDecoder(json.JSONDecoder):

    _question_map_ = {'Matrix': MatrixQuestion,
                      'MC': MultiChoiceQuestion,
                      "RO": RankOrderQuestion,
                      "Slider": SliderQuestion,
                      "TE": TextEntryQuestion,
                      'SBS': SideBySideQuestion}

    _question_keys_ = ("questionLabel", "questionName", "questionText", "questionType",)
    _block_keys_ = ('description', 'elements',)
    _survey_keys_ = ('SurveyEntry', 'SurveyElements',)

    def __init__(self, *args, **kwargs):
        hook = self.object_hook if 'object_hook' not in kwargs else kwargs.pop('object_hook')

        super().__init__(object_hook=hook, *args, **kwargs)

    def _is_question_(self, data):
        return data.get('Element') == 'SQ'

    def _is_block_(self, data):
        return all(itm in self._block_keys_ for itm in data.keys())

    def _is_survey_(self, data):
        return all(itm in data for itm in self._survey_keys_)

    def object_hook(self, data):

        if self._is_survey_(data):
            cls = _Survey
        elif self._is_question_(data):
            cls = self._question_map_.get(data['Payload']['QuestionType'], SurveyQuestion)
        else:
            cls = SurveyObjectBase
        
        return cls(data)

    def object_pairs_hook(self, data):
        for itm in data:
            print(itm[0])
        print("#####################################################################")
        return OrderedDict(data)

