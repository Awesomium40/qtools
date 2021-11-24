from .abc import SurveyQuestion

__all__ = ['MatrixQuestion', 'MultiChoiceQuestion', 'RankOrderQuestion', 'SideBySideQuestion',
           'SliderQuestion', 'TextEntryQuestion']


class MatrixQuestion(SurveyQuestion):

    def __init__(self, items, **kwargs):
        super().__init__(items, **kwargs)

    @property
    def is_multi_answer(self):
        return self.Payload.Selector != 'Bipolar' and self.Payload.SubSelector == 'MultipleAnswer'

    @staticmethod
    def choice_has_text_entry(choice):
        return choice.get('TextEntry') is not None

    def variable_info(self):
        rows = []
        answers = self.Payload.Answers
        ans_order = [str(x) for x in self.Payload.AnswerOrder]
        choices = self.Payload.Choices
        choice_order = [str(x) for x in self.Payload.ChoiceOrder]
        data_export_tags = self.Payload.ChoiceDataExportTags
        qid = self.Payload.QuestionID
        recode_values = self.Payload.get("RecodeValues")
        stem = self.Payload.QuestionDescription

        var_name_base = self.Payload.DataExportTag
        var_naming = self.Payload.get("VariableNaming")

        for key in choice_order:

            if self.is_multi_answer:
                for a_key in ans_order:
                    vn_leaf = recode_values[a_key] if recode_values is not None else a_key
                    vl_leaf = var_naming[a_key] if var_naming is not None else answers[key].Display
                    base = data_export_tags[key] if data_export_tags else f"{var_name_base}_{key}"

                    var_name = self._sanitize_for_spss_(f"{base}_{vn_leaf}")
                    var_label = f"{stem} - {choices[key].Display} {vl_leaf}"
                    value_labels = {1:  var_naming[a_key] if var_naming is not None else answers[key].Display}

                    rows.append([qid, var_name, var_label, value_labels])

            else:
                base = data_export_tags[key] if data_export_tags else f"{var_name_base}_{key}"
                var_name = self._sanitize_for_spss_(base)
                var_label = f"{stem} - {choices[key].Display}"

                value_labels = {recode_values[a_key] if recode_values is not None else a_key:
                                var_naming[a_key] if var_naming is not None else answers[a_key].Display
                                for a_key in ans_order}
                rows.append([qid, var_name, var_label, value_labels])

                if self.choice_has_text_entry(choices[key]):
                    rows.append([qid, f'{var_name}_TEXT', f'{var_label} - Text', None])

            if self.choice_has_text_entry(choices[key]):
                rows.append([qid, f'{base}_TEXT', f"{stem} - {choices[key].Display} - Text", None])

        return rows


class MultiChoiceQuestion(SurveyQuestion):

    def __init__(self, items, **kwargs):
        super().__init__(items, **kwargs)

    @property
    def is_multi_answer(self):
        return self.Payload.Selector in ('MAVR', 'MAHR', 'MACOL', 'MSB')

    def _variable_name_(self, choice_id=None):

        if choice_id is None:
            var_name = self.Payload.DataExportTag
        else:
            recode_values = self.Payload.get('RecodeValues')
            var_name = self.Payload.DataExportTag
            var_name_ext = recode_values[choice_id] if recode_values is not None else choice_id
            var_name = self._sanitize_for_spss_(f"{var_name}_{var_name_ext}")

        return var_name

    def variable_info(self):
        rows = []
        qid = self.Payload.QuestionID
        choices = self.Payload.Choices
        choice_order = [str(x) for x in self.Payload.ChoiceOrder]

        # Sometimes a response set will have recoded values. If so, need to retrieve them
        recode_values = self.Payload.get('RecodeValues')
        var_rename = self.Payload.get('VariableNaming')

        if qid == 'QID3':
            x = 25

        # How data translates to variables depends on if the question was SA or MA.
        # MA questions provide a variable for each possible choice,
        # SA questions provide a single variable representing the selection made from all choices
        if self.is_multi_answer:
            for choice_id in choice_order:
                leaf = var_rename[choice_id] if var_rename is not None else choices[choice_id].Display
                value_labels = {1: leaf}
                var_label = f"{self.Payload.QuestionDescription} {leaf}"
                var_name = self._variable_name_(choice_id)
                rows.append([qid, var_name, var_label, value_labels])

                # If a choice also allows Text entry, there should be an additional variable for the contents
                # of the text entry
                if choices[choice_id].get("TextEntry") in (True, "true"):
                    rows.append([qid, f'{var_name}_Text', f'{var_label} - Text', None])

        else:
            var_name = self._variable_name_()
            value_labels = {recode_values[key] if recode_values is not None else key:
                            var_rename[key] if var_rename is not None else choices[key].Display
                            for key in choice_order}

            var_label = self.Payload.QuestionDescription
            rows.append([qid, var_name, var_label, value_labels])

            # Some choices may have TextEntry attached to them. For those choices, add additional variables
            # for the contents of text entry
            for choice in filter(lambda x: choices[x].get("TextEntry") in (True, "true"), choice_order):
                vn_recode = str(choice) if recode_values is None else recode_values[choice]
                rows.append([qid, f"{var_name}_{vn_recode}_Text", f'{var_label} - Text', None])

        return rows


