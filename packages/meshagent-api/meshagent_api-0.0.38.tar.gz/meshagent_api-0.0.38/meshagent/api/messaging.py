import json
from abc import abstractmethod, ABC

from typing import Optional, Any, Dict

from opentelemetry.propagate import extract, inject


def split_message_payload(data: bytes):
    header_size = int.from_bytes(data[0:8], "big")
    payload = data[8 + header_size :]
    return payload


def split_message_header(data: bytes):
    header_size = int.from_bytes(data[0:8], "big")
    header_str = data[8 : 8 + header_size].decode("utf-8")
    return header_str


def unpack_message(data: bytes) -> tuple[dict, bytes]:
    header: dict = json.loads(split_message_header(data=data))
    payload = split_message_payload(data=data)

    meshagent_data: dict = header.get("__meshagent__")
    if meshagent_data is not None:
        del header["__meshagent__"]
        otel = meshagent_data.get("otel")

        if otel is not None:
            extract(otel)

    return header, payload


def pack_message(header: dict, data: bytes | None = None) -> bytes:
    otel = {}
    inject(otel)

    extra = {"__meshagent__": {"v": 1, "otel": otel}}

    json_message = json.dumps({**header, **extra}, default=str).encode("utf-8")

    message = bytearray()
    message.extend(len(json_message).to_bytes(8))
    message.extend(json_message)
    if data is not None:
        message.extend(data)
    return message


class Response(ABC):
    def __init__(
        self,
        *,
        usage: Optional[dict[str, float]] = None,
        caller_context: Optional[Dict[str, Any]] = None,
    ):
        self.usage = usage
        self.caller_context = caller_context

    @abstractmethod
    def to_json(self) -> dict:
        pass

    @abstractmethod
    def pack(self) -> bytes:
        pass


response_types = dict[str, type]()


class LinkResponse(Response):
    def __init__(
        self,
        *,
        url: str,
        name: str,
        usage: Optional[dict[str, float]] = None,
        caller_context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(usage=usage, caller_context=caller_context)
        self.name = name
        self.url = url

    def to_json(self):
        return {"type": "link", "name": self.name, "url": self.url, "usage": self.usage}

    @staticmethod
    def unpack(*, header: dict, payload: bytes):
        return LinkResponse(
            name=header["name"], url=header["url"], usage=header.get("usage", None)
        )

    def pack(self):
        return pack_message(header=self.to_json())

    def __str__(self):
        return f"LinkResponse name={self.name}, type={self.url} usage={self.usage}"


response_types["link"] = LinkResponse


class FileResponse(Response):
    def __init__(
        self,
        *,
        data: bytes,
        name: str,
        mime_type: str,
        usage: Optional[dict[str, float]] = None,
        caller_context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(usage=usage, caller_context=caller_context)
        self.data = data
        self.name = name
        self.mime_type = mime_type

    def to_json(self):
        return {
            "type": "file",
            "name": self.name,
            "mime_type": self.mime_type,
            "usage": self.usage,
        }

    @staticmethod
    def unpack(*, header: dict, payload: bytes):
        return FileResponse(
            data=payload,
            name=header["name"],
            mime_type=header["mime_type"],
            usage=header.get("usage", None),
        )

    def pack(self):
        return pack_message(header=self.to_json(), data=self.data)

    def __str__(self):
        return f"FileResponse name={self.name}, type={self.mime_type}, length={len(self.data)} usage={self.usage}"


response_types["file"] = FileResponse


class TextResponse(Response):
    def __init__(
        self,
        *,
        text: str,
        usage: Optional[dict[str, float]] = None,
        caller_context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(usage=usage, caller_context=caller_context)
        self.text = text

    @staticmethod
    def unpack(*, header: dict, payload: bytes):
        return TextResponse(text=header["text"], usage=header.get("usage", None))

    def to_json(self):
        return {"type": "text", "text": self.text, "usage": self.usage}

    def pack(self):
        return pack_message(header=self.to_json())

    def __str__(self):
        return f"TextResponse text={self.text} usage={self.usage}"


response_types["text"] = TextResponse


class EmptyResponse(Response):
    def __init__(
        self,
        *,
        usage: Optional[dict[str, float]] = None,
        caller_context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(usage=usage, caller_context=caller_context)

    def to_json(self):
        return {"type": "empty", "usage": self.usage}

    @staticmethod
    def unpack(*, header: dict, payload: bytes):
        return EmptyResponse(usage=header.get("usage", None))

    def pack(self):
        return pack_message(header=self.to_json())

    def __str__(self):
        return f"EmptyResponse usage={self.usage}"


response_types["empty"] = EmptyResponse


class ErrorResponse(Response):
    def __init__(
        self,
        *,
        text: str,
        usage: Optional[dict[str, float]] = None,
        caller_context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(usage=usage, caller_context=caller_context)
        self.text = text

    def to_json(self):
        return {
            "type": "error",
            "text": self.text,
            "usage": self.usage,
        }

    @staticmethod
    def unpack(*, header: dict, payload: bytes):
        return ErrorResponse(text=header["text"], usage=header.get("usage", None))

    def pack(self):
        return pack_message(header=self.to_json())

    def __str__(self):
        return f"ErrorResponse: text={self.text} usage={self.usage}"


response_types["error"] = ErrorResponse


class RawOutputs(Response):
    def __init__(
        self,
        *,
        outputs: list[dict],
        usage: Optional[dict[str, float]] = None,
        caller_context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(usage=usage, caller_context=caller_context)
        self.outputs = outputs

    def to_json(self):
        return {"type": "raw", "outputs": self.outputs, "usage": self.usage}

    @staticmethod
    def unpack(*, header: dict, payload: bytes):
        return RawOutputs(json=header["outputs"], usage=header.get("usage", None))

    def pack(self):
        return pack_message(header=self.to_json())

    def __str__(self):
        return f"RawOutputs: outputs={json.dumps(self.outputs)} usage={self.usage}"


response_types["raw"] = RawOutputs


class JsonResponse(Response):
    def __init__(
        self,
        *,
        json: dict,
        usage: Optional[dict[str, float]] = None,
        caller_context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(usage=usage, caller_context=caller_context)
        self.json = json

    def __getitem__(self, name: str):
        return self.json[name]

    def to_json(self):
        return {"type": "json", "json": self.json, "usage": self.usage}

    @staticmethod
    def unpack(*, header: dict, payload: bytes):
        return JsonResponse(json=header["json"], usage=header.get("usage", None))

    def pack(self):
        return pack_message(header=self.to_json())

    def __str__(self):
        return f"JsonResponse: json={json.dumps(self.json)} usage={self.usage}"


response_types["json"] = JsonResponse


def unpack_response(data: bytes) -> Response:
    header, payload = unpack_message(data)

    T = response_types[header["type"]]
    return T.unpack(header=header, payload=payload)


def ensure_response(response) -> Response:
    if isinstance(response, Response):
        return response
    elif isinstance(response, dict):
        return JsonResponse(json=response)
    elif isinstance(response, str):
        return TextResponse(text=response)
    elif response is None:
        return EmptyResponse()
    else:
        raise Exception(f"Invalid return type from request handler {type(response)}")
