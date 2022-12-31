from fastapi.testclient import TestClient
from a_package.main import app
import requests
client = TestClient(app)

def test_read_main_root():
    res = client.get("/")
    assert res.status_code == 200
    assert res.json() == {"msg": "Hello World"}
    print("Got the home page")

def test_get_batch(inserted_sample_data):
    # queried_batch = client.get("/batch", params="TKJ-23244")
    data = requests.get(
        "http://127.0.0.1:8000/batch/TKJ-23244",
    )
    print(data.json())

def test_allocate_batch():
    res = client.post("/allocate")
    assert res.status_code == 201