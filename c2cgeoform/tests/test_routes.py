# pylint: disable=no-self-use

from unittest import TestCase

from pyramid import testing
from pyramid.config import Configurator
from pyramid.exceptions import ConfigurationConflictError
from pyramid.interfaces import IRoutesMapper

from c2cgeoform.routes import (
    Application, ApplicationRoutePredicate, register_models, register_routes, get_application
)


class TestDirectives(TestCase):

    def test_add_c2cgeoform_application(self):
        config = Configurator()
        config.include('c2cgeoform.routes')
        config.add_c2cgeoform_application('app', models=[])
        self.assertEqual(0, len(config.registry['c2cgeoform_applications']))
        config.commit()
        registered_applications = config.registry['c2cgeoform_applications']
        self.assertEqual(1, len(registered_applications))
        self.assertEqual('app', registered_applications[0].name())

    def test_add_c2cgeoform_application_conflict(self):
        config = Configurator()
        config.include('c2cgeoform.routes')
        config.add_c2cgeoform_application('app', models=[])
        config.add_c2cgeoform_application('app', models=[])
        with self.assertRaises(ConfigurationConflictError):
            config.commit()


class TestApplicationRoutePredicate(TestCase):

    def _config(self, config, app_name, url_segment=None):
        config.include('c2cgeoform.routes')
        config.add_c2cgeoform_application(app_name, models=[], url_segment=url_segment)
        config.commit()

    def test_not_match(self):
        with testing.testConfig() as config:
            self._config(config, 'app')
            pred = ApplicationRoutePredicate(config, 'anything')
            context = {
                'match': {
                    'application': 'not_registered_application'
                }
            }
            request = testing.DummyRequest()
            self.assertFalse(pred(context, request))

    def test_match(self):
        with testing.testConfig() as config:
            self._config(config, 'app')
            pred = ApplicationRoutePredicate(config, 'anything')
            context = {
                'match': {
                    'application': 'app'
                }
            }
            request = testing.DummyRequest()
            self.assertTrue(pred(context, request))

            # We should have matched application in request.application
            application = get_application(request)
            self.assertTrue(isinstance(application, Application))
            self.assertEqual('app', application.name())

    def test_url_segment_not_match(self):
        with testing.testConfig() as config:
            self._config(config, 'app', url_segment='some_segment_url')
            pred = ApplicationRoutePredicate(config, 'anything')
            context = {
                'match': {
                    'application': 'app'
                }
            }
            request = testing.DummyRequest()
            self.assertFalse(pred(context, request))

    def test_url_segment_match(self):
        with testing.testConfig() as config:
            self._config(config, 'app', url_segment='some_segment_url')
            pred = ApplicationRoutePredicate(config, 'anything')
            context = {
                'match': {
                    'application': 'some_segment_url'
                }
            }
            request = testing.DummyRequest()
            self.assertTrue(pred(context, request))

            # We should have matched application in request.c2cgeoform_application
            application = get_application(request)
            self.assertTrue(isinstance(application, Application))
            self.assertEqual('app', application.name())


class TestPregenerator(TestCase):

    def test_pregenerator(self):
        with testing.testConfig() as config:
            config.include('c2cgeoform.routes')
            register_routes(config)
            config.commit()
            request = testing.DummyRequest()
            request.matchdict = {
                'application': 'app',
                'table': 'table'
            }
            self.assertEqual('http://example.com/app/table', request.route_url('c2cgeoform_index'))


class TestSingleApp(TestCase):

    def test_register_models(self):
        with testing.testConfig() as config:
            config.include('c2cgeoform.routes')

            class MyModel:

                __tablename__ = 'mytable'

            register_models(config, [('mytable', MyModel)])
            register_routes(config, multi_application=False)

            request = testing.DummyRequest(environ={
                'PATH_INFO': '/mytable'
            })
            routes_mapper = config.registry.queryUtility(IRoutesMapper)
            info = routes_mapper(request)
            match, route = info['match'], info['route']
            self.assertEqual('c2cgeoform_index', route.name)
            self.assertEqual('mytable', match['table'])

            # We should have the single application in request.c2cgeoform_application
            application = get_application(request)
            self.assertTrue(isinstance(application, Application))
            self.assertEqual('mytable', application.tables()[0]['key'])

            self.assertEqual('http://example.com/table', request.route_url('c2cgeoform_index', table='table'))
