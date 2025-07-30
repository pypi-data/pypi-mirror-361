# -*- encoding: utf-8 -*-
import json
import http
from typing import Any, Optional, Callable


def _jsonify(
    code: int = http.HTTPStatus.OK.value,
    msg: Optional[str] = None,
    data: Any = None,
    method: Optional[str] = None,
):
    """ """

    res_data = {
        "code": code,
        "meta": {"endpoint": method, "close": 1},
        "data": data,
        "msg": msg,
    }

    return res_data
