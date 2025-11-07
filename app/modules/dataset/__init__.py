from flask_restful import Api

from app.modules.dataset.api import init_blueprint_api
from core.blueprints.base_blueprint import BaseBlueprint

dataset_bp = BaseBlueprint("dataset", __name__, template_folder="templates", static_folder="assets", static_url_path="/dataset/assets")


api = Api(dataset_bp)
init_blueprint_api(api)
