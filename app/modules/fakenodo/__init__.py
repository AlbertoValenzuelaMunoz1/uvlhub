from flask_restful import Api

from app.modules.dataset.api import init_blueprint_api
from core.blueprints.base_blueprint import BaseBlueprint

fakenodo_bp = BaseBlueprint(
    "fakenodo",
    __name__,
)


api = Api(fakenodo_bp)
init_blueprint_api(api)
