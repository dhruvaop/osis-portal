##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from admission.forms import NewAccountForm, AccountForm, NewPasswordForm
from admission.utils import send_mail
from random import randint
from admission import models as mdl

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login
from admission.forms import AccountingForm

def accounting(request):
    academic_yr = mdl.academic_year.current_academic_year()
    previous_academic_year = mdl.academic_year.find_by_year(academic_yr.year-1)
    sport_affiliation_amount = 0
    culture_affiliation_amount = 0
    solidary_affiliation_amount = 0
    application = mdl.application.find_first_by_user(request.user)
    return render(request, "accounting.html",{"academic_year": academic_yr,
                                              "previous_academic_year":      previous_academic_year,
                                              "sport_affiliation_amount":    sport_affiliation_amount,
                                              "culture_affiliation_amount":  culture_affiliation_amount,
                                              "solidary_affiliation_amount": solidary_affiliation_amount,
                                              "application":                 application})


def accounting_update(request):
    print('accounting_update')
    academic_yr = mdl.academic_year.current_academic_year()
    previous_academic_year = mdl.academic_year.find_by_year(academic_yr.year-1)
    sport_affiliation_amount = 0
    culture_affiliation_amount = 0
    solidary_affiliation_amount = 0
    application = mdl.application.find_first_by_user(request.user)
    # is_valid, validation_messages = fields_validation(request)
    accounting_form = AccountingForm(data=request.POST)
    application = populate_application(request)

    if accounting_form.is_valid():
        application.save()

    return render(request, "accounting.html",{"academic_year": academic_yr,
                                              "previous_academic_year":      previous_academic_year,
                                              "sport_affiliation_amount":    sport_affiliation_amount,
                                              "culture_affiliation_amount":  culture_affiliation_amount,
                                              "solidary_affiliation_amount": solidary_affiliation_amount,
                                              "application":                 application,
                                              "form":                        accounting_form})


def fields_validation(request):
    is_valid = True
    validation_messages = {}

    if request.POST.get('scholarship') == 'true':
        if request.POST.get('scholarship_organization') is None or \
                len(request.POST.get('scholarship_organization').strip()) == 0 :
            validation_messages['scholarship_organization'] = _('mandatory_field')
            is_valid = False
    return is_valid, validation_messages


def populate_application(request):
    if request.POST.get('application_id') is None:
        application = mdl.application.Application()
    else:
        application = mdl.application.find_by_id(int(request.POST.get('application_id')))
    application.study_grant = False
    application.study_grant_number = None
    application.deduction_children = False
    application.scholarship = False
    application.scholarship_organization = None
    application.sport_membership = False
    application.culture_membership = False
    application.solidary_membership = False
    application.bank_account_iban = None
    application.bank_account_bic = None
    application.bank_account_name = None
    if request.POST.get('study_grant') == "true":
        application.study_grant = True
        if request.POST.get('study_grant_number'):
            application.study_grant_number = request.POST.get('study_grant_number')

    if request.POST.get('scholarship') == "true":
        application.scholarship = True
        if request.POST.get('scholarship_organization'):
            application.scholarship_organization = request.POST.get('scholarship_organization')
    if request.POST.get('sport_membership') == "true":
        application.sport_membership = True
    if request.POST.get('culture_membership') == "true":
        application.culture_membership = True
    if request.POST.get('solidary_membership') == "true":
        application.solidary_membership = True
    if request.POST.get('bank_account_iban'):
        application.bank_account_iban = request.POST.get('bank_account_iban')
    if request.POST.get('bank_account_bic'):
        application.bank_account_bic = request.POST.get('bank_account_bic')
    if request.POST.get('bank_account_name'):
        application.bank_account_bic = request.POST.get('bank_account_name')
    return application
