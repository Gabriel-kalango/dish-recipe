from flask import Flask,jsonify
from flask_restx import Api
from .config.config import config_dict
from .utils import db
from .user import user_namespace
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_migrate import Migrate
from .models import BlockliskModel
from .dish import dish_namespace
from flask_uploads import configure_uploads
from .libs.image_helper import IMAGE_SET


# creating the flask application
def create_app(config=config_dict["dev"]):
    app=Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    configure_uploads(app,IMAGE_SET)
    migrate=Migrate(app,db)
    socket=SocketIO(app)
    socket.init_app(app)
    
    jwt=JWTManager(app)
    api=Api(app)
    api.add_namespace(user_namespace)
    api.add_namespace(dish_namespace)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return  BlockliskModel.query.filter_by(jwt=jwt_payload["jti"] ).first() is not None

 
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The token has been revoked.", "error": "token_revoked"}
            ),
            401,
        )
        
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "description": "The token is not fresh.",
                    "error": "fresh_token_required",
                }
            ),
            401,
        )
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
        jsonify({"message": "The token has expired.", "error": "token_expired"}),
        401,
    )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed.", "error": "invalid_token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token.",
                    "error": "authorization_required",
                }
            ),
            401,
        )
    return app