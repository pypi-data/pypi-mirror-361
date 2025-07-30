# -*- coding: utf-8 -*-

__author__ = "Cyber-Detect"

import json
from time import time
from typing import Any

import aiohttp
import requests

from .models.clamav import CerberusClamav
from .models.common import Md5
from .models.die import CerberusDie
from .models.extract import CerberusExtract
from .models.filter import CerberusFilter
from .models.gorille_dynamic import CerberusGorilleDynamicGcore
from .models.gorille_sites_gcore import CerberusGorilleSitesGcore
from .models.gorille_static import (
    CerberusGorilleStatic,
    CerberusGorilleStaticGcore,
)
from .models.graph_3d import CerberusGraph3d, CerberusGraph3dScreenshots
from .models.is_alive import CerberusIsAlive
from .models.load_db import CerberusLoadDb
from .models.load_db_gcore import CerberusLoadDbGcore
from .models.magic import CerberusMagic
from .models.malware_metadata import CerberusMalwareMetadata
from .models.naming import CerberusNaming
from .models.signature import CerberusSignature
from .models.status import CerberusStatus
from .models.strings import CerberusStrings
from .models.unload_db import CerberusUnloadDb
from .models.unload_db_gcore import CerberusUnloadDbGcore
from .models.usage import CerberusUsage
from .models.version import CerberusVersion


class CerberusException(Exception):
    """Base class exception for Cererus package."""

    pass

class CerberusError(CerberusException):
    """Exception raised when Cerberus response contains an error field."""

    def __init__(self, message, error_code, error_message, error_details, raw_error):
        super().__init__(message)

        self.error_code = error_code
        self.error_message = error_message
        self.error_details = error_details
        self.raw_error = raw_error

    def pprint(self) -> str:
        return "{} ({})".format(
            self.error_message.capitalize(),
            self.error_details,
        )


