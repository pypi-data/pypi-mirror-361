# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from typing import Any

import requests
from dkg.dataclasses import HTTPRequestMethod, NodeResponseDict
from dkg.exceptions import HTTPRequestMethodNotSupported, NodeRequestError
from dkg.types import URI
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
from dkg.providers.node.base_node_http import BaseNodeHTTPProvider


class NodeHTTPProvider(BaseNodeHTTPProvider):
    def __init__(
        self,
        endpoint_uri: URI | str,
        api_version: str = "v1",
        auth_token: str | None = None,
    ):
        super().__init__(endpoint_uri, api_version, auth_token)

    def make_request(
        self,
        method: HTTPRequestMethod,
        path: str,
        params: dict[str, Any] = {},
        data: dict[str, Any] = {},
    ) -> NodeResponseDict:
        url = f"{self.url}/{path}"

        try:
            if method == HTTPRequestMethod.GET:
                response = requests.get(url, params=params, headers=self.headers)
            elif method == HTTPRequestMethod.POST:
                response = requests.post(url, json=data, headers=self.headers)
            else:
                raise HTTPRequestMethodNotSupported(
                    f"{method.name} method isn't supported"
                )

            response.raise_for_status()

            try:
                return NodeResponseDict(response.json())
            except ValueError as err:
                raise NodeRequestError(f"JSON decoding failed: {err}")

        except (HTTPError, ConnectionError, Timeout, RequestException) as err:
            raise NodeRequestError(f"Request failed: {err}")
