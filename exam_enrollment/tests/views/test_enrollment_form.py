##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
import json
import random
import warnings
from types import SimpleNamespace
from unittest.mock import patch

import mock
from django.conf import settings
from django.contrib.auth.models import User, Group, Permission
from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.offer_enrollment import OfferEnrollmentFactory
from base.tests.models import test_student, test_person, test_academic_year, \
    test_learning_unit_enrollment, test_learning_unit_year
from exam_enrollment.enums.covid_exam_choice import CovidExamChoice
from exam_enrollment.tests.factories.exam_enrollment_request import ExamEnrollmentRequestFactory
from exam_enrollment.views.enrollment_form import _exam_enrollment_form_submission_message


def load_json_file(path):
    with open(path, 'r') as fp:
        return json.load(fp)


def _create_group(name):
    group = Group(name=name)
    group.save()
    return group


HTTP_RESPONSE_NOTFOUND = 404


class ExamEnrollmentFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = test_academic_year.create_academic_year()
        group = _create_group('students')
        group.permissions.add(Permission.objects.get(codename='is_student'))
        cls.user = User.objects.create_user(username='jsmith', email='jsmith@localhost', password='secret')
        cls.user_not_student = User.objects.create_user(
            username='pjashar',
            email='pjashar@localhost',
            password='secret'
        )
        cls.user.groups.add(group)
        cls.person = test_person.create_person_with_user(cls.user, first_name="James", last_name="Smith")
        cls.student = test_student.create_student_with_registration_person("12345678", cls.person)
        cls.educ_group_year = EducationGroupYearFactory(
            acronym='SINF1BA',
            title='Bechelor in informatica',
            academic_year=cls.academic_year,
        )
        cls.url = "/exam_enrollment/{acronym}/{year}/form/".format(
            acronym=cls.educ_group_year.acronym,
            year=cls.academic_year.year
        )
        cls.correct_exam_enrol_form = load_json_file(
            "exam_enrollment/tests/resources/exam_enrollment_form_example.json"
        )
        cls.current_academic_year = test_academic_year.create_academic_year_current()
        cls.off_enrol = OfferEnrollmentFactory(
            student=cls.student,
            education_group_year=EducationGroupYearFactory(academic_year=cls.current_academic_year)
        )
        learn_unit_year = test_learning_unit_year.create_learning_unit_year({
            'acronym': 'LDROI1234',
            'specific_title': 'Bachelor in law',
            'academic_year': cls.academic_year
        })
        cls.learn_unit_enrol = test_learning_unit_enrollment.create_learning_unit_enrollment(
            cls.off_enrol,
            learn_unit_year
        )

    def setUp(self) -> None:
        self.client.force_login(self.user)

        # Mock the OSIS Remote API Call
        self.offer_enrollment_row = SimpleNamespace(**{
            'acronym': self.off_enrol.education_group_year.acronym,
            'title': self.off_enrol.education_group_year.title,
            'year': self.off_enrol.education_group_year.academic_year.year,
        })

        self.offer_enrollment_patcher = mock.patch(
            "exam_enrollment.views.enrollment_form.ExamEnrollmentForm.offer_enrollment",
            new_callable=mock.PropertyMock,
            return_value=self.offer_enrollment_row
        )
        self.mocked_offer_enrollment = self.offer_enrollment_patcher.start()
        self.addCleanup(self.offer_enrollment_patcher.stop)

    def test_json_form_content(self):
        form = self.correct_exam_enrol_form
        self.assertTrue(form.get('registration_id'))
        self.assertTrue(form.get('current_number_session'))
        exam_enrollments = form.get('exam_enrollments')
        self.assertTrue(exam_enrollments)
        random_exam_enrol_position = random.randrange(len(exam_enrollments))
        random_exam_enrol = exam_enrollments[random_exam_enrol_position]
        self.assertTrue('credits' in random_exam_enrol.keys())
        self.assertTrue('credited' in random_exam_enrol.keys())
        self.assertTrue('enrolled_by_default' in random_exam_enrol.keys())
        self.assertTrue('can_enrol_to_exam' in random_exam_enrol.keys())
        self.assertTrue('session_1' in random_exam_enrol.keys()
                        or 'session_2' in random_exam_enrol.keys()
                        or 'session_3' in random_exam_enrol.keys())
        self.assertTrue(random_exam_enrol.get('learning_unit_year'))

    @patch('base.models.learning_unit_enrollment.LearningUnitEnrollment.objects.filter')
    @patch("exam_enrollment.views.enrollment_form.ExamEnrollmentForm.ask_exam_enrollment_form")
    def test_exam_enrollment_form(self, fetch_json, mock_find_learn_unit_enrols):
        mock_find_learn_unit_enrols.return_value = [self.learn_unit_enrol]
        fetch_json.return_value = self.correct_exam_enrol_form
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, 'exam_enrollment_form.html')
        returned_data = response.context[-1]
        self.assertIn('exam_enrollments', returned_data)
        self.assertIn('student', returned_data)
        self.assertIn('current_number_session', returned_data)
        self.assertIn('academic_year', returned_data)
        self.assertIn('year', returned_data)
        self.assertIn('program_code', returned_data)
        self.assertIn('title', returned_data)

    @patch("exam_enrollment.views.enrollment_form.ExamEnrollmentForm.ask_exam_enrollment_form")
    def test_outside_score_encoding_period(self, fetch_json):
        fetch_json.return_value = None
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse('dashboard_home'))

    def test_case_user_is_not_student(self):
        self.client.force_login(self.user_not_student)
        response = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(response, 'access_denied.html')

    @patch('exam_enrollment.views.enrollment_form.ExamEnrollmentForm.ask_exam_enrollment_form')
    def test_navigation_student_has_programs_but_returned_form_is_none(self, mock_fetch_exam_form):
        mock_fetch_exam_form.return_value = None
        an_url = reverse(
            'exam_enrollment_form',
            args=[self.educ_group_year.acronym, self.educ_group_year.academic_year.year]
        )
        response = self.client.get(an_url, follow=True)
        self.assertRedirects(response, reverse('dashboard_home'))

    @patch("exam_enrollment.views.enrollment_form.ExamEnrollmentForm.ask_exam_enrollment_form")
    def test_case_exam_enrollment_form_contains_error_message(self, mock_fetch_json):
        form = self.correct_exam_enrol_form
        form['error_message'] = "an_error_message_key"
        mock_fetch_json.return_value = form
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse('dashboard_home'))

    @patch('base.models.learning_unit_enrollment.LearningUnitEnrollment.objects.filter')
    @patch("exam_enrollment.models.exam_enrollment_request.get_by_student_and_offer_year_acronym_and_fetch_date")
    def test_case_exam_enrollment_form_outside_period(self,
                                                      mock_get_exam_enrollment_request,
                                                      mock_find_learn_unit_enrols):
        mock_find_learn_unit_enrols.return_value = [self.learn_unit_enrol]
        mock_get_exam_enrollment_request.return_value = ExamEnrollmentRequestFactory(
            document='{"error_message": "outside_exam_enrollment_period",'
                     '"registration_id":" 12345678",'
                     '"current_number_session": null,'
                     '"legende": null,'
                     '"offer_year_acronym": "DROI1BA",'
                     '"exam_enrollments": null}'
        )
        response = self.client.get(self.url)
        error_message = response.context.get("error_message")
        self.assertEqual(
            error_message,
            _("You are outside the exams enrollment period")
        )

    @patch('base.models.learning_unit_enrollment.LearningUnitEnrollment.objects.filter')
    @patch("exam_enrollment.models.exam_enrollment_request.get_by_student_and_offer_year_acronym_and_fetch_date")
    def test_case_exam_enrollment_form_not_available(self,
                                                     mock_get_exam_enrollment_request,
                                                     mock_find_learn_unit_enrols):
        mock_find_learn_unit_enrols.return_value = [self.learn_unit_enrol]
        mock_get_exam_enrollment_request.return_value = ExamEnrollmentRequestFactory(
            document='{"error_message": "no_exam_enrollment_avalaible",'
                     '"registration_id":" 12345678",'
                     '"current_number_session": null,'
                     '"legende": null,'
                     '"offer_year_acronym": "DROI1BA",'
                     '"exam_enrollments": null}'
        )
        response = self.client.get(self.url)
        error_message = response.context.get("error_message")
        self.assertEqual(
            error_message,
            _("Exam enrollment is not available")
        )

    @patch('base.models.learning_unit_enrollment.LearningUnitEnrollment.objects.filter')
    @patch("exam_enrollment.models.exam_enrollment_request.get_by_student_and_offer_year_acronym_and_fetch_date")
    def test_case_exam_enrollment_form_no_learning_unit_enrollment_found(
            self, mock_get_exam_enrollment_request, mock_find_learn_unit_enrols):
        mock_find_learn_unit_enrols.return_value = [self.learn_unit_enrol]
        mock_get_exam_enrollment_request.return_value = ExamEnrollmentRequestFactory(
            document='{"error_message": "no_learning_unit_enrollment_found",'
                     '"registration_id":" 12345678",'
                     '"current_number_session": null,'
                     '"legende": null,'
                     '"offer_year_acronym": "DROI1BA",'
                     '"exam_enrollments": null}'
        )
        response = self.client.get(self.url)
        error_message = response.context.get("error_message")
        self.assertEqual(
            error_message,
            _("no_learning_unit_enrollment_found").format(self.educ_group_year.acronym)
        )

    @patch('base.models.learning_unit_enrollment.LearningUnitEnrollment.objects.filter')
    @patch("exam_enrollment.models.exam_enrollment_request.get_by_student_and_offer_year_acronym_and_fetch_date")
    def test_case_exam_enrollment_form_no_error(
            self, mock_get_exam_enrollment_request, mock_find_learn_unit_enrols):
        mock_find_learn_unit_enrols.return_value = [self.learn_unit_enrol]
        mock_get_exam_enrollment_request.return_value = ExamEnrollmentRequestFactory(
            document='{"error_message": null,'
                     '"registration_id":" 12345678",'
                     '"current_number_session": null,'
                     '"legende": null,'
                     '"offer_year_acronym": "DROI1BA",'
                     '"exam_enrollments": null}'
        )
        response = self.client.get(self.url)
        error_message = response.context.get("error_message")
        self.assertIsNone(error_message)

    @patch('base.models.learning_unit_enrollment.LearningUnitEnrollment.objects.filter')
    @patch('exam_enrollment.views.enrollment_form.ExamEnrollmentForm.ask_exam_enrollment_form')
    def test_navigation_student_has_programs_with_data(self, mock_fetch_exam_form, mock_find_learn_unit_enrols):
        mock_fetch_exam_form.return_value = {
            'exam_enrollments': [],
            'current_number_session': 0,
        }
        mock_find_learn_unit_enrols.return_value = [self.learn_unit_enrol]
        an_url = reverse(
            'exam_enrollment_form',
            args=[self.educ_group_year.acronym, self.educ_group_year.academic_year.year]
        )
        response = self.client.get(an_url, follow=True)
        self.assertEqual('exam_enrollment_form.html', response.templates[0].name)

    if hasattr(settings, 'QUEUES') and settings.QUEUES:
        @mock.patch("osis_common.queue.queue_sender.send_message")
        @mock.patch("exam_enrollment.models.exam_enrollment_submitted.insert_or_update_document")
        def test_exam_enrollment_form_submission_message(self, mock_doc, send_message):
            warnings.warn(
                "The field named 'etat_to_inscr' is only used to call EPC services. It should be deleted when the exam "
                "enrollment business will be implemented in Osis (not in EPC anymore). "
                "The flag 'is_enrolled' should be sufficient for Osis.",
                DeprecationWarning
            )
            send_message.return_value = None
            post_data = {
                "chckbox_exam_enrol_sess1_LPHYS1234": "on",
                "etat_to_inscr_current_session_LPHYS1234": "I",
                "chckbox_exam_enrol_sess1_LBIO4567": "",
                "etat_to_inscr_current_session_LBIO4567": "None",
                "chckbox_exam_enrol_sess1_LDROI1111": "None",
                "etat_to_inscr_current_session_LDROI1111": "None",
                "current_number_session": 1,
                "testwe_exam": CovidExamChoice.PAS_SUR_SITE,
                "teams_exam": CovidExamChoice.SUR_SITE,
                'moodle_exam': CovidExamChoice.NON_CONCERNE
            }
            response = self.client.post(self.url, post_data)
            result = _exam_enrollment_form_submission_message(
                response.wsgi_request,
                self.student,
                self.educ_group_year.acronym,
                self.educ_group_year.academic_year.year
            )
            self.assert_correct_data_structure(result)
            self.assert_none_etat_to_inscr_not_in_submitted_form(result.get('exam_enrollments'))

    def assert_correct_data_structure(self, result):
        exam_enrollment_expected = {
            "acronym": "LPHYS1234",
            "is_enrolled": True,
            "etat_to_inscr": "I"
        }
        expected_result = {
            "registration_id": self.student.registration_id,
            "offer_year_acronym": self.educ_group_year.acronym,
            "year": self.educ_group_year.academic_year.year,
            "exam_enrollments": [exam_enrollment_expected],
            "testwe_exam": CovidExamChoice.PAS_SUR_SITE,
            "teams_exam": CovidExamChoice.SUR_SITE,
            'moodle_exam': CovidExamChoice.NON_CONCERNE
        }
        self.assertEqual(len(result), len(expected_result))
        self.assertEqual(expected_result.get('registration_id'), result.get('registration_id'))
        self.assertEqual(expected_result.get('offer_year_acronym'), result.get('offer_year_acronym'))
        self.assertEqual(expected_result.get('year'), result.get('year'))
        exam_enrollments = result.get('exam_enrollments')
        self.assertEqual(len(exam_enrollments), 1)
        for exam_enrol in expected_result.get('exam_enrollments'):
            self.assertIn(exam_enrol, exam_enrollments)

    def assert_none_etat_to_inscr_not_in_submitted_form(self, exam_enrollments):
        exam_enrollments_unexpected = [{
            "acronym": "LBIO4567",
            "is_enrolled": False,
            "etat_to_inscr": None
        },
            {
                "acronym": "LDROI1111",
                "is_enrolled": False,
                "etat_to_inscr": None
            }]
        for index in range(0, len(exam_enrollments_unexpected)):
            self.assertNotIn(exam_enrollments_unexpected[index], exam_enrollments)

    @patch('base.models.learning_unit_enrollment.LearningUnitEnrollment.objects.filter')
    def test_case_student_has_no_learning_unit_enrollment(self, mock_find):
        mock_find.return_value = None
        off_year_enrol = OfferEnrollmentFactory(
            student=self.student,
            education_group_year=EducationGroupYearFactory(academic_year=self.current_academic_year)
        )
        response = self.client.get(
            reverse(
                'exam_enrollment_form',
                args=[off_year_enrol.education_group_year.acronym, self.current_academic_year.year]
            ),
            follow=True
        )
        self.assertRedirects(response, reverse('dashboard_home'))
