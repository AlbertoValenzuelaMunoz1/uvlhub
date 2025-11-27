import csv
import json
import logging
import os
import shutil
import tempfile
import uuid
from datetime import datetime, timezone
from zipfile import ZipFile

import requests
from flask import (
    abort,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_login import current_user, login_required
from urllib.parse import urlparse
from werkzeug.utils import secure_filename

from app.modules.dataset import dataset_bp
from app.modules.dataset.forms import DataSetForm
from app.modules.dataset.models import DSDownloadRecord,Comment
from app.modules.dataset.models import DSDownloadRecord
from app import db
from app.modules.dataset.services import (
    AuthorService,
    DataSetService,
    DOIMappingService,
    DSDownloadRecordService,
    DSMetaDataService,
    DSViewRecordService,
    CommentService
)
from app.modules.zenodo.services import ZenodoService
from app.modules.auth.services import AuthenticationService
comment_service=CommentService()
logger = logging.getLogger(__name__)


dataset_service = DataSetService()
author_service = AuthorService()
dsmetadata_service = DSMetaDataService()
zenodo_service = ZenodoService()
doi_mapping_service = DOIMappingService()
ds_view_record_service = DSViewRecordService()

CSV_REQUIRED_COLUMNS = [
    "ATP",
    "Location",
    "Tournament",
    "Date",
    "Series",
    "Court",
    "Surface",
    "Round",
    "Best of",
    "Winner",
    "Loser",
    "WRank",
    "LRank",
    "WPts",
    "LPts",
    "W1",
    "L1",
    "W2",
    "L2",
    "W3",
    "L3",
    "W4",
    "L4",
    "W5",
    "L5",
    "Wsets",
    "Lsets",
    "Comment",
    "B365W",
    "B365L",
    "PSW",
    "PSL",
    "MaxW",
    "MaxL",
    "AvgW",
    "AvgL",
]


SUPPORTED_EXTENSIONS = (".csv", ".uvl")


def validate_uploaded_files(temp_folder, feature_models):
    """Ensure every uploaded file exists and, if CSV, matches the expected columns."""
    for feature_model in feature_models:
        file_name = feature_model.uvl_filename.data

        if not file_name:
            return "Each uploaded file must include a filename."

        if not file_name.lower().endswith(SUPPORTED_EXTENSIONS):
            return f"{file_name} must be one of: {', '.join(SUPPORTED_EXTENSIONS)}"

        file_path = os.path.join(temp_folder, file_name)
        if not os.path.isfile(file_path):
            return f"{file_name} not found in the temporary upload folder."

        if file_name.lower().endswith(".csv"):
            try:
                with open(file_path, "r", newline="", encoding="utf-8-sig") as csv_file:
                    sample = csv_file.read(2048)
                    csv_file.seek(0)
                    try:
                        dialect = csv.Sniffer().sniff(sample)
                    except csv.Error:
                        dialect = csv.excel
                    reader = csv.reader(csv_file, dialect)
                    headers = next(reader, None)
            except Exception as exc:
                logger.exception("Error reading uploaded CSV %s", file_name)
                return f"Could not read {file_name}: {exc}"

            if not headers:
                return f"{file_name} is empty or missing a header row."

            normalized_headers = [header.strip() for header in headers]

            if normalized_headers != CSV_REQUIRED_COLUMNS:
                missing = [col for col in CSV_REQUIRED_COLUMNS if col not in normalized_headers]
                extras = [col for col in normalized_headers if col not in CSV_REQUIRED_COLUMNS]
                details = []
                if missing:
                    details.append(f"missing columns: {', '.join(missing)}")
                if extras:
                    details.append(f"unexpected columns: {', '.join(extras)}")

                detail_msg = "; ".join(details) if details else "columns are out of order"
                return (
                    f"{file_name} must include the columns "
                    f"{', '.join(CSV_REQUIRED_COLUMNS)}; {detail_msg}."
                )

    return None


def ensure_temp_upload_folder() -> str:
    """Create the current user's temp folder if it does not exist."""
    temp_folder = current_user.temp_folder()
    os.makedirs(temp_folder, exist_ok=True)
    return temp_folder


def unique_filename(directory: str, filename: str) -> str:
    """Return a filename that does not collide inside directory."""
    base_name, extension = os.path.splitext(filename)
    candidate = filename
    counter = 1
    while os.path.exists(os.path.join(directory, candidate)):
        candidate = f"{base_name} ({counter}){extension}"
        counter += 1
    return candidate


def validate_csv_file(file_path: str):
    """Validate a single CSV file against the expected header."""
    if not file_path.lower().endswith(".csv"):
        return "Only CSV files are supported."

    try:
        with open(file_path, "r", newline="", encoding="utf-8-sig") as csv_file:
            sample = csv_file.read(2048)
            csv_file.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample)
            except csv.Error:
                dialect = csv.excel
            reader = csv.reader(csv_file, dialect)
            headers = next(reader, None)
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Error reading CSV %s", file_path)
        return f"Could not read CSV: {exc}"

    if not headers:
        return "File is empty or missing a header row."

    normalized_headers = [header.strip() for header in headers]

    if normalized_headers != CSV_REQUIRED_COLUMNS:
        missing = [col for col in CSV_REQUIRED_COLUMNS if col not in normalized_headers]
        extras = [col for col in normalized_headers if col not in CSV_REQUIRED_COLUMNS]
        details = []
        if missing:
            details.append(f"missing columns: {', '.join(missing)}")
        if extras:
            details.append(f"unexpected columns: {', '.join(extras)}")
        detail_msg = "; ".join(details) if details else "columns are out of order"
        return (
            f"Columns must match {', '.join(CSV_REQUIRED_COLUMNS)}; {detail_msg}."
        )
    return None


