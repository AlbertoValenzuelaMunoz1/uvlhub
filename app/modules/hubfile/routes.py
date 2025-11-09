import os
import shutil
import tempfile
import uuid
from datetime import datetime, timezone
from zipfile import ZipFile

from flask import (
    after_this_request,
    current_app,
    jsonify,
    make_response,
    request,
    send_file,
    send_from_directory,
)
from flask_login import current_user

from app import db
from app.modules.hubfile import hubfile_bp
from app.modules.hubfile.models import HubfileDownloadRecord, HubfileViewRecord
from app.modules.hubfile.services import HubfileDownloadRecordService, HubfileService


@hubfile_bp.route("/file/download/<int:file_id>", methods=["GET"])
def download_file(file_id):
    file = HubfileService().get_or_404(file_id)
    filename = file.name

    directory_path = f"uploads/user_{file.feature_model.data_set.user_id}/dataset_{file.feature_model.data_set_id}/"
    parent_directory_path = os.path.dirname(current_app.root_path)
    file_path = os.path.join(parent_directory_path, directory_path)

    # Get the cookie from the request or generate a new one if it does not exist
    user_cookie = request.cookies.get("file_download_cookie")
    if not user_cookie:
        user_cookie = str(uuid.uuid4())

    # Check if the download record already exists for this cookie
    existing_record = HubfileDownloadRecord.query.filter_by(
        user_id=current_user.id if current_user.is_authenticated else None, file_id=file_id, download_cookie=user_cookie
    ).first()

    if not existing_record:
        # Record the download in your database
        HubfileDownloadRecordService().create(
            user_id=current_user.id if current_user.is_authenticated else None,
            file_id=file_id,
            download_date=datetime.now(timezone.utc),
            download_cookie=user_cookie,
        )

    # Save the cookie to the user's browser
    resp = make_response(send_from_directory(directory=file_path, path=filename, as_attachment=True))
    resp.set_cookie("file_download_cookie", user_cookie)

    return resp


@hubfile_bp.route("/file/download/bulk", methods=["POST"])
def download_bulk_files():
    data = request.get_json() or {}
    file_ids = data.get("file_ids", [])

    if not isinstance(file_ids, list) or len(file_ids) == 0:
        return jsonify({"error": "No files selected"}), 400

    try:
        file_ids = [int(file_id) for file_id in file_ids]
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid file identifiers"}), 400

    hubfile_service = HubfileService()
    files = [hubfile_service.get_or_404(file_id) for file_id in file_ids]

    parent_directory_path = os.path.dirname(current_app.root_path)

    temp_dir = tempfile.mkdtemp()
    zip_filename = f"uvlhub_cart_{uuid.uuid4().hex}.zip"
    zip_path = os.path.join(temp_dir, zip_filename)

    with ZipFile(zip_path, "w") as zipf:
        for file in files:
            directory_path = (
                f"uploads/user_{file.feature_model.data_set.user_id}/"
                f"dataset_{file.feature_model.data_set_id}/"
            )
            absolute_path = os.path.join(parent_directory_path, directory_path, file.name)
            if not os.path.exists(absolute_path):
                continue
            archive_name = os.path.join(f"dataset_{file.feature_model.data_set_id}", file.name)
            zipf.write(absolute_path, arcname=archive_name)

    user_cookie = request.cookies.get("file_download_cookie")
    if not user_cookie:
        user_cookie = str(uuid.uuid4())

    download_service = HubfileDownloadRecordService()
    for file_id in file_ids:
        existing_record = HubfileDownloadRecord.query.filter_by(
            user_id=current_user.id if current_user.is_authenticated else None,
            file_id=file_id,
            download_cookie=user_cookie,
        ).first()

        if not existing_record:
            download_service.create(
                user_id=current_user.id if current_user.is_authenticated else None,
                file_id=file_id,
                download_date=datetime.now(timezone.utc),
                download_cookie=user_cookie,
            )

    @after_this_request
    def cleanup(response):  # noqa
        shutil.rmtree(temp_dir, ignore_errors=True)
        return response

    response = make_response(
        send_file(
            zip_path,
            mimetype="application/zip",
            as_attachment=True,
            download_name="uvlhub-cart.zip",
        )
    )
    response.set_cookie("file_download_cookie", user_cookie)
    return response


@hubfile_bp.route("/file/view/<int:file_id>", methods=["GET"])
def view_file(file_id):
    file = HubfileService().get_or_404(file_id)
    filename = file.name

    directory_path = f"uploads/user_{file.feature_model.data_set.user_id}/dataset_{file.feature_model.data_set_id}/"
    parent_directory_path = os.path.dirname(current_app.root_path)
    file_path = os.path.join(parent_directory_path, directory_path, filename)

    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                content = f.read()

            user_cookie = request.cookies.get("view_cookie")
            if not user_cookie:
                user_cookie = str(uuid.uuid4())

            # Check if the view record already exists for this cookie
            existing_record = HubfileViewRecord.query.filter_by(
                user_id=current_user.id if current_user.is_authenticated else None,
                file_id=file_id,
                view_cookie=user_cookie,
            ).first()

            if not existing_record:
                # Register file view
                new_view_record = HubfileViewRecord(
                    user_id=current_user.id if current_user.is_authenticated else None,
                    file_id=file_id,
                    view_date=datetime.now(),
                    view_cookie=user_cookie,
                )
                db.session.add(new_view_record)
                db.session.commit()

            # Prepare response
            response = jsonify({"success": True, "content": content})
            if not request.cookies.get("view_cookie"):
                response = make_response(response)
                response.set_cookie("view_cookie", user_cookie, max_age=60 * 60 * 24 * 365 * 2)

            return response
        else:
            return jsonify({"success": False, "error": "File not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
