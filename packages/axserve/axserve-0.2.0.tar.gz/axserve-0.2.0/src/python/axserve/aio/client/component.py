# Copyright 2023 Yunseong Hwang
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import asyncio
import contextlib
import typing

from asyncio import Task
from collections import defaultdict
from collections.abc import AsyncIterator
from collections.abc import Callable
from collections.abc import Coroutine
from collections.abc import Mapping
from typing import TYPE_CHECKING
from weakref import WeakValueDictionary

import grpc

from axserve.aio.client.descriptor import AxServeEvent
from axserve.aio.client.descriptor import AxServeMember
from axserve.aio.client.descriptor import AxServeMethod
from axserve.aio.client.descriptor import AxServeProperty
from axserve.aio.common.async_aquireable import AsyncAquireable
from axserve.aio.common.async_initializable import AsyncInitializable
from axserve.aio.common.async_iterable_queue import AsyncIterableQueue
from axserve.proto import active_pb2
from axserve.proto.active_pb2_conversion import ValueFromVariant
from axserve.proto.active_pb2_grpc import ActiveStub


if TYPE_CHECKING:
    from axserve.aio.client.stub import AxServeObject


class AxServeEventContextManager:
    def __init__(self):
        self._handle_event_context_stack = []

    def _get_handle_event_context_stack(self) -> list[active_pb2.HandleEventRequest]:
        return self._handle_event_context_stack

    def _get_current_handle_event(self) -> active_pb2.HandleEventRequest | None:
        handle_event_context_stack = self._get_handle_event_context_stack()
        return handle_event_context_stack[-1] if handle_event_context_stack else None

    def _contextualize_request(self, request):
        current_handle_event = self._get_current_handle_event()
        if not current_handle_event:
            return request
        context_type = active_pb2.ContextType.EVENT
        request.context.context_type = context_type
        request.context.context_info.id = current_handle_event.id
        request.context.context_info.instance = current_handle_event.instance
        request.context.context_info.index = current_handle_event.index
        return request


class AxServeEventHandlersManager:
    def __init__(self):
        self._event_handlers_mapping: Mapping[int, list[Callable]] = defaultdict(list)
        self._event_handlers_lock_mapping: Mapping[int, AsyncAquireable] = defaultdict(asyncio.Lock)  # type: ignore

    def _get_event_handlers(self, index: int) -> list[Callable]:
        return self._event_handlers_mapping[index]

    def _get_event_handlers_lock(self, index: int) -> AsyncAquireable:
        return self._event_handlers_lock_mapping[index]


class AxServeEventStreamManager:
    def __init__(self, stub: ActiveStub, *, use_response_queue: bool = False):
        self._use_response_queue = use_response_queue
        if self._use_response_queue:
            self._handle_event_response_queue = AsyncIterableQueue()
            self._handle_event_requests = stub.HandleEvent(self._handle_event_response_queue)
        else:
            self._handle_event_requests = stub.HandleEvent()

    def _get_handle_event_requests(self) -> AsyncIterator[active_pb2.HandleEventRequest]:
        return self._handle_event_requests

    async def _put_handle_event_response(self, response: active_pb2.HandleEventResponse) -> None:
        if self._use_response_queue:
            return await self._handle_event_response_queue.put(response)
        else:
            handle_events = typing.cast(grpc.aio.StreamStreamCall, self._handle_event_requests)
            return await handle_events.write(response)

    async def _close_event_stream(self) -> None:
        if self._use_response_queue:
            return await self._handle_event_response_queue.close()
        else:
            handle_events = typing.cast(grpc.aio.StreamStreamCall, self._handle_event_requests)
            return await handle_events.done_writing()

    def _cancel_event_stream(self) -> bool:
        handle_events = typing.cast(grpc.aio.RpcContext, self._handle_event_requests)
        return handle_events.cancel()


