import io
import zipfile
from app.modules.hubfile.models import Hubfile
from bs4 import BeautifulSoup
from app.modules.dataset.services import DSMetaDataService,DataSetService
from app.modules.dataset.models import DataSet
from app.modules.auth.models import User
import re



def test_download_bulk_files_returns_zip(test_database_poblated):
    files = Hubfile.query.limit(2).all()
    assert len(files) == 2
    file_ids = [file.id for file in files]

    response = test_database_poblated.post(
        "/file/download/bulk",
        json={"file_ids": file_ids},
    )

    assert response.status_code == 200
    assert response.headers.get("Content-Type", "").startswith(
        "application/zip"
    )

    zip_file = zipfile.ZipFile(io.BytesIO(response.data))
    zip_names = set(zip_file.namelist())

    for file in files:
        expected_path = f"dataset_{file.feature_model.data_set_id}/{file.name}"
        assert expected_path in zip_names


def test_download_bulk_files_requires_files(test_database_poblated):
    response = test_database_poblated.post(
        "/file/download/bulk",
        json={"file_ids": []},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "No files selected"


dataset_service=DataSetService()
def test_create_comment(test_database_poblated):
    test_database_poblated.post(
        "/login", data=dict(email="user1@example.com", password="1234"), follow_redirects=True
    )
    doi="10.1234/dataset1"
    dataset=DSMetaDataService().filter_by_doi(doi).data_set
    test_database_poblated.post(f'/datasets/{dataset.id}/comments',data={'content':'Hola','parent_id':None})
    response=test_database_poblated.get(f"/doi/{doi}/")
    s=BeautifulSoup(response.data.decode('utf-8'),"html.parser")
    comment= list(s.find("div",class_="comments-container").div.p.stripped_strings)
    assert comment[0]=='John:', "The comment creator is incorrect"
    assert comment[1]=='Hola', "The comment content is incorrect"
def test_no_content_comment(test_database_poblated):
    test_database_poblated.post(
        "/login", data=dict(email="user1@example.com", password="1234"), follow_redirects=True
    )
    doi="10.1234/dataset1"
    dataset=DSMetaDataService().filter_by_doi(doi).data_set
    response=test_database_poblated.post(f'/datasets/{dataset.id}/comments',data={'content':'','parent_id':None})
    assert response.status_code==400
def test_create_comment_no_login(test_database_poblated):
    doi="10.1234/dataset1"
    dataset=DSMetaDataService().filter_by_doi(doi).data_set
    response=test_database_poblated.post(f'/datasets/{dataset.id}/comments',data={'content':'Hola','parent_id':None})
    assert response.status_code==302, "The user should get redirected if not logged in"
    redirect_url = response.headers.get('Location').split('?')[0]
    assert redirect_url == '/login', "The user should get redirected to log in page"
def test_create_parent_comment(test_database_poblated):
    test_database_poblated.post(
        "/login", data=dict(email="user1@example.com", password="1234"), follow_redirects=True
    )
    doi="10.1234/dataset1"
    dataset=DSMetaDataService().filter_by_doi(doi).data_set
    test_database_poblated.post(f'/datasets/{dataset.id}/comments',data={'content':'Hola','parent_id':None})
    response=test_database_poblated.get(f"/doi/{doi}/")
    s=BeautifulSoup(response.data.decode('utf-8'),"html.parser")
    id=int(s.find("div",class_="comments-container").div["id"].split("-")[1])
    test_database_poblated.post(f'/datasets/{dataset.id}/comments',data={'content':'Adios','parent_id':id})
    response=test_database_poblated.get(f"/doi/{doi}/")
    s=BeautifulSoup(response.data.decode('utf-8'),"html.parser")
    comment= s.find("div",id=re.compile(r'children-\d+'))
    assert comment!=None, "The comment is not created as a response"
    comment=list(comment.div.p.stripped_strings)
    assert comment[0]=='John:', "The comment creator is incorrect"
    assert comment[1]=='Adios', "The comment content is incorrect"

dataset_service = DataSetService()


def _get_first_dataset_and_user():
    dataset = DataSet.query.first()
    user = User.query.first()
    return dataset, user


def _build_download_url(test_client, dataset_id):
    """
    Find a rule that looks like a dataset download endpoint and replace the variable
    part with the actual id. Fall back to the common pattern if none found.
    """
    app = test_client.application
    rules = list(app.url_map.iter_rules())

    # Prefer download routes that belong to the dataset blueprint
    dataset_rules = [rule for rule in rules if rule.endpoint.startswith("dataset.") and "download" in rule.rule]
    for rule in dataset_rules or rules:
        if "download" in rule.rule and "<" in rule.rule:
            url = re.sub(r"<[^>]+>", str(dataset_id), rule.rule)
            return url

    # Fallback to the actual dataset download pattern
    return f"/dataset/download/{dataset_id}"


def test_downloadcounter_successful(test_database_poblated):
    """
    Fixture `test_database_poblated` yields a Flask test client.
    Retrieve dataset and user from the DB inside the test (the fixture already seeded them).
    """
    client = test_database_poblated
    dataset, user = _get_first_dataset_and_user()
    if not dataset:
        import pytest
        pytest.skip("No dataset seeded")

    initial_downloads = dataset.download_count or 0

    download_url = _build_download_url(client, dataset.id)
    response = client.get(download_url, follow_redirects=True)
    assert response.status_code == 200, f"Download request was unsuccessful (GET {download_url})"

    updated_dataset = dataset_service.get_or_404(dataset.id)
    assert updated_dataset.download_count == initial_downloads + 1, "Download count was not incremented"


def test_downloadcounter_multiple_downloads_same_user(test_database_poblated):
    client = test_database_poblated
    dataset, user = _get_first_dataset_and_user()
    if not dataset:
        import pytest
        pytest.skip("No dataset seeded")

    initial_downloads = dataset.download_count or 0

    download_url = _build_download_url(client, dataset.id)

    # First download
    response1 = client.get(download_url, follow_redirects=True)
    assert response1.status_code == 200, f"First download request was unsuccessful (GET {download_url})"

    # Second download (same client / same session)
    response2 = client.get(download_url, follow_redirects=True)
    assert response2.status_code == 200, f"Second download request was unsuccessful (GET {download_url})"

    updated_dataset = dataset_service.get_or_404(dataset.id)
    # Current implementation increments on every download request
    assert updated_dataset.download_count == initial_downloads + 2, "Download count should increment on each request"


def test_download_nonexistent_dataset_returns_404(test_database_poblated):
    client = test_database_poblated

    # Use a large id that should not exist in the seeded DB
    response = client.get("/dataset/999999/download", follow_redirects=True)
    assert response.status_code in (404, 410), "Non-existent dataset download should return 404 or similar"
