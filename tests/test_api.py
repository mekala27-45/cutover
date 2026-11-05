from fastapi.testclient import TestClient
import app as api
from packages.api.store import StorageUnavailable,BudgetExceeded
client=TestClient(api.app)
def test_health_is_explicit():
    r=client.get("/health")
    assert r.status_code==200 and r.json()["model_ready"] is False
def test_validation_does_not_echo_narrative():
    r=client.post("/v1/triage",json={"narrative":"SECRET"})
    assert r.status_code==422 and "SECRET" not in r.text
def test_no_labels_in_request():
    r=client.post("/v1/triage",json={"narrative":"A sufficiently long test narrative.","label":"ENGINE"})
    assert r.status_code==422
def test_persistence_failure_never_returns_success(monkeypatch):
    def fail(*args):raise StorageUnavailable()
    monkeypatch.setattr(api,"triage",fail)
    assert client.post("/v1/triage",json={"narrative":"The brake pedal became unusually soft."}).status_code==503
def test_budget_failure_returns_429(monkeypatch):
    def fail(*args):raise BudgetExceeded()
    monkeypatch.setattr(api,"triage",fail)
    assert client.post("/v1/triage",json={"narrative":"The brake pedal became unusually soft."}).status_code==429
def test_no_switch_mutation_endpoint():
    assert client.post("/v1/release",json={"killed":False}).status_code==405
def test_body_limit():
    assert client.post("/v1/triage",content="a"*21000).status_code==413
