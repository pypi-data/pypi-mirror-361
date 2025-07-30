# ============================================================================ #
#                                                                              #
#     Title   : Collection types                                               #
#     Purpose : Defines various type aliases for common collection types.      #
#                                                                              #
# ============================================================================ #


# ---------------------------------------------------------------------------- #
#                                                                              #
#     Setup                                                                 ####
#                                                                              #
# ---------------------------------------------------------------------------- #


## --------------------------------------------------------------------------- #
##  Imports                                                                 ####
## --------------------------------------------------------------------------- #


# ## Python StdLib Imports ----
from datetime import datetime
from typing import Any, Literal, Union


## --------------------------------------------------------------------------- #
##  Exports                                                                 ####
## --------------------------------------------------------------------------- #


__all__: list[str] = [
    "any_collection",
    "any_list",
    "any_list_tuple",
    "any_set",
    "any_tuple",
    "collection",
    "dict_any",
    "dict_str_int",
    "int_list",
    "int_tuple",
    "iterable",
    "log_levels",
    "scalar",
    "str_collection",
    "str_dict",
    "str_list",
    "str_list_tuple",
    "str_set",
    "str_tuple",
]


## --------------------------------------------------------------------------- #
##  Types                                                                   ####
## --------------------------------------------------------------------------- #


### `str` collections ----
str_list = list[str]
str_tuple = tuple[str, ...]
str_set = set[str]
str_list_tuple = Union[str_list, str_tuple]

### `int` collections ----
int_list = list[int]
int_tuple = tuple[int, ...]
int_set = set[int]
int_list_tuple = Union[int_list, int_tuple]

### `datetime` collections ----
datetime_list = list[datetime]
datetime_tuple = tuple[datetime, ...]
datetime_set = set[datetime]
datetime_list_tuple = Union[datetime_list, datetime_tuple]

### `Any` collections ----
any_list = list[Any]
any_tuple = tuple[Any, ...]
any_set = set[Any]
any_list_tuple = Union[any_list, any_tuple]

### Generic collections ----
collection = Union[any_list, any_tuple, any_set]
str_collection = Union[str_list, str_tuple, str_set]
any_collection = Union[any_list, any_tuple, any_set]

### basic collections ----
scalar = Union[str, int, float, bool]
iterable = Union[list, tuple, set, dict]

### `dict` collections ----
str_dict = dict[str, str]
dict_str_any = dict[str, Any]
dict_str_str = dict[str, str]
dict_int_str = dict[int, str]

dict_any = dict[
    Union[str, int],
    Union[str, int, float, list, tuple, dict],
]
"""
!!! note "Summary"
    To streamline other functions, this `type` alias is created for a `Dict` containing certain types.
!!! abstract "Details"
    The structure of the `type` is as follows:
    ```pycon {.py .python linenums="1" title="Type structure"}
    dict_any = Dict[
        Union[str, int],
        Union[str, int, float, list, tuple, dict],
    ]
    ```
"""

dict_str_int = dict[
    Union[str, int],
    Union[str, int],
]
"""
!!! note "Summary"
    To streamline other functions, this `type` alias is created for a `Dict` containing certain types.
!!! abstract "Details"
    The structure of the `type` is as follows:
    ```pycon {.py .python linenums="1" title="Type structure"}
    dict_str_int = Dict[
        Union[str, int],
        Union[str, int],
    ]
    ```
"""


log_levels = Literal["debug", "info", "warning", "error", "critical"]
"""
!!! note "Summary"
    To streamline other functions, this `type` alias is created for all of the `log` levels available.
!!! abstract "Details"
    The structure of the `type` is as follows:
    ```pycon {.py .python linenums="1" title="Type structure"}
    Literal["debug", "info", "warning", "error", "critical"]
    ```
"""
