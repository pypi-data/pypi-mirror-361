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
import onnxruntime as ort
import sys


def main():
    if len(sys.argv) < 3:
        print(
            "usage: python -m voe.tools.generate_test_cases <onnx model> <json_config>"
        )
        return
    ort.InferenceSession(
        sys.argv[1],
        providers=["VitisAIExecutionProvider"],
        provider_options=[{"config_file": sys.argv[2]}],
    )


if __name__ == "__main__":
    main()
