from app.modules.dataset.services import DataSetService
from app import db
from app.modules.dataset.models import DataSet
from app.modules.auth.models import User
from flask import current_app
import re


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
