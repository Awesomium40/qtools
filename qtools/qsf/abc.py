from collections import OrderedDict
import re


class SurveyObjectBase(OrderedDict):

    class AttributeNotFound(object):
        pass

    __counter__ = 0

    def __init__(self, items, **kwargs):
        super().__init__(items, **kwargs)

    def __getattr__(self, item):

        value = self.get(item, self.AttributeNotFound)
        if value is self.AttributeNotFound:
            raise AttributeError(item)

        return value

    def __setattr__(self, key, value):

        if key in self.keys():
            raise AttributeError(f"Setting of attribute {key} not supported")
        else:
            setattr(super(SurveyObjectBase, self), key, value)

    def __str__(self):
        return "{\n" + "\n".join(f"{key}: {value}" for key, value in self.items()) + "\n}"

    @staticmethod
    def _multi_replace_(txt, repl, ignore_case=False, whole_word_only=False):
        """
        caastools.utils._multi_replace_(text, repl, ignore_case=False, whole_word_only=False) -> str
        Performs simultaneous multi-replacement of substrings within a string
        :param txt: string in which replacements are to be performed
        :param repl: dictionary mapping substrings to be replaced with their replacements
        :param ignore_case: specifies whether to ignore case in search/replacement. Default False
        :param whole_word_only: specifies whether to replace only on whole word matches. Default False
        :return: string with replacements made
        """

        repl_str = "{0}{{0}}{0}".format("\\b" if whole_word_only else '')

        # The problem is that there is the risk of having one replacement be
        # the substring of another. Deal with this issue by sorting long to short
        replacements = sorted(repl, key=len, reverse=True)

        # Next, we can just use the regex engine to do the replacements all at once
        # Preferable to iteration because sequential replacement may cause undesired results
        replace_re = re.compile("|".join(map(lambda x: repl_str.format(re.escape(x)), replacements)),
                                re.IGNORECASE if ignore_case else 0)

        return replace_re.sub(lambda match: repl[match.group(0)], txt)

    @staticmethod
    def _sanitize_for_spss_(dirty_str, sub=None):
        """
        _sanitize_for_spss_(str, subs={}) -> str
        Sanitizes the provided string into an SPSS-Compatible identifier
        :param dirty_str: the string to be sanitized
        :param sub: A dictionary of substitutions to use in the santization process. Keys will be replaced with values
        in the sanitized string. Note that using unsanitary values will cause custom substitutions to themselves be sanitized.
        Default None
        :return: str
        """
        # SPSS has specifications on variable names. These will help ensure they are met
        max_length = 64
        invalid_chars = re.compile(r"[^a-zA-Z0-9_.]")
        invalid_starts = re.compile(r"[^a-zA-Z]+")
        subs = {} if sub is None else sub

        # Remove invalid starting characters
        start_invalid = invalid_starts.match(dirty_str)
        new_var = invalid_starts.sub('', dirty_str, count=1) if start_invalid else dirty_str

        # Possible that the process of removing starting chars could create empty string,
        # so create valid var name in that case
        if len(new_var) == 0:
            SurveyObjectBase.__counter__ += 1
            new_var = "VAR_{0}".format(SurveyObjectBase.__counter__)

        # Trim off excess characters to fit into maximum allowable length
        new_var = new_var[:max_length] if len(new_var) > max_length else new_var

        # If any custom substitutions are required, perform prior to final sanitization
        if len(subs) > 0:
            new_var = SurveyObjectBase._multi_replace_(new_var, subs)

        # locate invalid characters and replace with underscores
        replacements = {x: "_" for x in invalid_chars.findall(new_var)}
        new_var = SurveyObjectBase._multi_replace_(new_var, replacements) if len(replacements) > 0 else new_var

        return new_var


class SurveyQuestion(SurveyObjectBase):

    _content_types_ = {'ValidEmail': None, "ValidZip": "ValidZipType", "ValidDate": "ValidDateType",
                       "ValidTextOnly": None, "ValidUSState": None, "ValidPhone": None, "ValidNumber": "ValidNumber"}

    _validation_types_ = {"MinChar": "MinChars", "TotalChar": "TotalChars",
                          "None": None}
    CONTENT_TYPE = "ContentType"

    def __init__(self, items, **kwargs):
        super().__init__(items, **kwargs)

    def variable_info(self):
        """
        sq.variable_info() -> tuple
        Returns a list containing tuples of SPSS variable information.
        The number of tuples within the row depends on the nature of the question
        For Single-Answer Matrix-style questions (i.e. Matrix and Slider),
        there will be one tuple per statement in the matrix
        For Single-Answer, non-Matrix questions, there will be a single tuple
        For Multi-Answer, Matrix questions, there will be one tuple for each statement/answer combination
        (i.e. 3 statements with 3 possible answers will yield 9 rows)
        for Multi-Answer, non-Matrix questions, there will be one tuple for each possible answer

        Each tuple contains the following information:
        QuestionID,
        QuestionType,
        Selector,
        SubSelector (if any, otherwise None),
        QuestionStem (Text of the question),
        QuestionLeaf (For matrix-style questions, this is the text of the individual matrix item),
        Variable Name (The name as it would appear in an SPSS dataset)
        Variable label (The variable label as it would appear in an SPSS dataset)
        Value labels (Value labels as they would appear in an SPSS dataset)
        Validation (Any validation data used by the question)
        :return: list[tuple]
        """
        raise NotImplementedError("variable_info() not implemented for {0}".format(type(self)))

    def validation(self):
        settings: SurveyObjectBase = self.Payload.Validation.Settings
        validation_type: str = settings.Type

        # Need to try and decode the validation data for text entry questions
        sub_type_key = self._validation_types_.get(validation_type)
        if validation_type == self.CONTENT_TYPE:

            content_type = settings.get(validation_type)
            validation_extra = settings.get(content_type) if content_type is not None else None
        elif sub_type_key is not None:
            content_type = None
            validation_extra = settings.get(sub_type_key)
        else:
            content_type = None
            validation_extra = None

        validation_info = SurveyObjectBase((
            ("Type", validation_type), ("Settings_1", content_type), ("Settings_2", validation_extra)
        ))

        return validation_info
