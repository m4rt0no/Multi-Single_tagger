import logging
import pytest
from httpx import AsyncClient, ASGITransport

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_healthz(app):
    logger.info("[TEST] Calling GET /healthz")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/healthz")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_tag_single_generic(app, mock_openai_select_one):
    mock_openai_select_one("TST001")

    payload = {"text": "¿Puedo consultar algo?", "client": "test-client"}
    logger.info("[TEST] Calling POST /tag_single with client 'test-client'")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/tag_single", json=payload)
    assert res.status_code == 200
    body = res.json()
    logger.info("[TEST] /tag_single status=%s body_keys=%s", res.status_code, list(body.keys()))
    assert isinstance(body.get("categorias"), list)
    assert "response" in body


@pytest.mark.asyncio
async def test_tag_only_generic(app, mock_openai_select_one):
    mock_openai_select_one("TST002")

    payload = {"text": "Me falló un pedido", "client": "test-client"}
    logger.info("[TEST] Calling POST /tag_only with client 'test-client'")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/tag_only", json=payload)
    assert res.status_code == 200
    body = res.json()
    logger.info("[TEST] /tag_only status=%s num_codes=%s", res.status_code, len(body))
    assert isinstance(body, dict)
    assert set(body.values()) <= {0, 1}
    assert sum(v for v in body.values()) == 1


@pytest.mark.asyncio
async def test_tag_generic_multi_category_path(app, mock_openai_select_many):
    # force multi-category path in /tag
    mock_openai_select_many(["TST001", "TST002"])

    payload = {"text": "Mi caso combina consulta y reclamo", "client": "test-client"}
    logger.info("[TEST] Calling POST /tag (multi-category) with client 'test-client'")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/tag", json=payload)
    assert res.status_code == 200
    body = res.json()
    logger.info("[TEST] /tag status=%s categorias=%s", res.status_code, body.get("categorias"))
    assert isinstance(body.get("categorias"), list) and len(body["categorias"]) >= 1
    assert "response" in body

