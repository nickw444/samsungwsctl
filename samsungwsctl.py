import base64
import json
import logging
import ssl
from dataclasses import dataclass
from os import path
from typing import Optional

import requests
import websocket

_LOGGER = logging.getLogger(__name__)


@dataclass
class GetInfoResponse:
    id: str
    name: str
    version: str
    power_state: str


@dataclass
class GetAppInfoResponse:
    id: str
    name: str
    running: bool
    version: str
    visible: bool


class Remote():
    def __init__(self, host: str, port: int, secure: bool,
                 token_file: Optional[str], remote_name: str,
                 timeout: int = 1):
        self._host = host
        self._port = port
        self._secure = secure
        self._token_file_path = token_file
        self._remote_name = remote_name
        self._timeout = timeout
        self._connection = None

        self._token = self._load_token()

    def _connect(self):
        url = self._get_ws_connection_url()

        _LOGGER.debug("Opening ws connection: %s", url)
        connection = websocket.create_connection(url, self._timeout, sslopt={
            'cert_reqs': ssl.CERT_NONE
        })

        if self._token is None:
            # Read response during connection and persist token
            resp = connection.recv()
            data = json.loads(resp)
            if 'data' in data and 'token' in data['data']:
                self._token = data['data']['token']
                self._save_token(self._token)
            else:
                raise ValueError('Invalid response during connection. Cannot '
                                 'persist token')

        return connection

    def disconnect(self):
        self._connection.close()
        self._connection = None

    def _send(self, data: str):
        if self._connection is not None:
            try:
                return self._connection.send(data)
            except Exception:
                self.disconnect()

        # Reconnect and retry sending.
        self._connection = self._connect()
        try:
            self._connection.send(data)
        except Exception as e:
            self.disconnect()
            raise e

    def get_info(self) -> GetInfoResponse:
        url = self._get_http_base_path() + '/'
        resp = requests.get(url, timeout=self._timeout, verify=False)
        resp.raise_for_status()

        data = resp.json()
        return GetInfoResponse(
            id=data['id'],
            name=data['name'],
            version=data['version'],
            power_state=data['device']['PowerState']
        )

    def send_key(self, key: str):
        _LOGGER.debug('Sending key: %s', key)

        payload = {
            "method": "ms.remote.control",
            "params": {
                "Cmd": "Click",
                "DataOfCmd": key,
                "Option": "false",
                "TypeOfRemote": "SendRemoteKey"
            }
        }
        self._send(json.dumps(payload))

    def start_app(self, app_id: str):
        url = self._get_http_base_path() + f'/applications/{app_id}'
        resp = requests.post(url, timeout=self._timeout, verify=False)
        resp.raise_for_status()

    def stop_app(self, app_id: str):
        url = self._get_http_base_path() + f'/applications/{app_id}'
        resp = requests.delete(url, timeout=self._timeout, verify=False)
        resp.raise_for_status()

    def get_app_info(self, app_id: str) -> GetAppInfoResponse:
        url = self._get_http_base_path() + f'/applications/{app_id}'
        resp = requests.get(url, timeout=self._timeout, verify=False)
        resp.raise_for_status()

        return GetAppInfoResponse(**resp.json())

    def _get_ws_connection_url(self):
        protocol = 'wss' if self._secure else 'ws'
        token_component = f'&token={self._token}' if self._token else ''
        return (f'{protocol}://{self._host}:{self._port}/api/v2/channels/'
                f'samsung.remote.control?name={_encode_str(self._remote_name)}'
                f'{token_component}')

    def _get_http_base_path(self):
        protocol = 'https' if self._secure else 'http'
        return f'{protocol}://{self._host}:{self._port}/api/v2'

    def _save_token(self, token: str):
        if self._token_file_path is not None:
            with open(self._token_file_path, 'w') as f:
                f.write(token)

    def _load_token(self) -> Optional[str]:
        if self._token_file_path is not None and path.isfile(
                self._token_file_path):
            _LOGGER.debug('Loading token from %s', self._token_file_path)
            with open(self._token_file_path, 'r') as f:
                return f.read().strip()


def _encode_str(string: str):
    return base64.b64encode(string.encode('utf-8')).decode("utf-8")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    remote = Remote(
        host='192.168.2.20',
        port=8002,
        secure=True,
        token_file=path.realpath('token.txt'),
        remote_name='samsungwsctl',
        timeout=10
    )

    while True:
        key = input('Key: ')
        remote.send_key(key)