class AxServeInstancesManager:
    def __init__(self):
        self._instances = WeakValueDictionary()

    def _register_instance(self, i: str, o: AxServeObject):
        self._instances[i] = o

    def _unregister_instance(self, i: str):
        del self._instances[i]

    def _has_instance(self, i: str) -> bool:
        return i in self._instances

    def _get_instance(self, i: str) -> AxServeObject | None:
        return self._instances.get(i)


class AxServeMembersManager(AsyncInitializable):
    def __init__(
        self,
        instance: str,
        stub: ActiveStub,
        context_manager: AxServeEventContextManager,
    ):
        AsyncInitializable.__init__(self, instance, stub, context_manager)

    async def __ainit__(
        self,
        instance: str,
        stub: ActiveStub,
        context_manager: AxServeEventContextManager,
    ):
        self._members_dict: dict[str, AxServeMember] = {}

        self._properties_list: list[AxServeProperty] = []
        self._properties_dict: dict[str, AxServeProperty] = {}
        self._methods_list: list[AxServeMethod] = []
        self._methods_dict: dict[str, AxServeMethod] = {}
        self._events_list: list[AxServeEvent] = []
        self._events_dict: dict[str, AxServeEvent] = {}

        request = active_pb2.DescribeRequest()
        request.instance = instance
        context_manager._contextualize_request(request)
        response = await stub.Describe(request)
        response = typing.cast(active_pb2.DescribeResponse, response)

        for info in response.properties:
            prop = AxServeProperty(info)
            self._properties_list.append(prop)
            self._properties_dict[info.name] = prop
            if info.name not in self._members_dict:
                self._members_dict[info.name] = AxServeMember()
            self._members_dict[info.name]._property = prop
        for info in response.methods:
            method = AxServeMethod(info)
            self._methods_list.append(method)
            self._methods_dict[info.name] = method
            if info.name not in self._members_dict:
                self._members_dict[info.name] = AxServeMember()
            self._members_dict[info.name]._method = method
        for info in response.events:
            info.name = self._make_event_method_name(info.name)
            event = AxServeEvent(info)
            self._events_list.append(event)
            self._events_dict[info.name] = event
            if info.name not in self._members_dict:
                self._members_dict[info.name] = AxServeMember()
            self._members_dict[info.name]._event = event

    @classmethod
    def _make_event_method_name(cls, name: str) -> str:
        if not name.startswith("On"):
            name = "On" + name
        return name

    def _get_property(self, index: int) -> AxServeProperty:
        return self._properties_list[index]

    def _get_method(self, index: int) -> AxServeMethod:
        return self._methods_list[index]

    def _get_event(self, index: int) -> AxServeEvent:
        return self._events_list[index]

    def _has_member_name(self, name: str) -> bool:
        return name in self._members_dict

    def _get_member_by_name(self, name: str) -> AxServeMember:
        return self._members_dict[name]

    def _get_member_names(self) -> list[str]:
        return list(self._members_dict.keys())


class AxServeMembersManagerCache:
    def __init__(
        self,
        stub: ActiveStub,
        context_manager: AxServeEventContextManager,
    ):
        self._stub = stub
        self._context_manager = context_manager
        self._members_managers = {}

    async def _get_members_manager(self, c: str, i: str) -> AxServeMembersManager:
        if c not in self._members_managers:
            members_manager = AxServeMembersManager(i, self._stub, self._context_manager)
            await members_manager.__aenter__()
            self._members_managers[c] = members_manager
        members_manager = self._members_managers[c]
        return members_manager