def extract_supported_files_from_zip(zip_path: str, temp_folder: str):
    """Extract valid CSV/UVL files from a zip into the user's temp folder."""
    saved_files = []
    skipped = []
    with ZipFile(zip_path, "r") as archive:
        for member in archive.namelist():
            if member.endswith("/"):
                continue
            if not member.lower().endswith(SUPPORTED_EXTENSIONS):
                continue

            filename = secure_filename(os.path.basename(member))
            if not filename:
                skipped.append(f"{member} skipped (invalid name)")
                continue

            safe_filename = unique_filename(temp_folder, filename)
            destination = os.path.join(temp_folder, safe_filename)

            try:
                with archive.open(member) as source, open(destination, "wb") as target:
                    shutil.copyfileobj(source, target)
            except Exception as exc:  # pragma: no cover - defensive
                skipped.append(f"{filename} skipped (error while extracting: {exc})")
                continue

            # Only validate CSV headers; UVL files are accepted as-is.
            if filename.lower().endswith(".csv"):
                validation_error = validate_csv_file(destination)
                if validation_error:
                    skipped.append(f"{filename} skipped ({validation_error})")
                    try:
                        os.remove(destination)
                    except OSError:
                        pass
                    continue

            saved_files.append(safe_filename)
    return saved_files, skipped


def resolve_github_zip_url(github_url: str) -> str:
    """Return a direct zip URL given a GitHub repo or zip link."""
    if github_url.lower().endswith(".zip"):
        return github_url

    parsed = urlparse(github_url)
    if "github.com" not in parsed.netloc:
        raise ValueError("The provided link is not a valid GitHub URL or zip file.")

    path_parts = [part for part in parsed.path.split("/") if part]
    if len(path_parts) < 2:
        raise ValueError("GitHub URL must include owner and repository.")

    owner, repo = path_parts[0], path_parts[1]
    branch = "main"
    if len(path_parts) >= 4 and path_parts[2] == "tree":
        branch = path_parts[3]

    return f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"


@dataset_bp.route("/dataset/import/github", methods=["GET"])
@login_required
def import_dataset_from_github_form():
    return render_template("dataset/import_dataset.html", active_tab="github")


