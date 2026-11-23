# Copyright (c) 2026

from unittest import TestCase

import pyramid.request
from pyramid import testing
from pyramid.httpexceptions import HTTPFound

from c2cgeoform.views import set_locale_cookie


class TestSetLocaleCookie(TestCase):
    """Tests of the locale view, which is called with or without the language parameter."""

    def _request(self, query: str = "", referer: str | None = None) -> pyramid.request.Request:
        request = pyramid.request.Request.blank(
            f"/admin/locale{query}", headers={"Referer": referer} if referer is not None else {}
        )
        # As done by the Pyramid router at request ingress time
        request.registry = testing.setUp().registry
        return request

    def tearDown(self) -> None:
        testing.tearDown()

    def _cookies(self, request: pyramid.request.Request) -> list[str]:
        return [str(cookie) for cookie in request.response.headers.getall("Set-Cookie")]

    def test_no_language(self):
        """A missing language parameter must not raise, the locale cookie is just not set."""
        request = self._request()

        result = set_locale_cookie(request)

        assert result == {"success": True}
        assert self._cookies(request) == []

    def test_empty_language(self):
        request = self._request(query="?language=")

        result = set_locale_cookie(request)

        assert result == {"success": True}
        assert self._cookies(request) == []

    def test_language(self):
        request = self._request(query="?language=fr")

        result = set_locale_cookie(request)

        assert result == {"success": True}
        assert len(self._cookies(request)) == 1
        assert "_LOCALE_=fr" in self._cookies(request)[0]

    def test_no_language_with_referer(self):
        request = self._request(referer="http://localhost/admin/users")

        result = set_locale_cookie(request)

        assert isinstance(result, HTTPFound)
        assert result.location == "http://localhost/admin/users"
        assert self._cookies(request) == []

    def test_language_with_referer(self):
        request = self._request(query="?language=de", referer="http://localhost/admin/users")

        result = set_locale_cookie(request)

        assert isinstance(result, HTTPFound)
        assert result.location == "http://localhost/admin/users"
        assert "_LOCALE_=de" in self._cookies(request)[0]
