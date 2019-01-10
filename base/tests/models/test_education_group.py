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

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory


class EducationGroupTest(TestCase):
    def setUp(self):
        self.education_group = EducationGroupFactory()
        self.education_group2 = EducationGroupFactory()
        self.academic_year = AcademicYearFactory(year=2018)
        self.academic_year2 = AcademicYearFactory(year=2020)
        self.education_group_year1 = EducationGroupYearFactory(
            education_group= self.education_group,
            academic_year=self.academic_year
        )
        self.education_group_year2 = EducationGroupYearFactory(
            education_group= self.education_group,
            academic_year=self.academic_year2
        )


    def test_most_recent_acronym(self):
        self.assertEqual(self.education_group.most_recent_acronym, self.education_group_year2.acronym)
        self.assertEqual(self.education_group2.most_recent_acronym, None)