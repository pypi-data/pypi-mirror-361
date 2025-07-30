# -*- encoding: utf-8 -*-
import json
import http
from typing import Any, Optional, Callable

from jsonrpcserver import Success
from simplejrpc._json import _jsonify
from simplejrpc._text import json_dumps


def res_success(
    code: Optional[int] = http.HTTPStatus.OK.value,
    msg: Optional[str] = None,
    data: Optional[Any] = None,
    method: Optional[str] = None,
) -> str:
    """返回模板，成功的响应"""
    return _jsonify(code=code, msg=msg, data=data, method=method)


def res_failure(
    code: int = http.HTTPStatus.BAD_REQUEST.value,
    msg: Any = None,
    data: Any = None,
    method: Optional[str] = None,
) -> str:
    """ """

    return _jsonify(code=code, msg=str(msg), data=data, method=method)


def raise_exception(
    except_type: Callable[[Any], Any],
    msg: str,
    code: Optional[int] = http.HTTPStatus.BAD_REQUEST.value,
    method: Optional[str] = None,
):
    """ """
    raise except_type(res_failure(msg=msg, code=code, method=method))


def decoder_json(data):
    """ """

    return json.loads(json_dumps(data))


def jsonify(
    code: int = http.HTTPStatus.OK.value,
    msg: Optional[str] = None,
    data: Any = None,
    method: Optional[str] = None,
):
    """ """

    res_data = _jsonify(code=code, msg=str(msg), data=data, method=method)
    return Success(decoder_json(res_data))


class Response:
    """ """

    def __init__(self, payload: str):
        """ """
        self.payload = payload

    def raw(self):
        """ """
        return self.payload

    def json(self):
        """ """
        return self.payload

    def to_dict(self):
        """ """
        return (
            json.loads(self.payload) if isinstance(self.payload, str) else self.payload
        )

    def __str__(self):
        """ """
        return str(self.payload)

    def __repr__(self):
        """ """
        return f"<Response payload={self.payload}>"
