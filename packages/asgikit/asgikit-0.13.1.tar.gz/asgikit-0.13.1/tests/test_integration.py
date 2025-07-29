from httpx import ASGITransport, AsyncClient

from asgikit.requests import Request


async def test_request_response():
    async def app(scope, receive, send):
        if scope["type"] != "http":
            return

        request = Request(scope, receive, send)
        await request.respond_text("Ok")

    async with AsyncClient(transport=ASGITransport(app)) as client:
        response = await client.get("http://localhost:8000/")
        assert response.text == "Ok"
