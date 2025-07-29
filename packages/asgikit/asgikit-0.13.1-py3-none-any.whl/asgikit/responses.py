import itertools
import sys
from http import HTTPStatus
from http.cookies import SimpleCookie
from typing import Literal, TypeAlias

from asgikit._constants import (
    CONTENT_LENGTH,
    CONTENT_TYPE,
    COOKIES,
    DEFAULT_ENCODING,
    ENCODING,
    HEADERS,
    IS_FINISHED,
    IS_STARTED,
    RESPONSE,
    SCOPE_ASGIKIT,
    STATUS,
)
from asgikit.asgi import AsgiReceive, AsgiScope, AsgiSend
from asgikit.cookies import encode_cookies
from asgikit.exceptions import (
    ResponseAlreadyEndedError,
    ResponseAlreadyStartedError,
    ResponseNotStartedError,
)

__all__ = ("Response",)

from asgikit.headers import MutableHeaders

SameSitePolicy: TypeAlias = Literal["strict", "lax", "none"]


class Response:
    """Represents the response associated with a request

    Responses are created with their associated requests and can be written to
    """

    __slots__ = ("_scope", "_receive", "_send")

    def __init__(self, scope: AsgiScope, receive: AsgiReceive, send: AsgiSend):
        scope.setdefault(SCOPE_ASGIKIT, {})
        scope[SCOPE_ASGIKIT].setdefault(RESPONSE, {})
        scope[SCOPE_ASGIKIT][RESPONSE].setdefault(STATUS, {})
        scope[SCOPE_ASGIKIT][RESPONSE].setdefault(HEADERS, MutableHeaders())
        scope[SCOPE_ASGIKIT][RESPONSE].setdefault(COOKIES, SimpleCookie())
        scope[SCOPE_ASGIKIT][RESPONSE].setdefault(ENCODING, DEFAULT_ENCODING)
        scope[SCOPE_ASGIKIT][RESPONSE].setdefault(IS_STARTED, False)
        scope[SCOPE_ASGIKIT][RESPONSE].setdefault(IS_FINISHED, False)

        self._scope = scope
        self._receive = receive
        self._send = send

    @property
    def status(self) -> HTTPStatus | None:
        return self._scope[SCOPE_ASGIKIT][RESPONSE][STATUS]

    @status.setter
    def status(self, status: HTTPStatus):
        self._scope[SCOPE_ASGIKIT][RESPONSE][STATUS] = status

    @property
    def headers(self) -> MutableHeaders:
        return self._scope[SCOPE_ASGIKIT][RESPONSE][HEADERS]

    @property
    def cookies(self) -> SimpleCookie:
        return self._scope[SCOPE_ASGIKIT][RESPONSE][COOKIES]

    @property
    def media_type(self) -> str | None:
        return self._scope[SCOPE_ASGIKIT][RESPONSE].get(CONTENT_TYPE)

    @media_type.setter
    def media_type(self, value: str):
        self._scope[SCOPE_ASGIKIT][RESPONSE][CONTENT_TYPE] = value

    @property
    def content_length(self) -> int | None:
        return self._scope[SCOPE_ASGIKIT][RESPONSE].get(CONTENT_LENGTH)

    @content_length.setter
    def content_length(self, value: str):
        self._scope[SCOPE_ASGIKIT][RESPONSE][CONTENT_LENGTH] = value

    @property
    def encoding(self) -> str:
        return self._scope[SCOPE_ASGIKIT][RESPONSE][ENCODING]

    @encoding.setter
    def encoding(self, value: str):
        self._scope[SCOPE_ASGIKIT][RESPONSE][ENCODING] = value

    @property
    def is_started(self) -> bool:
        """Tells whether the response is started or not"""

        return self._scope[SCOPE_ASGIKIT][RESPONSE][IS_STARTED]

    def __set_started(self):
        self._scope[SCOPE_ASGIKIT][RESPONSE][IS_STARTED] = True

    @property
    def is_finished(self) -> bool:
        """Tells whether the response is started or not"""

        return self._scope[SCOPE_ASGIKIT][RESPONSE][IS_FINISHED]

    def __set_finished(self):
        self._scope[SCOPE_ASGIKIT][RESPONSE][IS_FINISHED] = True

    # pylint: disable=too-many-arguments
    def set_cookie(
        self,
        name: str,
        value: str,
        *,
        expires: int = None,
        domain: str = None,
        path: str = None,
        max_age: int = None,
        secure: bool = False,
        httponly: bool = True,
        samesite: SameSitePolicy = "lax",
        partitioned: bool = False,
    ):
        """Add a cookie to the response"""

        self.cookies[name] = value
        if expires is not None:
            self.cookies[name]["expires"] = expires
        if domain is not None:
            self.cookies[name]["domain"] = domain
        if path is not None:
            self.cookies[name]["path"] = path
        if max_age is not None:
            self.cookies[name]["max-age"] = max_age

        self.cookies[name]["secure"] = secure
        self.cookies[name]["httponly"] = httponly
        self.cookies[name]["samesite"] = samesite

        if partitioned:
            if sys.version_info < (3, 14):
                raise NotImplementedError(
                    "Partitioned cookies are only supported in Python >= 3.14."
                )
            self.cookies[name]["partitioned"] = True

    def delete_cookie(
        self,
        name: str,
        *,
        domain: str = None,
        path: str = None,
        secure: bool = False,
        httponly: bool = True,
        samesite: SameSitePolicy = "lax",
    ):
        self.set_cookie(
            name,
            "",
            expires=0,
            max_age=0,
            domain=domain,
            path=path,
            secure=secure,
            httponly=httponly,
            samesite=samesite,
        )

    def __encode_headers(self) -> list[tuple[bytes, bytes]]:
        if self.media_type is not None:
            if self.media_type.startswith("text/"):
                content_type = f"{self.media_type}; charset={self.encoding}"
            else:
                content_type = self.media_type

            self.headers.set("content-type", content_type)

        if (
            self.content_length is not None
            and not (
                self.status < HTTPStatus.OK
                or self.status in (HTTPStatus.NO_CONTENT, HTTPStatus.NOT_MODIFIED)
            )
            and "content-length" not in self.headers
        ):
            self.headers.set("content-length", str(self.content_length))

        encoded_headers = self.headers.encode()
        encoded_cookies = encode_cookies(self.cookies)

        return list(itertools.chain(encoded_headers, encoded_cookies))

    async def start(self):
        """Start the response

        Must be called before writing to the response
        :raise ResponseAlreadyStartedError: If the response is already started
        :raise ResponseAlreadyFinishedError: If the response is finished
        """
        if self.is_started:
            raise ResponseAlreadyStartedError()

        if self.is_finished:
            raise ResponseAlreadyEndedError()

        self.__set_started()

        status = self.status
        headers = self.__encode_headers()

        await self._send(
            {
                "type": "http.response.start",
                "status": status,
                "headers": headers,
            }
        )

    async def write(self, data: bytes | str, *, more_body=False):
        """Write data to the response

        :raise ResponseNotStartedError: If the response is not started
        """

        if not self.is_started:
            raise ResponseNotStartedError()

        encoded_data = data if isinstance(data, bytes) else data.encode(self.encoding)

        await self._send(
            {
                "type": "http.response.body",
                "body": encoded_data,
                "more_body": more_body,
            }
        )

        if not more_body:
            self.__set_finished()

    async def end(self):
        """Finish the response

        Must be called when no more data will be written to the response
        :raise ResponseNotStartedError: If the response is not started
        :raise ResponseAlreadyEndedError: If the response is already finished
        """
        if not self.is_started:
            raise ResponseNotStartedError()

        if self.is_finished:
            raise ResponseAlreadyEndedError

        await self.write(b"", more_body=False)
