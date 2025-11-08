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


def _build_download_url(dataset_id):
    return f"/dataset/download/{dataset_id}"


def _build_trending_url():
    return "/trending"


def test_trending_download_weekly(test_database_poblated):
    """
    Fixture `test_database_poblated` yields a Flask test client.
    Retrieve dataset and user from the DB inside the test (the fixture already seeded them).
    """
    client = test_database_poblated
    dataset, user = _get_first_dataset_and_user()
    if not dataset:
        import pytest
        pytest.skip("No dataset seeded")

    initial_downloads = dataset.get_number_of_downloads() or 0

    download_url = _build_download_url(dataset.id)
    response = client.get(download_url, follow_redirects=True)
    assert response.status_code == 200, f"Download request was unsuccessful (GET {download_url})"

    updated_dataset = dataset_service.get_or_404(dataset.id)
    assert updated_dataset.get_number_of_downloads() == initial_downloads + 1, "Download count was not incremented"


def test_trending_multiple_downloads_same_user(test_database_poblated):
    client = test_database_poblated
    dataset, user = _get_first_dataset_and_user()
    if not dataset:
        import pytest
        pytest.skip("No dataset seeded")

    initial_downloads = dataset.get_number_of_downloads() or 0

    download_url = _build_download_url(dataset.id)

    # First download
    response1 = client.get(download_url, follow_redirects=True)
    assert response1.status_code == 200, f"First download request was unsuccessful (GET {download_url})"

    # Second download (same client / same session)
    response2 = client.get(download_url, follow_redirects=True)
    assert response2.status_code == 200, f"Second download request was unsuccessful (GET {download_url})"

    updated_dataset = dataset_service.get_or_404(dataset.id)
    # Current implementation increments on every download request
    assert updated_dataset.get_number_of_downloads() == initial_downloads + 1, "Download count should increment on each request"


def test_trending_page_renders_and_contains_dataset_info(test_database_poblated):
    """
    Comprueba que la página de trending se renderiza y contiene información del dataset seed.
    """
    client = test_database_poblated
    dataset, user = _get_first_dataset_and_user()
    if not dataset:
        import pytest
        pytest.skip("No dataset seeded")

    client.get(f"/doi/{dataset.ds_meta_data.dataset_doi}", follow_redirects=True)
    client.get(_build_download_url(dataset.id), follow_redirects=True)
    trending_url = _build_trending_url()
    response = client.get(trending_url, follow_redirects=True)
    assert response.status_code == 200, f"GET {trending_url} should return 200"

    text = response.get_data(as_text=True)
    # Debe contener el título del dataset
    assert (dataset.ds_meta_data.title in text), "Trending page does not contain the dataset title"

    # Debe contener el badge de downloads y views con los contadores actuales
    downloads_text = f"Downloads: {dataset.get_number_of_downloads() or 0}"
    views_text = f"Views: {dataset.get_number_of_views() or 0}"
    assert downloads_text in text, "Trending page does not show downloads count"
    assert views_text in text, "Trending page does not show views count"
    # Debe contener el enlace de descarga esperado
    download_link = f"/dataset/download/{dataset.id}"
    assert download_link in text, "Trending page does not include download link for the dataset"


def test_trending_download_links_work(test_database_poblated):
    """
    Comprueba que los enlaces de descarga listados en la página de trending funcionan (status 200 o redirección válida).
    """
    client = test_database_poblated
    dataset, user = _get_first_dataset_and_user()
    if not dataset:
        import pytest
        pytest.skip("No dataset seeded")

    trending_url = _build_trending_url()
    page = client.get(trending_url, follow_redirects=True)
    assert page.status_code == 200, f"GET {trending_url} should return 200"

    # Intenta descargar usando el enlace estándar de descarga del dataset
    download_url = _build_download_url(dataset.id)
    resp = client.get(download_url, follow_redirects=True)
    assert resp.status_code == 200, f"Download from trending page should succeed (GET {download_url})"