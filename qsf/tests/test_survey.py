import qsf
import typing
import openpyxl
import docx
survey = qsf.Survey(r'g:\MAP.qsf')  # type: qsf.survey._Survey

cb = survey.codebook()  # type: typing.Union[openpyxl.Workbook, docx.Document]

cb.save(r'g:\test_MAP.xlsx')