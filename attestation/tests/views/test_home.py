##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import datetime
import json

import mock
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import MultipleObjectsReturned
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from mock import patch
from osis_reference_sdk.model.academic_calendar import AcademicCalendar
from osis_reference_sdk.model.paginated_academic_calendars import PaginatedAcademicCalendars
from rest_framework import status

import attestation.views.home
from attestation.views.home import _check_display_warning_invoice_not_available_yet
from base.tests.factories.person import PersonFactory
from base.tests.factories.student import StudentFactory

STUDENT_REGISTRATION_ID = "70531800"

MULTIPLE_STUDENT_ERROR = _(
    "A problem was detected with your registration : 2 registration id's are "
    "linked to your user.</br> Please contact <a href="
    "\"{registration_department_url}\" target=\"_blank\">the Registration "
    "department</a>. Thank you."
).format(registration_department_url=settings.REGISTRATION_ADMINISTRATION_URL)


class HomeTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('attestation_home')
        cls.person = PersonFactory()

        students_group = Group.objects.create(name='students')
        cls.permission = Permission.objects.get(codename="is_student")
        students_group.permissions.add(cls.permission)

    def setUp(self):
        self.client.force_login(self.person.user)

        self.discriminate_user_patcher = mock.patch(
            "base.business.student.find_by_user_and_discriminate",
        )
        self.mocked_discriminate_user = self.discriminate_user_patcher.start()
        self.addCleanup(self.discriminate_user_patcher.stop)

        self.academic_calendar_row = AcademicCalendar(**{
            'reference': 'REFERENCE',
            'title': 'TITLE',
            'data_year': 2021,
            'start_date': datetime.date.today(),
            'end_date': datetime.date.today()
        })
        self.academic_calendar_list_patcher = mock.patch(
            "reference.services.academic_calendar.AcademicCalendarService.get_academic_calendar_list",
            return_value=PaginatedAcademicCalendars(**{'results': [self.academic_calendar_row]})
        )
        self.mocked_academic_calendar_list = self.academic_calendar_list_patcher.start()
        self.addCleanup(self.academic_calendar_list_patcher.stop)

    def test_without_being_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/login/?next={self.url}')

    def test_with_user_not_a_student(self):
        response = self.client.get(self.url, follow=True)

        self.assertTemplateUsed(response, "access_denied.html")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_with_multiple_students_assigned_same_person(self):
        StudentFactory(person=self.person)
        self.mocked_discriminate_user.side_effect = MultipleObjectsReturned
        response = self.client.get(self.url, follow=True)

        self.assertTemplateUsed(response, "dashboard.html")

        messages = list(response.context['messages'])

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, MULTIPLE_STUDENT_ERROR)

    @patch('attestation.queues.student_attestation_status.fetch_json_attestation_statuses', side_effect=lambda x: None)
    def test_when_not_receive_attestation_statuses(self, mock_fetch_json_attestation_statuses):
        a_student = StudentFactory(person=self.person)
        self.mocked_discriminate_user.return_value = a_student
        response = self.client.get(self.url, follow=True)

        self.assertTrue(mock_fetch_json_attestation_statuses.called)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'attestation_home_student.html')

        self.assertEqual(response.context['student'], a_student)

        self.assertFalse(response.context['attestations'])
        self.assertFalse(response.context['current_year'])

    @patch('attestation.queues.student_attestation_status.fetch_json_attestation_statuses',
           side_effect=lambda x: {'current_year': 2015, 'attestations': [], 'registration_id': STUDENT_REGISTRATION_ID})
    def test_when_receive_attestation_statuses(self, mock_fetch_json_attestation_statuses):
        a_student = StudentFactory(person=self.person, registration_id=STUDENT_REGISTRATION_ID)
        self.mocked_discriminate_user.return_value = a_student
        response = self.client.get(self.url, follow=True)

        self.assertTrue(mock_fetch_json_attestation_statuses.called)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'attestation_home_student.html')

        self.assertEqual(response.context['student'], a_student)
        self.assertEqual(response.context['current_year'], 2015)

        self.assertFalse(response.context['attestations'])

    @patch('attestation.queues.student_attestation_status.fetch_json_attestation_statuses',
           side_effect=lambda x: {'current_year': 2015, 'attestations': [], 'registration_id': STUDENT_REGISTRATION_ID})
    def test_when_registration_id_doesnt_match(self, mock_fetch_json_attestation_statuses):
        self.mocked_discriminate_user.return_value = StudentFactory(person=self.person)
        with self.assertRaises(Exception) as e:
            self.client.get(self.url, follow=True)

        self.assertTrue(mock_fetch_json_attestation_statuses.called)
        self.assertEqual(str(e.exception), _('Registration fetched doesn\'t match with student registration_id'))

    def test_when_no_student_find_by_user(self):
        self.person.user.user_permissions.add(self.permission)
        self.mocked_discriminate_user.return_value = None
        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'attestation_home_student.html')

        self.assertFalse(response.context['attestations'])
        self.assertFalse(response.context['student'])
        self.assertFalse(response.context['current_year'])

    def test_check_display_warning_invoice_not_available_yet(self):
        with open("attestation/tests/resources/attestations.json") as f:
            attestation_statuses_all_years_json_dict = json.load(f)
        attestations = attestation_statuses_all_years_json_dict.get('attestationStatusesAllYears')
        self.assertFalse(_check_display_warning_invoice_not_available_yet(2020, attestations))
        self.assertTrue(_check_display_warning_invoice_not_available_yet(2021, attestations))


class TestRegistrationIdMessage(TestCase):
    def test_generate_message_with_registration_id(self):
        given_json_message = attestation.views.home._make_registration_json_message('1111111')
        expected_json_message = json.loads('{"registration_id" : "1111111"}')
        self.assertJSONEqual(given_json_message, expected_json_message)

    def test_generate_message_without_registration_id(self):
        given_json_message = attestation.views.home._make_registration_json_message(None)
        self.assertIsNone(given_json_message)
