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

from dataclasses import asdict
from typing import Any, Callable, Sequence

from dkg.exceptions import ValidationError
from dkg.managers.async_manager import AsyncRequestManager
from dkg.method import Method
from dkg.types import TReturn


class AsyncModule:
    manager: AsyncRequestManager

    def retrieve_caller_fn(
        self, method: Method[Callable[..., TReturn]]
    ) -> Callable[..., TReturn]:
        async def caller(*args: Any, **kwargs: Any) -> TReturn:
            processed_args = method.process_args(*args, **kwargs)
            request_params = asdict(method.action)
            request_params.update(processed_args)

            return await self.manager.blocking_request(
                type(method.action), request_params
            )

        return caller

    def _attach_modules(self, module_definitions: dict[str, Any]) -> None:
        for module_name, module_info in module_definitions.items():
            module_info_is_list_like = isinstance(module_info, Sequence)

            module = module_info[0] if module_info_is_list_like else module_info

            if hasattr(self, module_name):
                raise AttributeError(
                    f"Cannot set {self} module named '{module_name}'. "
                    " The dkg object already has an attribute with that name"
                )

            setattr(self, module_name, module)

            if module_info_is_list_like:
                if len(module_info) == 2:
                    submodule_definitions = module_info[1]
                    module: "AsyncModule" = getattr(self, module_name)
                    module._attach_modules(submodule_definitions)
                elif len(module_info) != 1:
                    raise ValidationError(
                        "Module definitions can only have 1 or 2 elements."
                    )
