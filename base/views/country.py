import io
import json

import requests
from dal import autocomplete
from django import http
from django.conf import settings
from rest_framework.parsers import JSONParser


class CountryAutocomplete(autocomplete.Select2ListView):

    def get(self, request, *args, **kwargs):

        if self.q:
            results = self.get_countries_list(name_filter=self.q)

        return http.HttpResponse(json.dumps({
            'results': [dict(id=x, text=x) for x in results]
        }), content_type='application/json')

    def get_countries_list(self, name_filter=None):
        list_countries = []
        list_country = self.get_country_list_from_osis(name_filter)
        for country in list_country:
            list_countries.append(country['name'])
        return list_countries

    def get_country_list_from_osis(self, name_filter=None):
        header_to_get = {'Authorization': 'Token ' + settings.OSIS_PORTAL_TOKEN}
        url = 'http://localhost:18000/api/v1/reference/countries/'
        if name_filter:
            url = url + '?search=' + name_filter
        response = requests.get(
            url=url,
            headers=header_to_get
        )

        stream = io.BytesIO(response.content)
        data = JSONParser().parse(stream)
        if 'results' in data:
            data = data['results']
        return data
