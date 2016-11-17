##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.test import TestCase
from dashboard.tests import data_for_tests
from dashboard.views import score_encoding
from unittest.mock import patch


class ScoreEncodingTest(TestCase):
    def setUp(self):
        self.score_encoding = data_for_tests.create_score_encoding()
        self.global_id = self.score_encoding.global_id

    def test_get_score_sheet_if_present_in_db(self):
        document = score_encoding.get_score_sheet(self.global_id)
        self.assertJSONEqual(self.score_encoding.document, document, "Should return the document in db")

    @patch('osis_common.queue.queue_listener.Client.call')
    def test_get_score_sheet_if_not_present_in_db_with_timeout(self, mock_client_call):
        mock_client_call.return_value = None
        document = score_encoding.get_score_sheet("12012")
        self.assertIsNone(document, "Should timeout when waiting for document and return none")

    @patch('osis_common.queue.queue_listener.Client.call')
    def test_get_score_sheet_if_not_present_in_db_and_fetch(self, mock_client_call):
        expected = """{"msg":"response"}"""
        mock_client_call.return_value = expected.encode("utf-8")
        document = score_encoding.get_score_sheet("12012")
        self.assertJSONEqual(document, expected, "Should fetch document from queue")


