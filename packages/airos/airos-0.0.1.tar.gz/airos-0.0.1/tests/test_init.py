# pylint: disable=protected-access
"""Test Plugwise Home Assistant module and generate test JSON fixtures."""

import importlib
import json

# Fixture writing
import logging
import os
from pprint import PrettyPrinter

# String generation
import secrets
import string

import pytest

# Testing
import aiofiles
import aiohttp
from freezegun import freeze_time
from packaging import version

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

class TestPlugwise:  # pylint: disable=attribute-defined-outside-init
    """Tests for Plugwise Smile."""

    def setup_app(
        self,
        broken=False,
        fail_auth=False,
        raise_timeout=False,
        stretch=False,
        timeout_happened=False,
    ):
        """Create mock webserver for Smile to interface with."""
        app = aiohttp.web.Application()

        if fail_auth:
            app.router.add_get("/{tail:.*}", self.smile_fail_auth)
            app.router.add_route("POST", "/{tail:.*}", self.smile_fail_auth)
            app.router.add_route("PUT", "/{tail:.*}", self.smile_fail_auth)
            return app

        if broken:
            app.router.add_get("/{tail:.*}", self.smile_broken)
        elif timeout_happened:
            app.router.add_get("/{tail:.*}", self.smile_timeout)
        else:
            app.router.add_get("/{tail:.*}", self.smile_domain_objects)

        if not raise_timeout:
            app.router.add_route("POST", CORE_GATEWAYS_TAIL, self.smile_http_accept)
            app.router.add_route("PUT", CORE_LOCATIONS_TAIL, self.smile_http_accept)
            app.router.add_route(
                "DELETE", CORE_NOTIFICATIONS_TAIL, self.smile_http_accept
            )
            app.router.add_route("PUT", CORE_RULES_TAIL, self.smile_http_accept)
            app.router.add_route("PUT", CORE_APPLIANCES_TAIL, self.smile_http_accept)
        else:
            app.router.add_route("POST", CORE_GATEWAYS_TAIL, self.smile_timeout)
            app.router.add_route("PUT", CORE_LOCATIONS_TAIL, self.smile_timeout)
            app.router.add_route("PUT", CORE_RULES_TAIL, self.smile_timeout)
            app.router.add_route("PUT", CORE_APPLIANCES_TAIL, self.smile_timeout)
            app.router.add_route("DELETE", CORE_NOTIFICATIONS_TAIL, self.smile_timeout)

        return app

    async def status_location(self, device: str = None): -> aiohttp.web.Response
        """Render data for status endpoint."""
        fixture = os.path.join(
            os.path.dirname(__file__),
            f"../fixtures/{device}.json",
        )
        async with aiofiles.open(fixture, encoding="utf-8") as filedata:
            data = await filedata.read()
        return aiohttp.web.Response(text=data)

    @classmethod
    async def smile_http_accept(cls, request):
        """Render generic API calling endpoint."""
        text = EMPTY_XML
        raise aiohttp.web.HTTPAccepted(text=text)

    @classmethod
    async def smile_http_ok(cls, request):
        """Render generic API calling endpoint."""
        text = EMPTY_XML
        raise aiohttp.web.HTTPOk(text=text)

    @classmethod
    async def smile_timeout(cls, request):
        """Render timeout endpoint."""
        raise aiohttp.web.HTTPGatewayTimeout()

    @classmethod
    async def smile_broken(cls, request):
        """Render server error endpoint."""
        raise aiohttp.web.HTTPInternalServerError(text="Internal Server Error")

    @classmethod
    async def smile_fail_auth(cls, request):
        """Render authentication error endpoint."""
        raise aiohttp.web.HTTPUnauthorized()
