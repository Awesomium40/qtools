import qtools
from qtools import *
import os
import unittest


class TestExportClient(unittest.TestCase):

    def test_build_client(self):

        # test that ExportClient correctly gets vars from OS environ
        ec = ExportClient()
        self.assertEqual(os.environ.get('Q_API_TOKEN'), qtools.security.decrypt(ec._token, ec._tkn_salt, ec._pass))
        self.assertEqual(os.environ.get('Q_DATA_CENTER'),
                         qtools.security.decrypt(ec._data_center, ec._dc_salt, ec._pass))

        # test that ExportClient correctly gets vars when vars specified as OS environ keys
        ec = ExportClient(data_center='Q_DATA_CENTER', token='Q_API_TOKEN')
        self.assertEqual(os.environ.get('Q_API_TOKEN'), qtools.security.decrypt(ec._token, ec._tkn_salt, ec._pass))
        self.assertEqual(os.environ.get('Q_DATA_CENTER'),
                         qtools.security.decrypt(ec._data_center, ec._dc_salt, ec._pass))

        # test that ExportClient correctly gets vars when specified as values.
        # Insert your own values here to test and remove return statement
        ec = ExportClient(data_center='', token='')
        self.assertEqual(os.environ.get('Q_API_TOKEN'), qtools.security.decrypt(ec._token, ec._tkn_salt, ec._pass))
        self.assertEqual(os.environ.get('Q_DATA_CENTER'),
                         qtools.security.decrypt(ec._data_center, ec._dc_salt, ec._pass))

    def test_export_responses(self):

        # Note that in order for this test to work, need to insert your own data_center and token values
        ec = ExportClient()
        ec.export_responses(out_folder=r'ResponseTest', survey_id='SV_0wiQvxuFUDgqWWh')

        ec.export_responses(out_folder='ResponseTest2', limit=1, questionIds=["QID52", "QID1"], useLabels=True)

    def test_list_surveys(self):
        # Need to test with your own surveys
        actual_data = {"SV_0wiQvxuFUDgqWWh": "Project RAVEN 1M Survey- BROWN",
                       "SV_2spdxBjZ6m0xQsl": "Provider Assessment (M&E - SA ATTC)",
                       "SV_6t9ZJUV8ju9Hu0B": "Project RAVEN Post-Intervention Survey - BROWN",
                       "SV_9oa19AX532702Pj": "REMOTE Final Baseline Survey - BROWN",
                       "SV_bsHkUbeZBMt8l93": "Final Baseline Survey - BROWN",
                       "SV_bxvQPfEAx02d7QV": "Project MAP BL Survey codebook test",
                       "SV_5j2iClJcQnNimgd": "Depressive Symptoms (CESD-10)",
                       "SV_6llqAsI32tDsPSl": "SurveyQuestionTest",
                       "SV_8iW8s9rBGb8LbRX": "UCLA Loneliness Scale",
                       "SV_9slKtyMOH11OceN": "Short Inventory of Problems (SIP)"}

        ec = ExportClient()
        survey_list = ec.list_surveys()

        self.assertEqual(len(survey_list), len(actual_data))
        for key, value in survey_list.items():
            self.assertEqual(value, actual_data[key])

    def test_prompt_for_surveys(self):
        ec = ExportClient()

        survey_id = ec._prompt_for_survey_()
        print(survey_id)

    def test_export_codebook(self):
        ec = ExportClient()

        data = ec.export_codebook(survey_id='SV_7ZJKWQhp7JjdhBP')
        data.save('d:\export.xlsx')
        d = 25

    def test_survey(self):

        ec = ExportClient()
        data = ec.export_survey_definition(survey_id='SV_bsHkUbeZBMt8l93', format=Format.TXT)
        survey = qtools.qsf.Survey(data)

        question = survey.get_question('QID44')

        print(question.Payload.QuestionText)