@dataset_bp.route("/dataset/import/zip", methods=["GET"])
@login_required
def import_dataset_from_zip_form():
    return render_template("dataset/import_dataset.html", active_tab="zip")


@dataset_bp.route("/dataset/file/import/github", methods=["POST"])
@login_required
def import_dataset_from_github():
    payload = request.get_json(silent=True) or {}
    github_url = (payload.get("github_url") or "").strip()

    if not github_url:
        return jsonify({"message": "GitHub URL is required."}), 400

    try:
        zip_url = resolve_github_zip_url(github_url)
    except ValueError as exc:
        return jsonify({"message": str(exc)}), 400

    try:
        response = requests.get(zip_url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.exception("Error downloading GitHub archive")
        return jsonify({"message": f"Could not download repository: {exc}"}), 400

    temp_folder = ensure_temp_upload_folder()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
        tmp.write(response.content)
        tmp_path = tmp.name

    try:
        saved_files, skipped = extract_supported_files_from_zip(tmp_path, temp_folder)
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass

    if not saved_files:
        message = "No valid CSV files were found in the provided repository."
        if skipped:
            message += " " + " ".join(skipped)
        return jsonify({"message": message, "files": [], "skipped": skipped}), 400

    return (
        jsonify(
            {
                "message": "CSV files imported from GitHub.",
                "files": saved_files,
                "skipped": skipped,
            }
        ),
        200,
    )


@dataset_bp.route("/dataset/file/import/zip", methods=["POST"])
@login_required
def import_dataset_from_zip():
    uploaded_file = request.files.get("file")
    if not uploaded_file or uploaded_file.filename == "":
        return jsonify({"message": "A zip file is required."}), 400

    if not uploaded_file.filename.lower().endswith(".zip"):
        return jsonify({"message": "Only .zip files are supported."}), 400

    temp_folder = ensure_temp_upload_folder()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
        uploaded_file.save(tmp.name)
        tmp_path = tmp.name

    try:
        saved_files, skipped = extract_supported_files_from_zip(tmp_path, temp_folder)
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass

    if not saved_files:
        message = "No valid CSV files were found inside the zip file."
        if skipped:
            message += " " + " ".join(skipped)
        return jsonify({"message": message, "files": [], "skipped": skipped}), 400

    return (
        jsonify(
            {
                "message": "CSV files imported from zip.",
                "files": saved_files,
                "skipped": skipped,
            }
        ),
        200,
    )


@dataset_bp.route("/dataset/upload", methods=["GET", "POST"])
@login_required
def create_dataset():
    form = DataSetForm()
    if request.method == "POST":

        dataset = None

        if not form.validate_on_submit():
            return jsonify({"message": form.errors}), 400

        temp_folder = current_user.temp_folder()
        validation_error = validate_uploaded_files(temp_folder, form.feature_models)
        if validation_error:
            return jsonify({"message": validation_error}), 400

        try:
            logger.info("Creating dataset...")
            dataset = dataset_service.create_from_form(form=form, current_user=current_user)
            logger.info(f"Created dataset: {dataset}")
            dataset_service.move_feature_models(dataset)
        except Exception as exc:
            logger.exception(f"Exception while create dataset data in local {exc}")
            return jsonify({"Exception while create dataset data in local: ": str(exc)}), 400

        # send dataset as deposition to Zenodo
        data = {}
        try:
            zenodo_response_json = zenodo_service.create_new_deposition(dataset)
            response_data = json.dumps(zenodo_response_json)
            data = json.loads(response_data)
        except Exception as exc:
            data = {}
            zenodo_response_json = {}
            logger.exception(f"Exception while create dataset data in Zenodo {exc}")

        if data.get("conceptrecid"):
            deposition_id = data.get("id")

            # update dataset with deposition id in Zenodo
            dataset_service.update_dsmetadata(dataset.ds_meta_data_id, deposition_id=deposition_id)

            try:
                # iterate for each feature model (one feature model = one request to Zenodo)
                for feature_model in dataset.feature_models:
                    zenodo_service.upload_file(dataset, deposition_id, feature_model)

                # publish deposition
                zenodo_service.publish_deposition(deposition_id)

                # update DOI
                deposition_doi = zenodo_service.get_doi(deposition_id)
                dataset_service.update_dsmetadata(dataset.ds_meta_data_id, dataset_doi=deposition_doi)
            except Exception as e:
                msg = f"it has not been possible upload feature models in Zenodo and update the DOI: {e}"
                return jsonify({"message": msg}), 200

        # Delete temp folder
        file_path = current_user.temp_folder()
        if os.path.exists(file_path) and os.path.isdir(file_path):
            shutil.rmtree(file_path)

        msg = "Everything works!"
        return jsonify({"message": msg}), 200

    prefilled_files = []
    temp_folder = current_user.temp_folder()
    if os.path.isdir(temp_folder):
        prefilled_files = [
            file
            for file in os.listdir(temp_folder)
            if os.path.isfile(os.path.join(temp_folder, file)) and file.lower().endswith(".csv")
        ]

    return render_template("dataset/upload_dataset.html", form=form, prefilled_files=prefilled_files)


@dataset_bp.route("/dataset/list", methods=["GET", "POST"])
@login_required
def list_dataset():
    return render_template(
        "dataset/list_datasets.html",
        datasets=dataset_service.get_synchronized(current_user.id),
        local_datasets=dataset_service.get_unsynchronized(current_user.id),
    )


@dataset_bp.route("/dataset/file/upload", methods=["POST"])
@login_required
def upload():
    file = request.files["file"]
    temp_folder = current_user.temp_folder()

    if not file or not file.filename.lower().endswith(SUPPORTED_EXTENSIONS):
        return jsonify({"message": f"No valid file, only {', '.join(SUPPORTED_EXTENSIONS)} allowed"}), 400

    # create temp folder
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    file_path = os.path.join(temp_folder, file.filename)

    if os.path.exists(file_path):
        # Generate unique filename (by recursion)
        base_name, extension = os.path.splitext(file.filename)
        i = 1
        while os.path.exists(os.path.join(temp_folder, f"{base_name} ({i}){extension}")):
            i += 1
        new_filename = f"{base_name} ({i}){extension}"
        file_path = os.path.join(temp_folder, new_filename)
    else:
        new_filename = file.filename

    try:
        file.save(file_path)
    except Exception as e:
        return jsonify({"message": str(e)}), 500

    return (
        jsonify(
            {
                "message": "CSV uploaded and validated successfully",
                "filename": new_filename,
            }
        ),
        200,
    )


@dataset_bp.route("/dataset/file/delete", methods=["POST"])
def delete():
    data = request.get_json()
    filename = data.get("file")
    temp_folder = current_user.temp_folder()
    filepath = os.path.join(temp_folder, filename)

    if os.path.exists(filepath):
        os.remove(filepath)
        return jsonify({"message": "File deleted successfully"})

    return jsonify({"error": "Error: File not found"})


@dataset_bp.route("/dataset/download/<int:dataset_id>", methods=["GET"])
def download_dataset(dataset_id):
    dataset = dataset_service.get_or_404(dataset_id)

    # incrementar contador de descargas
    dataset.download_count = (dataset.download_count or 0) + 1
    db.session.commit()

    file_path = f"uploads/user_{dataset.user_id}/dataset_{dataset.id}/"

    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, f"dataset_{dataset_id}.zip")

    with ZipFile(zip_path, "w") as zipf:
        for subdir, dirs, files in os.walk(file_path):
            for file in files:
                full_path = os.path.join(subdir, file)

                relative_path = os.path.relpath(full_path, file_path)

                zipf.write(
                    full_path,
                    arcname=os.path.join(os.path.basename(zip_path[:-4]), relative_path),
                )

    user_cookie = request.cookies.get("download_cookie")
    if not user_cookie:
        user_cookie = str(uuid.uuid4())  # Generate a new unique identifier if it does not exist
        # Save the cookie to the user's browser
        resp = make_response(
            send_from_directory(
                temp_dir,
                f"dataset_{dataset_id}.zip",
                as_attachment=True,
                mimetype="application/zip",
            )
        )
        resp.set_cookie("download_cookie", user_cookie)
    else:
        resp = send_from_directory(
            temp_dir,
            f"dataset_{dataset_id}.zip",
            as_attachment=True,
            mimetype="application/zip",
        )

    # Check if the download record already exists for this cookie
    existing_record = DSDownloadRecord.query.filter_by(
        user_id=current_user.id if current_user.is_authenticated else None,
        dataset_id=dataset_id,
        download_cookie=user_cookie,
    ).first()

    if not existing_record:
        # Record the download in your database
        DSDownloadRecordService().create(
            user_id=current_user.id if current_user.is_authenticated else None,
            dataset_id=dataset_id,
            download_date=datetime.now(timezone.utc),
            download_cookie=user_cookie,
        )

    return resp