class AxServeEventLoop:
    def __init__(
        self,
        instances_manager: AxServeInstancesManager,
        event_context_manager: AxServeEventContextManager,
        event_stream_manager: AxServeEventStreamManager,
    ):
        self._instances_manager = instances_manager
        self._event_context_manager = event_context_manager
        self._event_stream_manager = event_stream_manager

        self._state_lock = asyncio.Lock()
        self._is_exitting = False
        self._is_running = False
        self._return_code = 0

    @contextlib.asynccontextmanager
    async def _create_exec_context(self):
        async with self._state_lock:
            self._is_exitting = False
            self._is_running = True
        try:
            yield
        finally:
            async with self._state_lock:
                self._is_exitting = False
                self._is_running = False

    @contextlib.asynccontextmanager
    async def _create_handle_event_context(self, handle_event: active_pb2.HandleEventRequest):
        event_context_stack = self._event_context_manager._get_handle_event_context_stack()
        event_context_stack.append(handle_event)
        try:
            yield
        finally:
            event_context_stack.pop()
            response = active_pb2.HandleEventResponse()
            response.id = handle_event.id
            response.instance = handle_event.instance
            response.index = handle_event.index
            await self._event_stream_manager._put_handle_event_response(response)

    async def exec(self) -> int:
        async with self._create_exec_context():
            handle_events = self._event_stream_manager._get_handle_event_requests()
            try:
                async for handle_event in handle_events:
                    if handle_event.is_pong:
                        return self._return_code
                    async with self._create_handle_event_context(handle_event):
                        args = [ValueFromVariant(arg) for arg in handle_event.arguments]
                        if not self._instances_manager._has_instance(handle_event.instance):
                            continue
                        instance = self._instances_manager._get_instance(handle_event.instance)
                        if not instance:
                            continue
                        if instance.__axserve__ is None:
                            continue
                        event_callback = instance.__axserve__._members_manager._get_event(handle_event.index)
                        await event_callback(instance, *args)
            except grpc.RpcError as exc:
                if not (self._is_exitting and isinstance(exc, grpc.Call) and exc.code() == grpc.StatusCode.CANCELLED):
                    raise exc
        return self._return_code

    def is_running(self) -> bool:
        return self._is_running

    async def exit(self, return_code: int = 0) -> None:
        async with self._state_lock:
            if not self._is_running:
                return
            if self._is_exitting:
                return
            self._is_exitting = True
            self._return_code = return_code
        response = active_pb2.HandleEventResponse()
        response.is_ping = True
        await self._event_stream_manager._put_handle_event_response(response)


class AxServeEventLoopManager:
    def __init__(
        self,
        instances_manager: AxServeInstancesManager,
        event_context_manager: AxServeEventContextManager,
        event_stream_manager: AxServeEventStreamManager,
    ):
        self._instances_manager = instances_manager
        self._event_context_manager = event_context_manager
        self._event_stream_manager = event_stream_manager

        self._event_loop: AxServeEventLoop | None = None
        self._event_loop_exec_coro: Coroutine | None = None
        self._event_loop_exec_task: Task | None = None
        self._event_loop_exception: BaseException | None = None

    async def _event_loop_exec_target(self):
        if not self._event_loop:
            return
        try:
            await self._event_loop.exec()
        except grpc.RpcError as exc:
            self._event_loop_exception = exc
            self = None  # noqa: PLW0642
            if (
                isinstance(exc, grpc.aio.AioRpcError)
                and exc.code() == grpc.StatusCode.CANCELLED
                and isinstance(exc, grpc.aio.RpcContext)
                and exc.done()
            ):
                return
            raise exc
        except BaseException as exc:
            self._event_loop_exception = exc
            self = None  # noqa: PLW0642
            raise exc

    def start(self) -> None:
        if not self._event_loop:
            self._event_loop = AxServeEventLoop(
                self._instances_manager,
                self._event_context_manager,
                self._event_stream_manager,
            )
        if not self._event_loop_exec_task:
            self._event_loop_exec_coro = self._event_loop_exec_target()
            self._event_loop_exec_task = asyncio.create_task(self._event_loop_exec_coro)

    async def stop(self) -> None:
        if self._event_loop:
            await self._event_loop.exit()
            self._event_loop = None
        if self._event_loop_exec_task:
            await self._event_loop_exec_task
            self._event_loop_exec_task = None
