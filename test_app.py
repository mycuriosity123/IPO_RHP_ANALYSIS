import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status
from src.app import app

@pytest.mark.asyncio
async def test_upload_invalid_file_type():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        files = {
            "file": ("test.txt", b"Dummy content", "text/plain")  # not a PDF
        }
        response = await ac.post("/upload", files=files)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["error"] == "File must be a PDF."