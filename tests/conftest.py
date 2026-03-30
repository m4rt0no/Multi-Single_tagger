import os
import sys
import json
import pytest

# Ensure project root is importable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


@pytest.fixture(scope="session")
def app():
    os.environ.setdefault("OPENAI_API_KEY", "test-key")
    from main import app as fastapi_app
    return fastapi_app


@pytest.fixture(scope="session")
def test_client_codes():
    with open('clients/test-client/lista_test-client.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return list(data.keys())


def _build_json_all_zero_except(codes, positive_codes):
    positive = set(positive_codes)
    return json.dumps({code: (1 if code in positive else 0) for code in codes})


@pytest.fixture
def mock_openai_select_one(monkeypatch, test_client_codes):
    import func

    def _factory(selected_code: str):
        async def fake_create(*args, **kwargs):
            class _Msg:
                def __init__(self, content):
                    self.content = content

            class _Choice:
                def __init__(self, content):
                    self.message = _Msg(content)
                    self.logprobs = None

            class _Completion:
                def __init__(self, content):
                    self.choices = [_Choice(content)]

            content = _build_json_all_zero_except(test_client_codes, [selected_code])
            return _Completion(content)

        monkeypatch.setattr(func.client.chat.completions, "create", fake_create)
        return fake_create

    return _factory


@pytest.fixture
def mock_openai_select_many(monkeypatch, test_client_codes):
    import func

    def _factory(selected_codes):
        async def fake_create(*args, **kwargs):
            class _Msg:
                def __init__(self, content):
                    self.content = content

            class _Choice:
                def __init__(self, content):
                    self.message = _Msg(content)
                    self.logprobs = None

            class _Completion:
                def __init__(self, content):
                    self.choices = [_Choice(content)]

            content = _build_json_all_zero_except(test_client_codes, selected_codes)
            return _Completion(content)

        monkeypatch.setattr(func.client.chat.completions, "create", fake_create)
        return fake_create

    return _factory


