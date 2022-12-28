from fastapi.testclient import TestClient
from a_package.main import app

client = TestClient(app)

def test_read_main_root():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json() == {"msg": "Hello World"}
    print("Got the home page")