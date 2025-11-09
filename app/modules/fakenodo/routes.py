from flask import render_template

from app.modules.fakenodo import fakenodo_bp
from app.modules.zenodo.services import ZenodoService
from flask import Response
import uuid
from flask import jsonify




@fakenodo_bp.route("/fakenodo", methods=["POST"])
def create_deposition():
    unique_id = uuid.uuid4().int  
    return jsonify({"doi": f"10.1234/{unique_id}","id":1,"conceptrecid":1}), 201


@fakenodo_bp.route("/fakenodo/<int:id>", methods=["DELETE"])
def delete_deposition(id):
    unique_id = uuid.uuid4().int  
    return jsonify({"doi": f"10.1234/{unique_id}"}), 201


@fakenodo_bp.route("/fakenodo/<int:id>/files", methods=["POST"])
def upload_file(id):
    unique_id = uuid.uuid4().int  
    return jsonify({"doi": f"10.1234/{unique_id}","id":1,"conceptrecid":1}), 201
                

@fakenodo_bp.route("/fakenodo/<int:id>/actions/publish", methods=["POST"])
def publish_deposition(id):
    unique_id = uuid.uuid4().int  
    return jsonify({"doi": f"10.1234/{unique_id}","id":1,"conceptrecid":1}), 201


@fakenodo_bp.route("/fakenodo/<int:id>", methods=["GET"])
def get_deposition(id):
    unique_id = uuid.uuid4().int
    return jsonify({"doi": f"10.1234/{unique_id}","id":1,"conceptrecid":1}), 200


@fakenodo_bp.route("/fakenodo", methods=["GET"])
def list_depositions():
    return jsonify([]), 200  


