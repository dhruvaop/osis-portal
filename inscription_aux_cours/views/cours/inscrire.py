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
from typing import Optional

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from base.services.utils import ServiceException
from inscription_aux_cours.services.cours import CoursService
from inscription_aux_cours.views.common import InscriptionAuxCoursViewMixin


@method_decorator(require_POST, name='dispatch')
class InscrireAUnCoursView(LoginRequiredMixin, InscriptionAuxCoursViewMixin, TemplateView):
    name = 'inscrire-cours'

    # TemplateView
    template_name = "inscription_aux_cours/cours/desinscrire.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.erreurs = []

    @property
    def code_mini_formation(self) -> Optional[str]:
        return self.request.POST.get('code_mini_formation')

    @property
    def code_cours(self) -> str:
        return self.request.POST.get('code_cours')

    def post(self, request, *args, **kwargs):
        try:
            self.inscrire_a_un_cours()
        except ServiceException as e:
            self.erreurs = e.messages
        return super().get(request, *args, **kwargs)

    def inscrire_a_un_cours(self):
        CoursService().inscrire(
            self.person,
            code_programme=self.code_programme,
            code_cours=self.code_cours,
            code_mini_formation=self.code_mini_formation,
            hors_formulaire=False
        )

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "code_mini_formation": self.code_mini_formation,
            "code_cours": self.code_cours,
            "erreurs": self.erreurs
        }
