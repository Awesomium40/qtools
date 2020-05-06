from .abc import SurveyObject, SurveyQuestion

__all__ = ['MatrixQuestion', 'MultiChoiceQuestion', 'RankOrderQuestion', 'SideBySideQuestion',
           'SliderQuestion', 'TextEntryQuestion']


class MatrixQuestion(SurveyQuestion):

    def __init__(self, items, **kwargs):
        super().__init__(items, **kwargs)

    @property
    def is_multi_answer(self):
        return self.Payload.SubSelector in ('MultipleAnswer', 'DND')

    def variable_info(self):
        rows = []
        answers = self.Payload.Answers
        ans_order = [str(x) for x in self.Payload.AnswerOrder]
        choices = self.Payload.Choices
        choice_order = [str(x) for x in self.Payload.ChoiceOrder]
        data_export_tags = self.Payload.ChoiceDataExportTags
        qid = self.Payload.QuestionID
        question_type = self.Payload.QuestionType
        recode_values = self.Payload.get("RecodeValues")
        selector = self.Payload.Selector
        stem = self.Payload.QuestionDescription
        sub_selector = self.Payload.SubSelector
        var_name_base = self.Payload.DataExportTag
        var_naming = self.Payload.get("VariableNaming")

        for key in choice_order:
            leaf = choices[key].Display
            if self.is_multi_answer:
                for a_key in ans_order:
                    item_id = "{0}_{1}_{2}".format(qid, key,
                                                   recode_values[a_key] if recode_values is not None else a_key)
                    base = data_export_tags[key] if data_export_tags else "{0}_{1}".format(var_name_base, key)
                    var_name = self._sanitize_for_spss_("{0}_{1}".format(base, recode_values[a_key]
                                                        if recode_values is not None else a_key))
                    var_label = "{0} - {1} {2}".format(stem, choices[key].Display,
                                                     var_naming[a_key] if var_naming is not None else answers[key])
                    value_labels = SurveyObject((1, var_naming[a_key] if var_naming is not None else answers[key].Display))

                    rows.append(tuple((item_id, question_type, selector, sub_selector, stem, leaf, var_name,
                                       var_label, str(value_labels), None)))
            else:
                item_id = "{0}_{1}".format(qid, key)
                var_name = self._sanitize_for_spss_(data_export_tags[key] if data_export_tags else
                                                    "{0}_{1}".format(var_name_base, key))
                var_label = "{0} - {1}".format(stem, choices[key].Display)
                value_labels = SurveyObject(((recode_values[a_key] if recode_values is not None else a_key,
                                             var_naming[a_key] if var_naming is not None else answers[a_key].Display)
                                            for a_key in ans_order))
                rows.append(tuple((item_id, question_type, selector, sub_selector, stem, leaf, var_name,
                                   var_label, str(value_labels), None)))

        return rows


