#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from typing import overload, Dict, Union, Optional
from py4j.java_gateway import JavaObject

from pyspark.resource.requests import (
    TaskResourceRequest,
    TaskResourceRequests,
    ExecutorResourceRequests,
    ExecutorResourceRequest,
)


class ResourceProfile:

    """
    Resource profile to associate with an RDD. A :class:`pyspark.resource.ResourceProfile`
    allows the user to specify executor and task requirements for an RDD that will get
    applied during a stage. This allows the user to change the resource requirements between
    stages. This is meant to be immutable so user cannot change it after building.

    .. versionadded:: 3.1.0

    Notes
    -----
    This API is evolving.
    """

    @overload
    def __init__(self, _java_resource_profile: JavaObject):
        ...

    @overload
    def __init__(
        self,
        _java_resource_profile: None = ...,
        _exec_req: Optional[Dict[str, ExecutorResourceRequest]] = ...,
        _task_req: Optional[Dict[str, TaskResourceRequest]] = ...,
    ):
        ...

    def __init__(
        self,
        _java_resource_profile: Optional[JavaObject] = None,
        _exec_req: Optional[Dict[str, ExecutorResourceRequest]] = None,
        _task_req: Optional[Dict[str, TaskResourceRequest]] = None,
    ):
        if _java_resource_profile is not None:
            self._java_resource_profile = _java_resource_profile
        else:
            self._java_resource_profile = None
            self._executor_resource_requests = _exec_req or {}
            self._task_resource_requests = _task_req or {}

    @property
    def id(self) -> int:
        if self._java_resource_profile is not None:
            return self._java_resource_profile.id()
        else:
            raise RuntimeError(
                "SparkContext must be created to get the id, get the id "
                "after adding the ResourceProfile to an RDD"
            )

    @property
    def taskResources(self) -> Dict[str, TaskResourceRequest]:
        if self._java_resource_profile is not None:
            taskRes = self._java_resource_profile.taskResourcesJMap()
            result = {}
            for k, v in taskRes.items():
                result[k] = TaskResourceRequest(v.resourceName(), v.amount())
            return result
        else:
            return self._task_resource_requests

    @property
    def executorResources(self) -> Dict[str, ExecutorResourceRequest]:
        if self._java_resource_profile is not None:
            execRes = self._java_resource_profile.executorResourcesJMap()
            result = {}
            for k, v in execRes.items():
                result[k] = ExecutorResourceRequest(
                    v.resourceName(), v.amount(), v.discoveryScript(), v.vendor()
                )
            return result
        else:
            return self._executor_resource_requests


class ResourceProfileBuilder:

    """
    Resource profile Builder to build a resource profile to associate with an RDD.
    A ResourceProfile allows the user to specify executor and task requirements for
    an RDD that will get applied during a stage. This allows the user to change the
    resource requirements between stages.

    .. versionadded:: 3.1.0

    Notes
    -----
    This API is evolving.
    """

    def __init__(self) -> None:
        from pyspark.context import SparkContext

        # TODO: ignore[attr-defined] will be removed, once SparkContext is inlined
        _jvm = SparkContext._jvm  # type: ignore[attr-defined]
        if _jvm is not None:
            self._jvm = _jvm
            self._java_resource_profile_builder = (
                _jvm.org.apache.spark.resource.ResourceProfileBuilder()
            )
        else:
            self._jvm = None
            self._java_resource_profile_builder = None
            self._executor_resource_requests: Optional[Dict[str, ExecutorResourceRequest]] = {}
            self._task_resource_requests: Optional[Dict[str, TaskResourceRequest]] = {}

    def require(
        self, resourceRequest: Union[ExecutorResourceRequest, TaskResourceRequests]
    ) -> "ResourceProfileBuilder":
        if isinstance(resourceRequest, TaskResourceRequests):
            if self._java_resource_profile_builder is not None:
                if (
                    resourceRequest._java_task_resource_requests is not None
                ):  # type: ignore[attr-defined]
                    self._java_resource_profile_builder.require(
                        resourceRequest._java_task_resource_requests
                    )  # type: ignore[attr-defined]
                else:
                    taskReqs = TaskResourceRequests(self._jvm, resourceRequest.requests)
                    self._java_resource_profile_builder.require(
                        taskReqs._java_task_resource_requests
                    )  # type: ignore[attr-defined]
            else:
                self._task_resource_requests.update(  # type: ignore[union-attr]
                    resourceRequest.requests
                )
        else:
            if self._java_resource_profile_builder is not None:
                if (
                    resourceRequest._java_executor_resource_requests is not None  # type: ignore[attr-defined]
                ):
                    self._java_resource_profile_builder.require(
                        resourceRequest._java_executor_resource_requests  # type: ignore[attr-defined]
                    )
                else:
                    execReqs = ExecutorResourceRequests(
                        self._jvm, resourceRequest.requests  # type: ignore[attr-defined]
                    )
                    self._java_resource_profile_builder.require(
                        execReqs._java_executor_resource_requests  # type: ignore[attr-defined]
                    )
            else:
                self._executor_resource_requests.update(  # type: ignore[union-attr]
                    resourceRequest.requests  # type: ignore[attr-defined]
                )
        return self

    def clearExecutorResourceRequests(self) -> None:
        if self._java_resource_profile_builder is not None:
            self._java_resource_profile_builder.clearExecutorResourceRequests()
        else:
            self._executor_resource_requests = {}

    def clearTaskResourceRequests(self) -> None:
        if self._java_resource_profile_builder is not None:
            self._java_resource_profile_builder.clearTaskResourceRequests()
        else:
            self._task_resource_requests = {}

    @property
    def taskResources(self) -> Optional[Dict[str, TaskResourceRequest]]:
        if self._java_resource_profile_builder is not None:
            taskRes = self._java_resource_profile_builder.taskResourcesJMap()
            result = {}
            for k, v in taskRes.items():
                result[k] = TaskResourceRequest(v.resourceName(), v.amount())
            return result
        else:
            return self._task_resource_requests

    @property
    def executorResources(self) -> Optional[Dict[str, ExecutorResourceRequest]]:
        if self._java_resource_profile_builder is not None:
            result = {}
            execRes = self._java_resource_profile_builder.executorResourcesJMap()
            for k, v in execRes.items():
                result[k] = ExecutorResourceRequest(
                    v.resourceName(), v.amount(), v.discoveryScript(), v.vendor()
                )
            return result
        else:
            return self._executor_resource_requests

    @property
    def build(self) -> ResourceProfile:
        if self._java_resource_profile_builder is not None:
            jresourceProfile = self._java_resource_profile_builder.build()
            return ResourceProfile(_java_resource_profile=jresourceProfile)
        else:
            return ResourceProfile(
                _exec_req=self._executor_resource_requests, _task_req=self._task_resource_requests
            )
