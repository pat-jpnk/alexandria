from os import getenv

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_smorest import Api

from blocklist import BLOCKED_JWT
from db import db
from resources.book import blp as BookBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint
from resources.user import get_user_admin


def create_app(development_db = None):

    app = Flask(__name__)

    load_dotenv()

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Alexandria API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/documentation"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/openapi"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@3.25.x/"
    app.config["SQLALCHEMY_DATABASE_URI"] = development_db or getenv("DATABASE")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["JWT_SECRET_KEY"] = getenv("JWT_SECRET_KEY")                        # used to sign JWT, confirms generation by this app, is not encryption, against tampering
                                                                                   # secrets.SystemRandom().getrandbits(128) 


    app.config["FILE_FORMATS"] = ["application/pdf", "application/epub+zip"]
    app.config["MAX_FILE_SIZE"] = 300000000                                         # 300 MB in bytes

    app.config["AWS_S3_BUCKET_URL"] = "https://s3-eu-central-1.amazonaws.com/alexandria-api"


    db.init_app(app)
    api = Api(app)

    jwt = JWTManager(app)

    api.register_blueprint(BookBlueprint)
    api.register_blueprint(UserBlueprint)
    api.register_blueprint(TagBlueprint)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message": "access token has expired", "error": "token_expired"}),
            401
        )
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify({"message": "failed signature verification", "error": "invalid_token"}),
            401
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify({"message": "missing access token", "error": "authorization_required"}),
            401
        )

    @jwt.needs_fresh_token_loader
    def fresh_token_required(jwt_header, jwt_payload):
        return (
            jsonify({"message": "fresh token is required", "error": "fresh_token_required"}),
            401
        )

    @jwt.token_in_blocklist_loader
    def check_token_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKED_JWT

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message:": "access token was revoked", "error": "revoked access token"}),
            401
        )

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        is_admin = get_user_admin(identity)

        return {
            "admin": is_admin
        }

    return app


'''
            
from flask_jwt_extended import get_jwt
            
in method:

jwt = get_jwt()
if not jwt.get("admin"):
    abort(401, message="admin privilege is required")

'''

    #with app.app_context(): # todo: look up if better alternative
    #    db.create_all()



create_app()