from django.conf import settings
from main.test_case import APITestCase

from .serializers import LanguageBulkActionSerializer
from .models import String


class LangTest(APITestCase):

    def setUp(self):
        super().setUp()

    def test_list_languages(self, **kwargs):
        self.authenticate(self.user)
        resp = self.client.get('/api/v2/language/')
        j_resp = resp.json()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(j_resp['results']), len(settings.LANGUAGES))
        self.assertEqual(j_resp['count'], len(settings.LANGUAGES))

    def test_list_strings(self, **kwargs):
        language = settings.LANGUAGES[0][0]
        current_strings_count = String.objects.filter(language=language).count()
        String.objects.create(language=language, key='random-key-for-language-test1', value='Random value', hash='random hash')
        self.authenticate(self.user)
        resp = self.client.get(f'/api/v2/language/{language}/')
        j_resp = resp.json()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(j_resp['strings']), current_strings_count + 1)

    def test_bulk_action(self, **kwargs):
        language = settings.LANGUAGES[0][0]
        string_1 = {
            'key': 'new-string-101',
            'value': 'New Value 101',
            'hash': 'new-hash-101',
        }
        string_2 = {
            'key': 'new-string-102',
            'value': 'New Value 102',
            'hash': 'new-hash-102',
        }
        data = {
            'actions': [
                {'action': LanguageBulkActionSerializer.SET, **string_1},
                {'action': LanguageBulkActionSerializer.SET, **string_2}
            ],
        }

        self.authenticate(self.root_user)
        resp = self.client.post(f'/api/v2/language/{language}/bulk-action/', data, format='json')
        j_resp = resp.json()
        self.assertEqual(resp.status_code, 200)

        first_string = j_resp['new_strings'][0]
        second_string = j_resp['new_strings'][1]
        first_string.pop('id')
        second_string.pop('id')
        self.assertEqual(first_string, {**string_1, 'language': language})
        self.assertEqual(second_string, {**string_2, 'language': language})

        string_2['value'] = 'updated value 101'
        data = {
            'actions': [
                {'action': LanguageBulkActionSerializer.DELETE, **string_1},
                {'action': LanguageBulkActionSerializer.SET, **string_2}
            ],
        }
        resp = self.client.post(f'/api/v2/language/{language}/bulk-action/', data, format='json')
        j_resp = resp.json()

        first_string_key = j_resp['deleted_strings_keys'][0]
        second_string = j_resp['updated_strings'][0]
        second_string.pop('id')
        self.assertEqual(second_string, {**string_2, 'language': language})
        self.assertEqual(first_string_key, string_1['key'])
