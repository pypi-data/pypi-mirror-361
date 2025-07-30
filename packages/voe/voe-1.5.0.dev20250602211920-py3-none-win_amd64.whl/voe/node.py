##
# Copyright (C) 2023 – 2025 Advanced Micro Devices, Inc. All rights reserved.
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##  http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##

import voe.voe_cpp2py_export as v


class Node(object):
    def __init__(self, graph: v.GraphWrapper, node: v.Node) -> None:
        self._graph = graph
        self._node = node

    def __str__(self) -> str:
        return self._node.__str__()