class MultiChoiceQuestion(SurveyQuestion):

    def __init__(self, items, **kwargs):
        super().__init__(items, **kwargs)

    @property
    def is_multi_answer(self):
        return self.Payload.Selector in ('MAVR', 'MAHR', 'MACOL')

    def variable_info(self):
        rows = []
        qid = self.Payload.QuestionID
        var_name_base = self.Payload.DataExportTag
        selector = self.Payload.Selector
        sub_selector = self.Payload.SubSelector
        q_type = self.Payload.QuestionType
        stem = self.Payload.QuestionText
        choices = self.Payload.Choices
        choice_order = [str(x) for x in self.Payload.ChoiceOrder]

        # Sometimes a response set will have recoded values. If so, need to retrieve them
        recode_values = self.Payload.get('RecodeValues')
        var_rename = self.Payload.get('VariableNaming')

        # How data translates to variables depends on if the question was SA or MA.
        # MA questions provide a variable for each possible choice,
        # SA questions provide a single variable representing the selection made from all choices
        if self.is_multi_answer:
            for key in choice_order:
                leaf = var_rename[key] if var_rename is not None else choices[key].Display
                var_name = self._sanitize_for_spss_("{0}_{1}".format(var_name_base, recode_values[key]
                                                    if recode_values is not None else key))

                value_labels = SurveyObject(((1, var_rename[key] if var_rename is not None else choices[key].Display),))
                var_label = "{0} {1}".format(self.Payload.QuestionDescription, var_rename[key]
                                             if var_rename is not None else choices[key].Display)

                rows.append(tuple((qid, q_type, selector, sub_selector, stem, leaf, var_name, var_label,
                                   str(value_labels), None)))
                if choices[key].get("TextEntry") in (True, "true"):
                    rows.append(tuple((qid, "TextEntry", None, None, stem, leaf, var_name + "_Text",
                                       var_label + " - Text", None, None)))

        else:
            leaf = None
            var_name = var_name_base
            value_labels = SurveyObject(((recode_values[key] if recode_values is not None else key,
                                         var_rename[key] if var_rename is not None else choices[key].Display)
                                        for key in choice_order))

            var_label = self.Payload.QuestionDescription
            rows.append(tuple((qid, q_type, selector, sub_selector, stem, leaf, var_name,
                               var_label, str(value_labels), None)))

            for choice in filter(lambda x: choices[x].get("TextEntry") in (True, "true"), choice_order):
                rows.append(tuple((qid, "TextEntry", None, None, stem, leaf, var_name + "_" + str(choice) + "_Text",
                                       var_label + " - Text", None, None)))

        return rows


class RankOrderQuestion(SurveyQuestion):

    def __init__(self, items, **kwargs):
        super().__init__(items, **kwargs)

    def variable_info(self):
        rows = []
        choices = self.Payload.Choices
        choice_order = self.Payload.ChoiceOrder
        recodes = self.Payload.RecodeValues

        for key in choice_order:
            rows.append(tuple((self.Payload.QuestionID, self.Payload.DataExportTag, self.Payload.QuestionType,
                        self.Payload.Selector, self.Payload.SubSelector, self.Payload.QuestionText,
                        choices.get(key).Display, None)))

        return rows


class SideBySideQuestion(SurveyQuestion):

    def __init__(self, items, **kwargs):

        super().__init__(items, **kwargs)

    def variable_info(self):
        choices = self.Payload.Choices
        columns = self.Payload.AdditionalQuestions
        choice_order = self.Payload.ChoiceOrder
        stem = self.Payload.QuestionText
        rows = []

        for col_number, col_data in columns.items():
            col_choices = col_data.Choices
            answers = col_data.Answers
            recode_values = col_data.get('RecodeValues')
            var_names = col_data.get('VariableNaming')

            for key in choice_order:
                item = col_choices.get(key)
                if item is None: continue
                leaf = "{0}: {1}".format(item.Display, col_data.QuestionText)


class SliderQuestion(SurveyQuestion):

    def __init__(self, items, **kwargs):
        super().__init__(items, **kwargs)

    def variable_info(self):
        min_value = self.Payload.Configuration.CSSliderMin
        max_value = self.Payload.Configuration.CSSliderMax
        decimal_places = self.Payload.Configuration.NumDecimals
        choices = self.Payload.Choices
        choice_order = self.Payload.ChoiceOrder
        stem = self.Payload.QuestionText
        validation = SurveyObject((("Min", min_value), ("Max", max_value), ("Decimals", decimal_places)))
        responses_txt = "Min: {0}\nMax: {1}\nDecimals: {2}".format(min_value, max_value, decimal_places)
        rows = []

        for key in choice_order:
            rows.append(tuple((self.Payload.QuestionID,
                               self._sanitize_for_spss_(self.Payload.DataExportTag + "_" + str(key)),
                               "Slider", self.Payload.Selector, None, stem, choices.get(key).Display,
                               None, str(validation))))

        return rows


class TextEntryQuestion(SurveyQuestion):

    def __init__(self, items, **kwargs):
        super().__init__(items, **kwargs)

    def variable_info(self):

        rows = [tuple((self.Payload.QuestionID, self.Payload.QuestionType, self.Payload.Selector, None,
                       self.Payload.QuestionText, None, self.Payload.DataExportTag, self.Payload.QuestionDescription,
                       None, str(self.validation())))]

        return rows
