from openpyxl.cell.cell import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo
from .abc import SurveyObjectBase
from .questions import *
import openpyxl


class _Survey(SurveyObjectBase):

    COL_HEADERS = ["QuestionID", 'Variable Name', "Variable Label", "Value Labels"]
    WIDTHS = {"A": 10.3, "B": 21.5, "C": 44.3, "D": 27.9}
    ALIGNMENTS = {"A": openpyxl.styles.Alignment(),
                  "B": openpyxl.styles.Alignment(),
                  "C": openpyxl.styles.Alignment(wrapText=True),
                  "D": openpyxl.styles.Alignment(wrapText=True)}

    TBL_STYLE = TableStyleInfo(name="TableStyleMedium8",
                               showRowStripes=True)

    _question_map_ = {'Matrix': MatrixQuestion,
                      'MC': MultiChoiceQuestion,
                      "RO": RankOrderQuestion,
                      "SQ": SliderQuestion,
                      "TE": TextEntryQuestion,
                      'SBS': SideBySideQuestion}

    def __init__(self, items, **kwargs):
        super().__init__(items, **kwargs)

    def get_question(self, question_id):
        """
        s.get_question(question_id) -> SurveyQuestion
        finds the question with ID question_id and returns it
        :param question_id: the ID of the question to find
        :return: SurveyQuestion
        :raises ValueError: if no question can be found
        """
        question = next(filter(lambda x: x.Element == 'SQ' and x.Payload.QuestionID == question_id,
                               self.SurveyElements), None)

        if question is None:
            raise ValueError(f'Question {question_id} not found')

        return question

    def __xl__codebook(self):

        blocks = next(filter(lambda x: x.get('Element') == 'BL', self.SurveyElements))
        payload = blocks.Payload
        block_items = filter(lambda x: x.get('Type') in ("Default", "Standard"),
                             payload if isinstance(payload, list) else payload.values())

        trash = next(filter(lambda x: x.get('Type') == 'Trash', payload if isinstance(payload, list)
                            else payload.values()))
        trash_ids = [x.QuestionID for x in trash.BlockElements if hasattr(x, 'QuestionID')]
        wb = openpyxl.Workbook()

        for i, block in enumerate(block_items):
            ws = wb.active if i == 0 else wb.create_sheet()
            title = self._sanitize_for_spss_(block.Description)
            title = title if len(title) < 31 else title[:30]
            ws.title = title
            for key, value in self.WIDTHS.items():
                ws.column_dimensions[key].width = value

            ws.append(self.COL_HEADERS)
            questions = filter(lambda x: x.Type == "Question" and x.QuestionID not in trash_ids,
                               block.BlockElements)

            for q in questions:
                question_id = q.QuestionID
                question = next(filter(lambda x: x.Element == 'SQ' and x.Payload.QuestionID == question_id,
                                       self.SurveyElements))
                try:
                    for row in question.variable_info():
                        ws.append(row)
                except Exception as err:
                    print(f"Unable to insert data for question {question_id}. Error was \n{err}")

            # Make a table
            max_row = ws.max_row
            if max_row > 2:
                tbl = Table(displayName=title, ref="A1:D{0}".format(max_row))
                tbl.tableStyleInfo = self.TBL_STYLE
                ws.add_table(tbl)

            # Styles have to be set on cells one at a time or they won't take
            for row_index, row in enumerate(ws.iter_rows(), 1):
                for column_index, cell in enumerate(row, 1):
                    column_letter = get_column_letter(column_index)
                    ws.cell(row_index, column_index).alignment = self.ALIGNMENTS.get(column_letter,
                                                                                     openpyxl.styles.Alignment())

        return wb

    def codebook(self, output_type='xlsx'):
        """

        :param output_type:
        :param var_info_only:
        :return:
        """

        if output_type == 'xlsx':
            return self.__xl__codebook()
        else:
            raise NotImplementedError("The output type '{0}' is not currently supported".format(output_type))
