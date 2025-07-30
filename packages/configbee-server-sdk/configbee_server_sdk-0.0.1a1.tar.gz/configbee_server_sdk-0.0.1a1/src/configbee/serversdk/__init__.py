from . import _client
from ._client import ConfigbeeClient
import logging

__CLIENTS = dict()

def get_client(account_id: str, project_id: str, environment_id:str, logger:logging.Logger=None) -> ConfigbeeClient:
    client_key = f"a-{account_id}/p-{project_id}/e-{environment_id}"
    if client_key in __CLIENTS:
        return __CLIENTS[client_key]
    
    cb_client = _client.ConfigbeeClient(account_id, project_id, environment_id, logger=logger)
    __CLIENTS[client_key] = cb_client
    cb_client.init()
    return cb_client