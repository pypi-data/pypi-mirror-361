import typing
from pydantic import parse_obj_as
from ...core.client_wrapper import AsyncClientWrapper, SyncClientWrapper
from ...core.request_options import RequestOptions
from .types.secret import Secret


class SecretsClient:
    def __init__(self, *, client_wrapper: SyncClientWrapper):
        self._client_wrapper = client_wrapper

    def get(
        self, *, name: str, request_options: typing.Optional[RequestOptions] = None
    ) -> str:
        """
        Get a secret by name

        Parameters:
            - name: str. The name of the secret.

            - request_options: typing.Optional[RequestOptions]. Request-specific configuration.
        """
        _response = self._client_wrapper.httpx_client.request(
            method="GET",
            path="api/public/secrets",
            params={"name": name},
            request_options=request_options,
        )
        return _response.json()


class AsyncSecretsClient:
    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        self._client_wrapper = client_wrapper

    async def get(
        self, *, name: str, request_options: typing.Optional[RequestOptions] = None
    ) -> str:
        """
        Get a secret by name

        Parameters:
            - name: str. The name of the secret.

            - request_options: typing.Optional[RequestOptions]. Request-specific configuration.
        """
        _response = await self._client_wrapper.httpx_client.request(
            method="GET",
            path="api/public/secrets",
            params={"name": name},
            request_options=request_options,
        )
        return _response.json()