@dataset_bp.route("/dataset/<int:dataset_id>/stats", methods=["GET"])
def dataset_stats(dataset_id):
    dataset = dataset_service.get_or_404(dataset_id)
    views = ds_view_record_service.get_view_count(dataset.id)
    return jsonify(
        {
            "dataset_id": dataset.id,
            "download_count": dataset.download_count or 0,
            "view_count": views,
        }
    ), 200


@dataset_bp.route("/doi/<path:doi>/", methods=["GET"])
def subdomain_index(doi):

    # Check if the DOI is an old DOI
    new_doi = doi_mapping_service.get_new_doi(doi)
    if new_doi:
        # Redirect to the same path with the new DOI
        return redirect(url_for("dataset.subdomain_index", doi=new_doi), code=302)

    # Try to search the dataset by the provided DOI (which should already be the new one)
    ds_meta_data = dsmetadata_service.filter_by_doi(doi)

    if not ds_meta_data:
        abort(404)

    # Get dataset
    dataset = ds_meta_data.data_set

    # Save the cookie to the user's browser
    user_cookie = ds_view_record_service.create_cookie(dataset=dataset)
    resp = make_response(render_template("dataset/view_dataset.html", dataset=dataset))
    resp.set_cookie("view_cookie", user_cookie)

    return resp