class Cerberus:
    def __init__(self, host: str = "127.0.0.1", port: int = 55222):
        self._url = "http://%s:%s" % (host, port)

        # Only use for async requests
        self._aiohttp_session: aiohttp.ClientSession | None = None

        # Variables used to cache cerberus version
        self._cerberus_version: CerberusVersion | None = None
        self._last_versions_update: int | None = None

    def _add_to_dict_if_not_none(self, d: dict[str, Any], k: str, v: Any) -> None:
        if v is not None:
            d[k] = v

    async def close_aiohttp_session(self) -> None:
        if self._aiohttp_session is not None:
            await self._aiohttp_session.close()

    def _check_for_cerberus_error(self, resp: dict) -> None:
        if "result" not in resp:
            error = resp.get("error", {})
            error_code = error.get("code", "unknown code")
            error_message = error.get("message", "unknown error")
            error_details = error.get("details", "no error details")
            error_msg = "{} ({}) (code: {})".format(error_message, error_details, error_code)
            raise CerberusError(error_msg, error_code, error_message, error_details, {"error": error})

    # Async request method using aiohttp module
    async def request_async(self, method: str, params: dict = {}) -> dict:
        """Generic request method used to send a request to Cerberus."""
        body = {
            "method": method,
            "params": params
        }
        try:
            if self._aiohttp_session is None:
                # TODO: improve timeout stuff
                timeout = aiohttp.ClientTimeout(total=None)
                self._aiohttp_session = aiohttp.ClientSession(
                    headers={"content-type": "application/json"}, timeout=timeout
                )
            async with self._aiohttp_session.post(self._url, data=json.dumps(body)) as rep:
                resp = await rep.json()
                self._check_for_cerberus_error(resp)
                return resp["result"]
        except CerberusError:
            raise
        # TODO: handle iohttp exceptions
        except Exception as e:
            raise CerberusException(e)

    # Sync request method using requests module
    def request(self, method: str, params: dict = {}) -> dict:
        body = {
            "method": method,
            "params": params
        }
        try:
            rep = requests.post(self._url, data=json.dumps(body))
            resp = rep.json()
            self._check_for_cerberus_error(resp)
            # print(resp["result"])
            return resp["result"]
        except CerberusError:
            raise
        # TODO: handle requests exceptions
        except Exception as e:
            raise CerberusException(e)

    def _should_update_version(self, cache_validity: int | None = None) -> bool:
        if cache_validity is None:
            return True
        if self._cerberus_version is None:
            return True
        if self._last_versions_update is None:
            return True
        if (int(time()) - self._last_versions_update > cache_validity):
            return True
        return False

    # version method
    async def version_async(self, cache_validity: int | None = None) -> CerberusVersion:
        """Send request with 'version' method to Cerberus."""
        if self._should_update_version(cache_validity):
            r = await self.request_async("version")
            self._cerberus_version = CerberusVersion(**r)
            self._last_versions_update = int(time())
        assert self._cerberus_version is not None
        return self._cerberus_version

    def version(self, cache_validity: int | None = None) -> CerberusVersion:
        """Send request with 'version' method to Cerberus."""
        if self._should_update_version(cache_validity):
            r = self.request("version")
            self._cerberus_version = CerberusVersion(**r)
            self._last_versions_update = int(time())
        assert self._cerberus_version is not None
        return self._cerberus_version

    # is_alive method
    async def is_alive_async(self) -> CerberusIsAlive:
        """Send request with 'is_alive' method to Cerberus."""
        r = await self.request_async("is_alive")
        return CerberusIsAlive(**r)

    def is_alive(self) -> CerberusIsAlive:
        """Send request with 'is_alive' method to Cerberus."""
        r = self.request("is_alive")
        return CerberusIsAlive(**r)

    # usage method
    async def usage_async(self) -> CerberusUsage:
        """Send request with 'usage' method to Cerberus."""
        r = await self.request_async("usage")
        return CerberusUsage(**r)

    def usage(self) -> CerberusUsage:
        """Send request with 'usage' method to Cerberus."""
        r = self.request("usage")
        return CerberusUsage(**r)

    # status method
    async def status_async(self) -> CerberusStatus:
        """Send request with 'status' method to Cerberus."""
        r = await self.request_async("status")
        return CerberusStatus(**r)

    def status(self) -> CerberusStatus:
        """Send request with 'status' method to Cerberus."""
        r = self.request("status")
        return CerberusStatus(**r)

    # naming method
    async def naming_async(
        self,
        md5: Md5
    ) -> CerberusNaming:
        """Send request with 'naming' method to Cerberus."""
        params = {}
        params["md5"] = md5
        r = await self.request_async("naming", params)
        return CerberusNaming(**r)

    def naming(
        self,
        md5: Md5
    ) -> CerberusNaming:
        """Send request with 'naming' method to Cerberus."""
        params = {}
        params["md5"] = md5
        r = self.request("naming", params)
        return CerberusNaming(**r)

    # filter method
    async def filter_async(
        self,
        file_hash: str,
        disable_naming: bool | None = None,
    ) -> CerberusFilter:
        """Send request with 'filter' method to Cerberus."""
        params = {}
        params["hash"] = file_hash
        self._add_to_dict_if_not_none(params, "disable_naming", disable_naming)
        r = await self.request_async("filter", params)
        return CerberusFilter(**r)

    def filter(
        self,
        file_hash: str,
        disable_naming: bool | None = None,
    ) -> CerberusFilter:
        """Send request with 'filter' method to Cerberus."""
        params = {}
        params["hash"] = file_hash
        self._add_to_dict_if_not_none(params, "disable_naming", disable_naming)
        r = self.request("filter", params)
        return CerberusFilter(**r)

    # clamav method
    async def clamav_async(
        self,
        path: str
    ) -> CerberusClamav:
        """Send request with 'clamav' method to Cerberus."""
        params = {}
        params["path"] = path
        r = await self.request_async("clamav", params)
        return CerberusClamav(**r)

    def clamav(
        self,
        path: str
    ) -> CerberusClamav:
        """Send request with 'clamav' method to Cerberus."""
        params = {}
        params["path"] = path
        r = self.request("clamav", params)
        return CerberusClamav(**r)

    # signature method
    async def signature_async(
        self,
        path: str,
        timeout: int | None = None
    ) -> CerberusSignature:
        """Send request with 'signature' method to Cerberus."""
        params = {}
        params["path"] = path
        self._add_to_dict_if_not_none(params, "timeout", timeout)
        r = await self.request_async("signature", params)
        return CerberusSignature(**r)

    def signature(
        self,
        path: str,
        timeout: int | None = None
    ) -> CerberusSignature:
        """Send request with 'signature' method to Cerberus."""
        params = {}
        params["path"] = path
        self._add_to_dict_if_not_none(params, "timeout", timeout)
        r = self.request("signature", params)
        return CerberusSignature(**r)

    # die method
    async def die_async(
        self,
        path: str,
        timeout: int | None = None
    ) -> CerberusDie:
        """Send request with 'die' method to Cerberus."""
        params = {}
        params["path"] = path
        self._add_to_dict_if_not_none(params, "timeout", timeout)
        r = await self.request_async("die", params)
        return CerberusDie(**r)

    def die(
        self,
        path: str,
        timeout: int | None = None
    ) -> CerberusDie:
        """Send request with 'die' method to Cerberus."""
        params = {}
        params["path"] = path
        self._add_to_dict_if_not_none(params, "timeout", timeout)
        r = self.request("die", params)
        return CerberusDie(**r)

    # graph_3d method
    async def graph_3d_async(
        self,
        path: str,
        md5: Md5,
        black: bool | None = None,
        white: bool | None = None,
        small: bool | None = None,
        timeout: int | None = None,
    ) -> CerberusGraph3d:
        """Send request with 'die' method to Cerberus."""
        params = {}
        params["path"] = path
        params["md5"] = md5
        self._add_to_dict_if_not_none(params, "black", black)
        self._add_to_dict_if_not_none(params, "white", white)
        self._add_to_dict_if_not_none(params, "small", small)
        self._add_to_dict_if_not_none(params, "timeout", timeout)
        r = await self.request_async("graph_3d", params)
        return CerberusGraph3d(**r)

    def graph_3d(
        self,
        path: str,
        md5: Md5,
        black: bool | None = None,
        white: bool | None = None,
        small: bool | None = None,
        timeout: int | None = None,
    ) -> CerberusGraph3d:
        """Send request with 'graph_3d' method to Cerberus."""
        params = {}
        params["path"] = path
        params["md5"] = md5
        self._add_to_dict_if_not_none(params, "black", black)
        self._add_to_dict_if_not_none(params, "white", white)
        self._add_to_dict_if_not_none(params, "small", small)
        self._add_to_dict_if_not_none(params, "timeout", timeout)
        r = self.request("graph_3d", params)
        return CerberusGraph3d(**r)

    # graph_3d screenshots method
    async def graph_3d_screenshots_async(
        self,
        path: str,
        md5: Md5,
        screenshots: int = 1,
        black: bool | None = None,
        white: bool | None = None,
        small: bool | None = None,
        timeout: int | None = None,
    ) -> CerberusGraph3dScreenshots:
        """Send request with 'die' method to Cerberus."""
        params: dict[str, Any] = {}
        params["path"] = path
        params["md5"] = md5
        params["screenshots"] = screenshots
        self._add_to_dict_if_not_none(params, "black", black)
        self._add_to_dict_if_not_none(params, "white", white)
        self._add_to_dict_if_not_none(params, "small", small)
        self._add_to_dict_if_not_none(params, "timeout", timeout)
        r = await self.request_async("graph_3d", params)
        return CerberusGraph3dScreenshots(**r)

    def graph_3d_screenshots(
        self,
        path: str,
        md5: Md5,
        screenshots: int = 1,
        black: bool | None = None,
        white: bool | None = None,
        small: bool | None = None,
        timeout: int | None = None,
    ) -> CerberusGraph3dScreenshots:
        """Send request with 'graph_3d' method to Cerberus."""
        params: dict[str, Any] = {}
        params["path"] = path
        params["md5"] = md5
        params["screenshots"] = screenshots
        self._add_to_dict_if_not_none(params, "black", black)
        self._add_to_dict_if_not_none(params, "white", white)
        self._add_to_dict_if_not_none(params, "small", small)
        self._add_to_dict_if_not_none(params, "timeout", timeout)
        r = self.request("graph_3d", params)
        return CerberusGraph3dScreenshots(**r)

    # malware_metadata method
    async def malware_metadata_async(
        self,
        malware: str,
    ) -> CerberusMalwareMetadata:
        """Send request with 'malware_metadata' method to Cerberus."""
        params = {}
        params["malware"] = malware
        r = await self.request_async("malware_metadata", params)
        return CerberusMalwareMetadata(**r)

    def malware_metadata(
        self,
        malware: str,
    ) -> CerberusMalwareMetadata:
        """Send request with 'malware_metadata' method to Cerberus."""
        params = {}
        params["malware"] = malware
        r = self.request("malware_metadata", params)
        return CerberusMalwareMetadata(**r)

    # load_db method
    async def load_db_async(
        self,
        db_path: str,
        db_type: str,
        filter_db_path: str | None = None,
        generation_datetime: str | None = None,
        mdecs_numbers: int | None = None,
    ) -> CerberusLoadDb:
        """Send request with 'load_db' method to Cerberus."""
        params = {}
        params["db_path"] = db_path
        params["db_type"] = db_type
        self._add_to_dict_if_not_none(params, "filter_db_path", filter_db_path)
        self._add_to_dict_if_not_none(params, "generation_datetime", generation_datetime)
        self._add_to_dict_if_not_none(params, "mdecs_numbers", mdecs_numbers)
        r = await self.request_async("load_db", params)
        return CerberusLoadDb(**r)

    def load_db(
        self,
        db_path: str,
        db_type: str,
        filter_db_path: str | None = None,
        generation_datetime: str | None = None,
        mdecs_numbers: int | None = None,
    ) -> CerberusLoadDb:
        """Send request with 'load_db' method to Cerberus."""
        params = {}
        params["db_path"] = db_path
        params["db_type"] = db_type
        self._add_to_dict_if_not_none(params, "filter_db_path", filter_db_path)
        self._add_to_dict_if_not_none(params, "generation_datetime", generation_datetime)
        self._add_to_dict_if_not_none(params, "mdecs_numbers", mdecs_numbers)
        r = self.request("load_db", params)
        return CerberusLoadDb(**r)

    # unload_db method
    async def unload_db_async(
        self,
    ) -> CerberusUnloadDb:
        """Send request with 'unload_db' method to Cerberus."""
        r = await self.request_async("unload_db", {})
        return CerberusUnloadDb(**r)

    def unload_db(
        self,
    ) -> CerberusUnloadDb:
        """Send request with 'load_db' method to Cerberus."""
        r = self.request("unload_db", {})
        return CerberusUnloadDb(**r)


    # load_db_gcore method
    async def load_db_gcore_async(
        self,
        dbs: dict,
    ) -> CerberusLoadDbGcore:
        """Send request with 'load_db_gcore' method to Cerberus."""
        params = {}
        params["dbs"] = dbs
        r = await self.request_async("load_db_gcore", params)
        return CerberusLoadDbGcore(**r)

    def load_db_gcore(
        self,
        dbs: dict,
    ) -> CerberusLoadDbGcore:
        """Send request with 'load_db_gcore' method to Cerberus."""
        params = {}
        params["dbs"] = dbs
        r = self.request("load_db_gcore", params)
        return CerberusLoadDbGcore(**r)

    # unload_db_gcore method
    async def unload_db_gcore_async(self) -> CerberusUnloadDbGcore:
        """Send request with 'unload_db_gcore' method to Cerberus."""
        r = await self.request_async("unload_db_gcore")
        return CerberusUnloadDbGcore(**r)

    def unload_db_gcore(self) -> CerberusUnloadDbGcore:
        """Send request with 'unload_db_gcore' method to Cerberus."""
        r = self.request("unload_db_gcore")
        return CerberusUnloadDbGcore(**r)


    # gorille_static method
    async def gorille_static_async(
        self,
        path: str,
        type: str | None = None,
        dist_3d_mode: bool | None = None,
        timeout_dist: int | None = None,
        timeout_waiting_mdec: int | None = None,
        max_matches: int | None = None,
        best_match_name: bool | None = None,
    ) -> CerberusGorilleStatic:
        """Send request with 'gorille_static' method to Cerberus."""
        params = {}
        params["path"] = path
        self._add_to_dict_if_not_none(params, "type", type)
        self._add_to_dict_if_not_none(params, "dist_3d_mode", dist_3d_mode)
        self._add_to_dict_if_not_none(params, "timeout_dist", timeout_dist)
        self._add_to_dict_if_not_none(params, "timeout_waiting_mdec", timeout_waiting_mdec)
        self._add_to_dict_if_not_none(params, "max_matches", max_matches)
        self._add_to_dict_if_not_none(params, "best_match_name", best_match_name)
        r = await self.request_async("gorille_static", params)
        return CerberusGorilleStatic(**r)

    def gorille_static(
        self,
        path: str,
        type: str | None = None,
        dist_3d_mode: bool | None = None,
        timeout_dist: int | None = None,
        timeout_waiting_mdec: int | None = None,
        max_matches: int | None = None,
        best_match_name: bool | None = None,
    ) -> CerberusGorilleStatic:
        """Send request with 'gorille_static' method to Cerberus."""
        params = {}
        params["path"] = path
        self._add_to_dict_if_not_none(params, "type", type)
        self._add_to_dict_if_not_none(params, "dist_3d_mode", dist_3d_mode)
        self._add_to_dict_if_not_none(params, "timeout_dist", timeout_dist)
        self._add_to_dict_if_not_none(params, "timeout_waiting_mdec", timeout_waiting_mdec)
        self._add_to_dict_if_not_none(params, "max_matches", max_matches)
        self._add_to_dict_if_not_none(params, "best_match_name", best_match_name)
        r = self.request("gorille_static", params)
        return CerberusGorilleStatic(**r)

    # gorille_static_gcore method
    async def gorille_static_gcore_async(
        self,
        path: str,
        reduction: str | None = None,
        sites_size: int | None = None,
        detailed_dist: bool | None = None,
        max_matches: int | None = None,
        timeout: int | None = None,
    ) -> CerberusGorilleStaticGcore:
        """Send request with 'gorille_static_gcore' method to Cerberus."""
        params = {}
        params["path"] = path
        self._add_to_dict_if_not_none(params, "reduction", reduction)
        self._add_to_dict_if_not_none(params, "sites_size", sites_size)
        self._add_to_dict_if_not_none(params, "detailed_dist", detailed_dist)
        self._add_to_dict_if_not_none(params, "max_matches", max_matches)
        self._add_to_dict_if_not_none(params, "timeout", timeout)
        r = await self.request_async("gorille_static_gcore", params)
        return CerberusGorilleStaticGcore(**r)

    def gorille_static_gcore(
            self,
            path: str,
            reduction: str | None = None,
            sites_size: int | None = None,
            detailed_dist: bool | None = None,
            max_matches: int | None = None,
            timeout: int | None = None,
        ) -> CerberusGorilleStaticGcore:
        """Send request with 'gorille_static' method to Cerberus."""
        params = {}
        params["path"] = path
        self._add_to_dict_if_not_none(params, "reduction", reduction)
        self._add_to_dict_if_not_none(params, "sites_size", sites_size)
        self._add_to_dict_if_not_none(params, "detailed_dist", detailed_dist)
        self._add_to_dict_if_not_none(params, "max_matches", max_matches)
        self._add_to_dict_if_not_none(params, "timeout", timeout)
        r = self.request("gorille_static_gcore", params)
        return CerberusGorilleStaticGcore(**r)


    # gorille_sites_gcore method
    async def gorille_sites_gcore_async(
        self,
        path: str,
        reduction: str | None = None,
        sites_size: int | None = None,
        no_tag: bool | None = None,
        timeout: int | None = None,
    ) -> CerberusGorilleSitesGcore:
        """Send request with 'gorille_sites_gcore' method to Cerberus."""
        params = {}
        params["path"] = path
        self._add_to_dict_if_not_none(params, "reduction", reduction)
        self._add_to_dict_if_not_none(params, "sites_size", sites_size)
        self._add_to_dict_if_not_none(params, "no_tag", no_tag)
        self._add_to_dict_if_not_none(params, "timeout", timeout)
        r = await self.request_async("gorille_sites_gcore", params)
        return CerberusGorilleSitesGcore(**r)

    def gorille_sites_gcore(
        self,
        path: str,
        reduction: str | None = None,
        sites_size: int | None = None,
        no_tag: bool | None = None,
        timeout: int | None = None,
    ) -> CerberusGorilleSitesGcore:
        """Send request with 'gorille_sites_gcore' method to Cerberus."""
        params = {}
        params["path"] = path
        self._add_to_dict_if_not_none(params, "reduction", reduction)
        self._add_to_dict_if_not_none(params, "sites_size", sites_size)
        self._add_to_dict_if_not_none(params, "no_tag", no_tag)
        self._add_to_dict_if_not_none(params, "timeout", timeout)
        r = self.request("gorille_sites_gcore", params)
        return CerberusGorilleSitesGcore(**r)


    # extract method
    async def extract_async(
        self,
        path: str,
        tool: str,
        output_folderpath: str,
        password: list[str] | str | None = None,
        timeout: int | None = None
    ) -> CerberusExtract:
        """Send request with 'extract' method to Cerberus."""
        params = {}
        params["path"] = path
        params["tool"] = tool
        params["output_folderpath"] = output_folderpath
        self._add_to_dict_if_not_none(params, "password", password)
        self._add_to_dict_if_not_none(params, "timeout", timeout)
        r = await self.request_async("extract", params)
        return CerberusExtract(**r)

    def extract(
        self,
        path: str,
        tool: str,
        output_folderpath: str,
        password: list[str] | str | None = None,
        timeout: int | None = None
    ) -> CerberusExtract:
        """Send request with 'extract' method to Cerberus."""
        params = {}
        params["path"] = path
        params["tool"] = tool
        params["output_folderpath"] = output_folderpath
        self._add_to_dict_if_not_none(params, "password", password)
        self._add_to_dict_if_not_none(params, "timeout", timeout)
        r = self.request("extract", params)
        return CerberusExtract(**r)


    # strings method
    async def strings_async(
        self,
        path: str,
        timeout: int | None = None,
        limit: int | None = None,
        regex: list[str] | None = None,
    ) -> CerberusStrings:
        """Send request with 'strings' method to Cerberus."""
        params = {}
        params["path"] = path
        self._add_to_dict_if_not_none(params, "timeout", timeout)
        self._add_to_dict_if_not_none(params, "limit", limit)
        self._add_to_dict_if_not_none(params, "regex", regex)
        r = await self.request_async("strings", params)
        return CerberusStrings(**r)

    def strings(
        self,
        path: str,
        timeout: int | None = None,
        limit: int | None = None,
        regex: list[str] | None = None,
    ) -> CerberusStrings:
        """Send request with 'strings' method to Cerberus."""
        params = {}
        params["path"] = path
        self._add_to_dict_if_not_none(params, "timeout", timeout)
        self._add_to_dict_if_not_none(params, "limit", limit)
        self._add_to_dict_if_not_none(params, "regex", regex)
        r = self.request("strings", params)
        return CerberusStrings(**r)

    # magic method
    async def magic_async(
        self,
        path: str,
    ) -> CerberusMagic:
        """Send request with 'magic' method to Cerberus."""
        params = {}
        params["path"] = path
        r = await self.request_async("magic", params)
        return CerberusMagic(**r)

    def magic(
        self,
        path: str,
    ) -> CerberusMagic:
        """Send request with 'magic' method to Cerberus."""
        params = {}
        params["path"] = path
        r = self.request("magic", params)
        return CerberusMagic(**r)

    # gorille_dynamic_gcore method
    async def gorille_dynamic_gcore_async(
        self,
        path: str,
        os: str | None = None,
        timeout_tracing: int | None = None,
        timeout_waiting_sandbox: int | None = None,
        screenshots: bool | None = None,
        tracing_artifacts_output_folderpath: str | None = None,
        dist: bool | None = None,
        reduction: str | None = None,
        sites_size: int | None = None,
        disable_naming: bool | None = None,
        max_matches: int | None = None,
        timeout: int | None = None,
    ) -> CerberusGorilleDynamicGcore:
        """Send request with 'gorille_dynamic_gcore' method to Cerberus."""
        params = {}
        params["path"] = path
        self._add_to_dict_if_not_none(params, "os", os)
        self._add_to_dict_if_not_none(params, "timeout_tracing", timeout_tracing)
        self._add_to_dict_if_not_none(params, "timeout_waiting_sandbox", timeout_waiting_sandbox)
        self._add_to_dict_if_not_none(params, "screenshots", screenshots)
        self._add_to_dict_if_not_none(params, "tracing_artifacts_output_folderpath", tracing_artifacts_output_folderpath)
        self._add_to_dict_if_not_none(params, "dist", dist)
        self._add_to_dict_if_not_none(params, "reduction", reduction)
        self._add_to_dict_if_not_none(params, "sites_size", sites_size)
        self._add_to_dict_if_not_none(params, "disable_naming", disable_naming)
        self._add_to_dict_if_not_none(params, "max_matches", max_matches)
        self._add_to_dict_if_not_none(params, "timeout", timeout)
        r = await self.request_async("gorille_dynamic_gcore", params)
        return CerberusGorilleDynamicGcore(**r)

    def gorille_dynamic_gcore(
        self,
        path: str,
        os: str | None = None,
        timeout_tracing: int | None = None,
        timeout_waiting_sandbox: int | None = None,
        screenshots: bool | None = None,
        tracing_artifacts_output_folderpath: str | None = None,
        dist: bool | None = None,
        reduction: str | None = None,
        sites_size: int | None = None,
        disable_naming: bool | None = None,
        max_matches: int | None = None,
        timeout: int | None = None,
    ) -> CerberusGorilleDynamicGcore:
        """Send request with 'gorille_dynamic_gcore' method to Cerberus."""
        params = {}
        params["path"] = path
        self._add_to_dict_if_not_none(params, "os", os)
        self._add_to_dict_if_not_none(params, "timeout_tracing", timeout_tracing)
        self._add_to_dict_if_not_none(params, "timeout_waiting_sandbox", timeout_waiting_sandbox)
        self._add_to_dict_if_not_none(params, "screenshots", screenshots)
        self._add_to_dict_if_not_none(params, "tracing_artifacts_output_folderpath", tracing_artifacts_output_folderpath)
        self._add_to_dict_if_not_none(params, "dist", dist)
        self._add_to_dict_if_not_none(params, "reduction", reduction)
        self._add_to_dict_if_not_none(params, "sites_size", sites_size)
        self._add_to_dict_if_not_none(params, "disable_naming", disable_naming)
        self._add_to_dict_if_not_none(params, "max_matches", max_matches)
        self._add_to_dict_if_not_none(params, "timeout", timeout)
        r = self.request("gorille_dynamic_gcore", params)
        return CerberusGorilleDynamicGcore(**r)



cerberus = None

def init_cerberus_session(host: str, port: int) -> Cerberus:
    global cerberus
    cerberus = Cerberus(host, port)
    return cerberus

def get_cerberus_session() -> Cerberus:
    global cerberus
    if cerberus is None:
        raise CerberusException("Please init shared session first with 'init_cerberus_session'")
    return cerberus
