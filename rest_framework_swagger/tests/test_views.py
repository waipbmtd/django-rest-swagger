from django.test import TestCase, override_settings

from .. import views


class SwaggerJSONViewTest(TestCase):
    def setUp(self):
        self.sut = views.SwaggerJSON()

    @override_settings(SWAGGER_SETTINGS=None)
    def test_get_info_with_no_settings(self):
        result = self.sut.get_info_data()
        self.assertDictEqual({
            'contact': None,
            'license': None,
            'version': '2.0',
            'title': 'Django REST Swagger'
        }, result)

    def test_get_info_with_contact_data(self):
        settings = {
            'contact': {
                'name': 'George Costanza',
                'url': 'http://vandelay.com',
                'email': 'george@vandelay.com'
            }
        }
        with override_settings(SWAGGER_SETTINGS=settings):
            self.assertDictContainsSubset(settings, self.sut.get_info_data())

    def test_get_info_with_license_data(self):
        settings = {
            'license': {
                'name': 'FreeBSD',
                'url': 'https://www.freebsd.org/'
            }
        }
        with override_settings(SWAGGER_SETTINGS=settings):
            self.assertDictContainsSubset(settings, self.sut.get_info_data())
