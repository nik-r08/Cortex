import io
import pytest


@pytest.mark.asyncio
async def test_root(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "cortex"


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ("healthy", "degraded")


@pytest.mark.asyncio
async def test_upload_document(client):
    # create a fake text file
    content = b"This is a sample invoice for testing purposes."
    resp = await client.post(
        "/api/v1/documents/",
        files={"file": ("test_invoice.txt", io.BytesIO(content), "text/plain")},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["filename"].endswith(".txt")
    assert data["status"] == "uploaded"
    return data["id"]


@pytest.mark.asyncio
async def test_upload_rejects_bad_type(client):
    content = b"not a real file"
    resp = await client.post(
        "/api/v1/documents/",
        files={"file": ("test.exe", io.BytesIO(content), "application/x-msdownload")},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_list_documents(client):
    resp = await client.get("/api/v1/documents/")
    assert resp.status_code == 200
    data = resp.json()
    assert "documents" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_get_nonexistent_document(client):
    resp = await client.get("/api/v1/documents/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_stats(client):
    resp = await client.get("/api/v1/stats/")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_documents" in data

# search tests: empty query, special chars, no results
# edge case: query with unicode chars, SQL injection attempts
