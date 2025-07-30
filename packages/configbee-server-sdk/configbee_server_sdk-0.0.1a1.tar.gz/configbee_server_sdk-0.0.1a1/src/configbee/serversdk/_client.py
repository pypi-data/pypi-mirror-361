import logging
import asyncio
import hishel
from enum import Enum
from typing import Dict, Optional
from . import _client_config
import re
import threading
import json
from httpx_sse import aconnect_sse, ServerSentEvent

import httpx
from urllib.parse import urljoin

def get_http_client():
    return hishel.AsyncCacheClient()

class ConfigbeeStatus(Enum):
    """Status types for ConfigBee client"""
    INITIALIZING = "INITIALIZING"
    ACTIVE = "ACTIVE"
    DEACTIVE = "DEACTIVE"
    ERROR = "ERROR"

class ConfigbeeClient:
    """
    ConfigBee Python client for feature flags and dynamic configuration.
    
    This client provides real-time feature flag management with support for:
    - Boolean flags
    - Number configurations
    - Text configurations
    - JSON configurations
    - Real-time updates
    """
    
    ENV_DEFAULT_CONFIG_GROUP_DIST_OBJ_KEY_REGEX = re.compile(
        r'^p-([0-9A-Fa-f]{4,64})\/e-([0-9A-Fa-f]{4,64})\/cg-default$'
    )

    @property
    def status(self) -> ConfigbeeStatus:
        """Get current status"""
        return self._status

    def __init__(self, 
                 account_id: str,
                 project_id: str,
                 environment_id: str,
                 logger=None
                 ):
        """
        Initialize ConfigBee client.
        
        Args:
            account_id: Your ConfigBee account ID
            project_id: Your ConfigBee project ID
            environment_id: Your ConfigBee environment ID
        """

        self._account_id = account_id
        self._project_id = project_id
        self._environment_id = environment_id
        self._config_group_key = "default"


        if logger is None:
            logger = logging.getLogger("Configbee")
            logger.setLevel(logging.ERROR)
        self._logger = logger
        
        self._http_client = get_http_client()
        
        # Initialize status
        self._status = None

        # Initialize data structures
        self._current_config_groups_data: Dict[str, object] = {}

        self._dist_object_current_version_id = None
        
        # Initialize keys
        self._sse_base_url = _client_config.CB_DEFAULT_SSE_BASE_URL
        self._cdn_cached_fetch_base_url = _client_config.CB_DEFAULT_CDN_CACHED_FETCH_BASE_URL
        self._static_store_fetch_base_url = _client_config.CB_DEFAULT_STATIC_STORE_FETCH_BASE_URL
        self._direct_fetch_base_url = _client_config.CB_DEFAULT_DIRECT_FETCH_BASE_URL
        
        self._env_key = f"a-{account_id}/p-{project_id}/e-{environment_id}"
        self._distribution_obj_key = f"a-{account_id}/p-{project_id}/e-{environment_id}/cg-{self._config_group_key}"
        self._default_group_obj_key = f"p-{project_id}/e-{environment_id}/cg-{self._config_group_key}"
        
        # Threading and async support
        self._loop = None
        self._thread = None
        self._loaded_condition = threading.Condition()
    
    def init(self):
        """Initialize the ConfigBee client"""
        self._thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self._thread.start()

    def _run_async_loop(self):
        """Run the async event loop in a separate thread"""
        try:
            self._loop = asyncio.new_event_loop()
            self._loop.run_until_complete(self._run_sse())
        except Exception as e:
            self._logger.error(f"Error in async loop: {e}")
            self._status = ConfigbeeStatus.ERROR
            with self._loaded_condition:
                self._loaded_condition.notify_all()

    async def _handle_distribution_obj(self, obj):
        obj_key = obj.get("key") or self._default_group_obj_key

        if self.ENV_DEFAULT_CONFIG_GROUP_DIST_OBJ_KEY_REGEX.match(obj_key):
            if ("default" not in self._current_config_groups_data or 
                self._current_config_groups_data["default"]["meta"]["versionTs"] < obj["meta"]["versionTs"]):
                self._current_config_groups_data["default"] = obj
                if obj["meta"]["versionId"]:
                    self._dist_object_current_version_id = obj["meta"]["versionId"]
        else:
            pass
            """
            if "default" not in self.current_targeting_data:
                self.current_targeting_data["default"] = {"distribution_data": {}}
            
            existing_obj = self.current_targeting_data["default"]["distribution_data"].get(obj_key)
            if existing_obj is None or existing_obj["meta"]["versionTs"] < obj["meta"]["versionTs"]:
                self.current_targeting_data["default"]["distribution_data"][obj_key] = obj
            """

    async def _fetch_http(self, url):
        http_client = self._http_client
        r = await http_client.get(url)
        if(r.status_code!=200):
            raise Exception(f"Http status code: {r.status_code}")
        return r.json()
    
    async def _fetch_http_retry(self, url, retries=3, wait_time=0.2, stop_on_status_code=True):
        while True:
            try:
                return await self._fetch_http(url)
            except Exception as e:
                if stop_on_status_code:
                    if str(e).startswith("Http status code: "):
                        raise e
                retries -= 1
                if retries<=0:
                    raise e
                await asyncio.sleep(wait_time)
        
    
    async def do_initial_load(self):
        json_obj = None
        #when no version available, try store, direct, and CDN
        if not self._dist_object_current_version_id:
            url = self._get_http_path(base_url=self._static_store_fetch_base_url)
            try:
                json_obj = await self._fetch_http_retry(url=url)
            except Exception as e_store:
                self._logger.info(f"failed to fetch from static store {e_store}. trying from direct")
                url = self._get_http_path(base_url=self._direct_fetch_base_url)
                try:
                    json_obj = await self._fetch_http_retry(url=url)
                except Exception as e_direct:
                    self._logger.info(f"failed to fetch from direct {e_direct}. trying from cdn")
                    url = self._get_http_path(base_url=self._cdn_cached_fetch_base_url)
                    try:
                        json_obj = await self._fetch_http_retry(url=url)
                    except Exception as e_cdn:
                        self._logger.info(f"failed to fetch from cdn {e_cdn}.")
                        raise Exception("intial load failed")
        #when version available, try CDN, store and direct
        else:
            url = self._get_http_path(base_url=self._cdn_cached_fetch_base_url)
            try:
                json_obj = await self._fetch_http_retry(url=url)
            except Exception as e_cdn:
                self._logger.info(f"failed to fetch from cdn {e_cdn}. trying static store")
                url = self._get_http_path(base_url=self._static_store_fetch_base_url)
                try:
                    json_obj = await self._fetch_http_retry(url=url)
                except Exception as e_store:
                    self._logger.info(f"failed to fetch from static store {e_store}. trying direct")
                    url = self._get_http_path(base_url=self._direct_fetch_base_url)
                    try:
                        json_obj = await self._fetch_http_retry(url=url)
                    except Exception as e_direct:
                        self._logger.info(f"failed to fetch from static direct {e_direct}.")
                        raise Exception("intial load failed")
        await self._handle_distribution_obj(json_obj)
    
    async def _do_load_new_version(self, version_id):
        json_obj = None
        #try direct, store, and cdn
        url = self._get_http_path(base_url=self._direct_fetch_base_url, version_id=version_id)
        try:
            json_obj = await self._fetch_http_retry(url=url)
        except Exception as e_direct:
            self._logger.error(f"failed to fetch from direct {e_direct}.")
            url = self._get_http_path(base_url=self._static_store_fetch_base_url, version_id=version_id)
            try:
                json_obj = await self._fetch_http_retry(url=url)
            except Exception as e_store:
                self._logger.error(f"failed to fetch from static store {e_store}.")
                url = self._get_http_path(base_url=self._cdn_cached_fetch_base_url, version_id=version_id)
                try:
                    json_obj = await self._fetch_http_retry(url=url)
                except Exception as e_cdn:
                    #self._logger.error(f"failed to fetch from cdn {e_store}.")
                    raise e_direct
        await self._handle_distribution_obj(json_obj)

    async def _run_sse(self):
        self._status = ConfigbeeStatus.INITIALIZING
        try:
            self._logger.debug("initializing ConfigBee client.")
            await self.do_initial_load()
            self._status = ConfigbeeStatus.ACTIVE
            self._logger.debug("initialization of ConfigBee client completed.")
            with self._loaded_condition:
                self._loaded_condition.notify_all()
            while True:
                try:
                    await self._run_sse_once()
                except Exception as e:
                    self._logger.debug(f"error in sse connection {e}.")
                    await asyncio.sleep(1)
        except Exception as e:
            self._logger.error(e)
            self._status = ConfigbeeStatus.ERROR
            with self._loaded_condition:
                self._loaded_condition.notify_all()
    
    async def _run_sse_once(self):
        sse_url = f"{self._sse_base_url}{self._distribution_obj_key}.events"
        timeout = httpx.Timeout(10,read=40)
        async with httpx.AsyncClient(timeout=timeout) as httpx_client:
            async with aconnect_sse(
                httpx_client, "GET", sse_url) as event_source:
                async for sse in event_source.aiter_sse():
                    await self._handle_ss_event(sse)
    
    async def _handle_ss_event(self, event: ServerSentEvent):
        self._logger.debug(f"handling ss event: {event}")
        event_data = json.loads(event.data)
        event_meta = event_data.get("meta") or {}
        version_id = event_meta.get("versionId")
        version_ts = event_meta.get("versionTs")

        current_version_ts = None
        if self._current_config_groups_data.get("default"):
            current_version_ts = self._current_config_groups_data.get("default")["meta"]["versionTs"]
        
        if not current_version_ts or (current_version_ts < version_ts):
            await self._do_load_new_version(version_id=version_id)

    def _get_http_path(self, base_url: str, distribution_obj_key: Optional[str] = None, 
                      version_id: Optional[str] = None, use_versioned_url: bool = True) -> str:
        """Get HTTP path for fetching data"""
        if distribution_obj_key is None:
            distribution_obj_key = self._distribution_obj_key
        
        if use_versioned_url or version_id:
            url_version_id = version_id or self._dist_object_current_version_id
            if url_version_id:
                return urljoin(base_url, f"{distribution_obj_key}--v-{url_version_id}.json")
        
        return urljoin(base_url, f"{distribution_obj_key}.json")
    
    def get_flag(self, key) -> Optional[bool]:
        dist_obj = self._current_config_groups_data.get("default")
        if not dist_obj:
            return
        content = dist_obj.get("content") or {}
        
        valueObj = content.get(key)
        if valueObj.get("optionType") == "FLAG":
            return valueObj.get("flagValue")
    
    def get_text(self, key) -> Optional[str]:
        dist_obj = self._current_config_groups_data.get("default")
        if not dist_obj:
            return
        content = dist_obj.get("content") or {}
        
        valueObj = content.get(key)
        if valueObj.get("optionType") == "TEXT":
            return valueObj.get("textValue")
    
    def get_number(self, key) -> Optional[float]:
        dist_obj = self._current_config_groups_data.get("default")
        if not dist_obj:
            return
        content = dist_obj.get("content") or {}
        
        valueObj = content.get(key)
        if valueObj.get("optionType") == "NUMBER":
            return float(valueObj.get("numberValue"))
    
    def get_json(self, key) -> Optional[object]:
        dist_obj = self._current_config_groups_data.get("default")
        if not dist_obj:
            return
        content = dist_obj.get("content") or {}
        
        valueObj = content.get(key)
        if valueObj.get("optionType") == "JSON":
            return valueObj.get("jsonValue")
    
    def get_all_flags(self) -> Optional[Dict[str, bool]]:
        dist_obj = self._current_config_groups_data.get("default")
        if not dist_obj:
            return
        content = dist_obj.get("content") or {}
        
        return {k: v.get("flagValue") for k, v in content.items() if v.get("optionType") == "FLAG"}

    def get_all_texts(self) -> Optional[Dict[str, str]]:
        dist_obj = self._current_config_groups_data.get("default")
        if not dist_obj:
            return
        content = dist_obj.get("content") or {}
        
        return {k: v.get("textValue") for k, v in content.items() if v.get("optionType") == "TEXT"}
    
    def get_all_numbers(self) -> Optional[Dict[str, float]]:
        dist_obj = self._current_config_groups_data.get("default")
        if not dist_obj:
            return
        content = dist_obj.get("content") or {}
        
        return {k: v.get("numberValue") for k, v in content.items() if v.get("optionType") == "NUMBER"}
    
    def get_all_jsons(self) -> Optional[Dict[str,  object]]:
        dist_obj = self._current_config_groups_data.get("default")
        if not dist_obj:
            return
        content = dist_obj.get("content") or {}
        
        return {k: v.get("jsonValue") for k, v in content.items() if v.get("optionType") == "JSON"}
    
    def wait_to_load(self, timeout=40):
        if self.status == ConfigbeeStatus.ACTIVE:
            return
        if self.status == ConfigbeeStatus.ERROR:
            raise Exception(f"invalid Configbee client status: {self.status}")
        with self._loaded_condition:
            self._loaded_condition.wait(timeout)
        if self.status != ConfigbeeStatus.ACTIVE:
            raise Exception(f"invalid Configbee client status: {self.status}")
    
    
    async def await_to_load(self, timeout=40):
        #intent to call from other loops
        running_loop = asyncio.get_running_loop()
        await running_loop.run_in_executor(None, self.wait_to_load, timeout)