class RankOrderQuestion(SurveyQuestion):

    def __init__(self, items, **kwargs):
        super().__init__(items, **kwargs)

    def variable_info(self):
        rows = []
        choices = self.Payload.Choices
        choice_order = self.Payload.ChoiceOrder
        recodes = self.Payload.get('RecodeValues') if self.Payload.get('RecodeValues') is not None else \
            {key: key for key in self.Payload.Choices}
        value_labels = {key: key for key in self.Payload.Choices}

        for key in choice_order:
            rows.append([self.Payload.QuestionID, f'{self.Payload.DataExportTag}_{recodes[key]}',
                         f'{self.Payload.QuestionDescription} - {choices[key].Display}', value_labels])

        return rows


class SideBySideQuestion(SurveyQuestion):

    def __init__(self, items, **kwargs):

        super().__init__(items, **kwargs)

    @staticmethod
    def is_multi_answer(additional_question):
        return additional_question.SubSelector == 'MultipleAnswer' or additional_question.Selector == 'TE'

    def _variable_name_(self, aq_id, additional_question, choice_id, answer_value=''):

        choice_data_export_tags = additional_question.get('ChoiceDataExportTags')
        answer_tag = additional_question.get('AnswerDataExportTag')
        var_name_base = choice_data_export_tags[choice_id] if choice_data_export_tags else \
            f'{self.Payload.DataExportTag}_{aq_id}'
        var_name_aq_leaf = answer_tag if answer_tag is not None else choice_id
        var_name = f'{var_name_base}_{var_name_aq_leaf}' if answer_value == '' else \
            f'{var_name_base}_{var_name_aq_leaf}_{answer_value}'

        return var_name

    def _variable_label_(self, additional_question, choice_id, answer_id=None):

        answers = additional_question.Answers
        var_label = f'{self.Payload.QuestionDescription} - {additional_question.QuestionText}' + \
            f' - {additional_question.Choices[choice_id].Display}' + \
                    ('' if answer_id is None else f' {answers[answer_id].Display}')
        return var_label

    @staticmethod
    def _value_labels_(additional_question, answer_id=None):

        var_naming = additional_question.VariableNaming if len(additional_question.VariableNaming) > 0 else \
            {key: value.Display for key, value in additional_question.Answers.items()}
        if additional_question.Selector == 'TE':
            value_labels = None
        elif answer_id is not None:
            value_labels = {1: var_naming[answer_id]}
        elif len(additional_question.RecodeValues) > 0:
            value_labels = {value: var_naming[answer_id]
                            for answer_id, value in additional_question.RecodeValues.items()}
        else:
            value_labels = {key: value.Display for key, value in additional_question.Answers.items()}

        return value_labels
        #return "{\n" + "\n".join(f"{key}: {value}" for key, value in value_labels.items()) + "\n}" \
        #    if value_labels is not None else value_labels

    def variable_info(self):

        choice_order = self.Payload.ChoiceOrder

        rows = []

        # AdditonalQuestions represents the 'columns' of a SideBySide question
        for aq_id, aq_data in self.Payload.AdditionalQuestions.items():

            # Choices represent the 'Statements' of a SideBySide quetion
            for position, choice_id in enumerate(choice_order):
                choice = aq_data.Choices[choice_id]
                choice_has_text_entry = choice.get('TextEntry') is not None

                # How a question translates to variables depends, much like the matrix, upon whether a column
                # is SingleAnswer or MultipleAnswer
                # SingleAnswer questions yield a single variable per statement per column,
                # While MulitpleAnswer questions yield one variable per answer per statement per column
                if self.is_multi_answer(aq_data):

                    answers = {key: key for key, value in aq_data.Answers.items()} if len(aq_data.RecodeValues) == 0 \
                        else aq_data.RecodeValues
                    for answer_id, answer_value in answers.items():
                        var_name = self._variable_name_(aq_id, aq_data, choice_id, answer_value=answer_value)
                        var_label = self._variable_label_(aq_data, choice_id, answer_id=answer_id)
                        value_labels = self._value_labels_(aq_data, answer_id=answer_id)
                        rows.append([self.Payload.QuestionID, var_name, var_label, value_labels])

                        # Some statements may have a Text entry option, which yields an additional variable
                        if choice_has_text_entry:
                            rows.append((self.Payload.QuestionID, f'{var_name}_TEXT', f'{var_label} - Text', None))
                else:
                    var_name = self._variable_name_(aq_id, aq_data, choice_id)
                    var_label = self._variable_label_(aq_data, choice_id)
                    value_labels = self._value_labels_(aq_data)
                    rows.append([self.Payload.QuestionID, var_name, var_label, value_labels])

                    # Some statements may have a Text entry option, which yields an additional variable
                    if choice_has_text_entry:
                        rows.append([self.Payload.QuestionID, f'{var_name}_TEXT', f'{var_label} - Text', None])
        return rows


class SliderQuestion(SurveyQuestion):

    def __init__(self, items, **kwargs):
        super().__init__(items, **kwargs)

    def variable_info(self):
        choices = self.Payload.Choices
        choice_order = self.Payload.ChoiceOrder
        rows = []

        for key in choice_order:
            var_name = self._sanitize_for_spss_(f'{self.Payload.DataExportTag}_{str(key)}')
            var_label = f'{self.Payload.QuestionDescription} - {choices[key].Display}'
            rows.append([self.Payload.QuestionID, var_name, var_label, None])

        return rows


class TextEntryQuestion(SurveyQuestion):

    def __init__(self, items, **kwargs):
        super().__init__(items, **kwargs)

    def variable_info(self):

        rows = [[self.Payload.QuestionID, self.Payload.DataExportTag, self.Payload.QuestionDescription, None]]

        return rows
