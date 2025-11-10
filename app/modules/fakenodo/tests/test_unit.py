def test_status_list_deposition(test_client):
    response=test_client.get("/fakenodo")
    assert response.status_code==200
def test_delete_deposition(test_client):
    response=test_client.delete("/fakenodo/1")
    assert response.status_code==201
def upload_file(test_client):
    response=test_client.post("/fakenodo/1/files")
    assert response.status_code==201
    assert "doi" in response.get_json()
def publish_deposition(test_client):
    response=test_client.post("/fakenodo/1/files/actions/publish")
    assert response.status_code==202
    assert "doi" in response.get_json()
def get_deposition(test_client):
    response=test_client.get("/fakenodo/1")
    assert response.status_code==200
    assert "doi" in response.get_json()