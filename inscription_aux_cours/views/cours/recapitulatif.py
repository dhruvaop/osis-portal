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
from decimal import Decimal
from typing import List

import attr
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from osis_inscription_cours_sdk.model.programme_annuel_etudiant import ProgrammeAnnuelEtudiant

from education_group.services.mini_training import MiniTrainingService
from inscription_aux_cours.services.cours import CoursService
from inscription_aux_cours.views.common import InscriptionAuxCoursViewMixin
from learning_unit.services.learning_unit import LearningUnitService


@attr.dataclass(auto_attribs=True, frozen=True, slots=True)
class Inscription:
    code: str
    intitule: str
    credits: Decimal


@attr.dataclass(auto_attribs=True, frozen=True, slots=True)
class InscriptionsParContexte:
    intitule: str
    cours: List[Inscription]


@attr.dataclass(auto_attribs=True, frozen=True, slots=True)
class PropositionProgrammeAnnuel:
    inscriptions_par_contexte: List['InscriptionsParContexte']

    @property
    def total_credits(self) -> 'Decimal':
        return sum([Decimal(cours.credits) for contexte in self.inscriptions_par_contexte for cours in contexte.cours])


class RecapitulatifView(LoginRequiredMixin, InscriptionAuxCoursViewMixin, TemplateView):
    name = "recapitulatif"

    template_name = "inscription_aux_cours/cours/recapitulatif.html"

    @cached_property
    def programme_annuel(self) -> 'ProgrammeAnnuelEtudiant':
        return CoursService().recuperer_inscriptions(
            self.person,
            self.annee_academique,
            self.sigle_formation
        )

    @cached_property
    def details_cours(self):
        code_cours = [cours['code'] for cours in self.programme_annuel['tronc_commun']]
        code_cours += [
            cours['code']
            for mini_formation in self.programme_annuel['mini_formations']
            for cours in mini_formation['cours']
        ]
        result = LearningUnitService.search_learning_units(
            self.person,
            year=self.annee_academique,
            learning_unit_codes=code_cours
        )
        return {learning_unit['acronym']: learning_unit for learning_unit in result}

    @cached_property
    def details_mini_formation(self):
        codes_mini_formation = [mini_formation['code'] for mini_formation in self.programme_annuel['mini_formations']]
        result = MiniTrainingService().search(self.person, year=self.annee_academique, codes=codes_mini_formation)
        return {mini_formation.code: mini_formation for mini_formation in result}

    @cached_property
    def programme_annuel_avec_details_cours(self) -> 'PropositionProgrammeAnnuel':
        inscriptions_tronc_commun = InscriptionsParContexte(
            intitule=self.formation['title'],
            cours=self._build_cours(self.programme_annuel['tronc_commun'])
        )
        inscriptions_aux_mini_formations = [
            InscriptionsParContexte(
                intitule=self.details_mini_formation[mini_formation['code']]['title'],
                cours=self._build_cours(mini_formation['cours'])
            ) for mini_formation in self.programme_annuel['mini_formations']
        ]
        inscriptions = [inscriptions_tronc_commun] + inscriptions_aux_mini_formations if inscriptions_tronc_commun.cours else\
            inscriptions_aux_mini_formations
        return PropositionProgrammeAnnuel(
            inscriptions_par_contexte=inscriptions
        )

    def _build_cours(self, cours_par_contexte) -> List['Inscription']:
        code_cours = [cours['code'] for cours in cours_par_contexte]
        cours_avec_details = [self.details_cours[code] for code in code_cours]
        return [
            Inscription(code=cours['acronym'], intitule=cours['title'], credits=cours['credits'])
            for cours in cours_avec_details
        ]

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'student': self.student,
            'formation': self.formation,
            'annee_academique': self.annee_academique,
            'programme_annuel': self.programme_annuel_avec_details_cours
        }
