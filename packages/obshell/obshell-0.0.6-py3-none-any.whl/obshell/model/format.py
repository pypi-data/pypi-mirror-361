# coding: utf-8
# Copyright (c) 2024 OceanBase.
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

def model_str(cls):
    def __convert_value(value):
        if isinstance(value, list):
            return [__convert_value(item) for item in value]
        elif isinstance(value, dict):
            return {f"{key}": __convert_value(value) for key, value in value.items()}
        else:
            return str(value)
    members = ", ".join(
        f"\"{k}\":\"{__convert_value(v)}\"" for k, v in cls.__dict__.items())
    return '{' + members.replace("'", "\"") + '}'
