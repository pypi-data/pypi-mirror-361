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

from voe.pattern import node, wildcard
from voe.rule_ext import Rule


class GraphLabelBaseRule(Rule):
    def action(self, **kwargs):
        pass


class ReluConv(GraphLabelBaseRule):
    """
    Match : Relu(Conv(x,w))
    """

    def pattern(self):
        X = wildcard()
        W = wildcard()
        B = wildcard()
        conv = node("Conv", X, W, [B])
        relu = node("Relu", conv)
        return relu.build(locals())

    def where(self, **_kwargs):
        return True


class Conv(GraphLabelBaseRule):
    """
    Match : Conv(x,w)
    """

    def pattern(self):
        X = wildcard()
        W = wildcard()
        B = wildcard()
        conv = node("Conv", X, W, [B])
        return conv.build(locals())

    def where(self, **_kwargs):
        return True


def rules():
    return [ReluConv(), Conv()]