@dataset_bp.route("/dataset/unsynchronized/<int:dataset_id>/", methods=["GET"])
@login_required
def get_unsynchronized_dataset(dataset_id):

    # Get dataset
    dataset = dataset_service.get_unsynchronized_dataset(current_user.id, dataset_id)

    if not dataset:
        abort(404)

    return render_template("dataset/view_dataset.html", dataset=dataset)


@dataset_bp.route("/trending", methods=["GET", "POST"])
#@login_required
def trending_datasets():
    most_downloaded = dataset_service.get_trending_datasets_by_downloads()
    most_viewed = dataset_service.get_trending_datasets_by_views()
    return render_template(
        "dataset/trending_datasets.html",
        most_downloaded=most_downloaded,
        most_viewed=most_viewed,
    )
    
@dataset_bp.route("/datasets/<int:dataset_id>/comments", methods=["POST"])
@login_required  
def add_comment(dataset_id):
    content = request.form.get("content")
    if not content or content.strip() == '':
        abort(400, description="El contenido del comentario no puede estar vacío.")
    parent_id = request.form.get("parent_id") or None
    auth_service=AuthenticationService()
    user=auth_service.get_authenticated_user()
    dataset=dataset_service.get_or_404(dataset_id)
    comment_service.create(
        content=content,
        dataset_id=dataset_id,
        parent_id=parent_id,
        user_id=user.id)
    

    return redirect(f'/doi/{dataset.ds_meta_data.dataset_doi}')
