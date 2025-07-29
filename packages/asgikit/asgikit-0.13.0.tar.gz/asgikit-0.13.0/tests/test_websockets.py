from asgikit.requests import Request
from tests.utils.asgi import AsgiReceiveInspector, WebSocketSendInspector


async def test_websocket():
    scope = {
        "type": "websocket",
        "subprotocols": ["stomp"],
        "headers": [],
    }

    receive = AsgiReceiveInspector()
    send = WebSocketSendInspector()

    request = Request(scope, receive, send)

    receive.send(
        {
            "type": "websocket.connect",
        }
    )

    await request.websocket.accept(subprotocol="stomp")
    assert send.subprotocol == "stomp"


async def test_non_websocket_request():
    scope = {"type": "http", "headers": []}

    async def asgi_receive():
        return {
            "type": "websocket.connect",
        }

    async def asgi_send(_message):
        pass

    request = Request(scope, asgi_receive, asgi_send)
    assert request.websocket is None
