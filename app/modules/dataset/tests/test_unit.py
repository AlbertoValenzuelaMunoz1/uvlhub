import io
import os
import zipfile
from pathlib import Path

import pytest

from app import db
from app.modules.auth.seeders import AuthSeeder
from app.modules.dataset.seeders import DataSetSeeder
from app.modules.hubfile.models import Hubfile


@pytest.fixture(scope="function")
def test_database_poblated(test_app):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    working_dir = Path(__file__).resolve().parents[5]
    os.environ.setdefault("WORKING_DIR", str(working_dir))

    with test_app.test_client() as testing_client:
        with test_app.app_context():
            db.drop_all()
            db.create_all()
            AuthSeeder().run()
            DataSetSeeder().run()
            yield testing_client
            db.session.remove()
            db.drop_all()


def test_download_bulk_files_returns_zip(test_database_poblated):
    files = Hubfile.query.limit(2).all()
    assert len(files) == 2
    file_ids = [file.id for file in files]

    response = test_database_poblated.post("/file/download/bulk", json={"file_ids": file_ids})

    assert response.status_code == 200
    assert response.headers.get("Content-Type", "").startswith("application/zip")

    zip_file = zipfile.ZipFile(io.BytesIO(response.data))
    zip_names = set(zip_file.namelist())

    for file in files:
        expected_path = f"dataset_{file.feature_model.data_set_id}/{file.name}"
        assert expected_path in zip_names


def test_download_bulk_files_requires_files(test_database_poblated):
    response = test_database_poblated.post("/file/download/bulk", json={"file_ids": []})

    assert response.status_code == 400
    assert response.get_json()["error"] == "No files selected"
