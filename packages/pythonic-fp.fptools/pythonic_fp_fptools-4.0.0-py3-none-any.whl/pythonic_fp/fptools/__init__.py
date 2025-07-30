# Copyright 2023-2025 Geoffrey R. Scheller
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

"""Pythonic FP - Functional Programming Tools

Tools to aid with functional programming in Python yet still endeavoring to
remain Pythonic.

- Subclassable Boolean datatype (*module* `pythonic_fp.fptools.bool`)
- Functions as first class objects (*module* `pythonic_fp.fptools.function`)
- Lazy (non-strict) function evaluation (*module* `pythonic_fp.fptools.lazy`)
- Singletons (*module* `pythonic_fp.fptools.singletons`)

  - 3 singleton classes representing

    - a missing value (actually missing, not potentially missing)
    - a sentinel values
    - a failed calculation

- State monad implementation (*module* `pythonic_fp.fptools.state`)

  - pure FP handling of state (the state monad)
  - Classic FP implementation

    - the monad encapsulates a state transformation, not a "state"

"""

__author__ = 'Geoffrey R. Scheller'
__copyright__ = 'Copyright (c) 2023-2025 Geoffrey R. Scheller'
__license__ = 'Apache License 2.0'
