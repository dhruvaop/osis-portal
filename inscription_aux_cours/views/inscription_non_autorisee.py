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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from osis_inscription_cours_sdk.model.autorise_inscrire_aux_cours import AutoriseInscrireAuxCours
from osis_program_management_sdk.model.programme import Programme

from base.models.person import Person
from inscription_aux_cours.services.autorisation import AutorisationService
from inscription_aux_cours.services.periode import PeriodeInscriptionAuxCoursService
from program_management.services.programme import ProgrammeService


class InscriptionNonAutoriseeView(LoginRequiredMixin, TemplateView):
    permission_required = "base.is_student"
    name = 'non-autorisee'
    template_name = "inscription_aux_cours/non_autorisee.html"

    @cached_property
    def person(self) -> 'Person':
        return Person.objects.get(user=self.request.user)

    @property
    def code_programme(self) -> str:
        return self.kwargs['code_programme']

    @cached_property
    def annee_academique(self) -> 'int':
        return PeriodeInscriptionAuxCoursService().get_annee(self.person)

    @cached_property
    def programme(self) -> 'Programme':
        return ProgrammeService.rechercher(self.person, annee=self.annee_academique, codes=[self.code_programme])[0]

    @cached_property
    def autorisation(self) -> 'AutoriseInscrireAuxCours':
        return AutorisationService().est_autorise(self.person, self.code_programme)

    def get(self, request, *args, **kwargs):
        if self.autorisation.autorise:
            return redirect(reverse('inscription-aux-cours:selectionner-formation'))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "raison": self.autorisation.msg,
            'person': self.person,
            'programme': self.programme,
        }
