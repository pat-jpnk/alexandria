from flask.views import MethodView
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                get_jwt, get_jwt_identity, jwt_required)
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

import link_id as lid
from db import db
from models import UserModel
from redis_client import redis_client
from schemas import (PlainUserSchema, UserLoginSchema, UserRegisterSchema,
                     UserSearchQueryArgs, UserUpdateSchema)

#from resources.access_code import deactivate_access_code

blp = Blueprint("Users", __name__, description="User resource")           


@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserLoginSchema)
    @blp.alt_response(401, description="error, invalid login credentials")
    def post(self, user_data):
        """login user"""
        user = UserModel.query.filter(UserModel.user_name == user_data["user_name"]).first()
        
        #if not verified_email:
        #    abort(401, message="denied, user email not verified")

        if user and pbkdf2_sha256.verify(user_data["user_password"], user.user_password):
            #verified_email = user.verified_email    

            #if not verified_email:
            #    abort(401, message="denied, user email not verified")
            
            access_token = create_access_token(identity=user.id, fresh=True)                        
            refresh_token = create_refresh_token(identity=user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}
    
        abort(401, message="invalid login credentials")    


@blp.route("/refresh")
class LoginRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        """refresh JWT"""
        current_user = get_jwt_identity()                                       # returns "sub" claim
        new_token = create_access_token(identity=current_user, fresh=False)
        jti = get_jwt().get("jti")
        try:
            redis_client.sadd("blocked_jwt", jti)       # TODO: decide if use SET name constant
        except redis.exceptions.RedisError as e:
             # TODO: log error e
             # TODO: determine how to handle
            pass

        return {"access_token": new_token}

@blp.route("/logout") 
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        """logout user"""
        jti = get_jwt()["jti"]
        try:
            redis_client.sadd("blocked_jwt", jti)
        except redis.exceptions.RedisError as e:
             # TODO: log error e
             # TODO: determine how to 
            pass

        return {"message:": "successfully logged out"}


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserRegisterSchema)
    @blp.response(201, PlainUserSchema, description="created - user created")
    @blp.alt_response(409, description="error, database constraint violation occured")
    def post(self, user_data):
        """register user"""

        #access_code = user_data["access_code"]
        '''
        access_code = AccessCodeModel.query.filter_by(access_code == user_data["access_code"]).first()
        if not access_code:
            abort(401, message="invalid access code")
        
        access_code.active = False
        '''

        if UserModel.query.filter(UserModel.user_name == user_data["user_name"]).first():
            abort(409, message="duplicate username")

        user_data["link_id"] = lid.get_link_id()
        user_data["is_admin"] = False
        
        user = UserModel (
            user_name = user_data["user_name"],
            user_password = pbkdf2_sha256.hash(user_data["user_password"]),
            email = user_data["email"],
            link_id = user_data["link_id"],
            is_admin = user_data["is_admin"]
        )

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError as e:
            abort(409, message="error, database constraint violation occured")
        except SQLAlchemyError:
            abort(500, message="error occured during user registration")

        '''
        try:
            db.session.add(access_code)
            db.session.commit()
        except IntegrityError:
            abort(409, message="error, database constraint violation occured") 
        except SQLAlchemyError:
            abort(500, message="error occured during access code deactivation")    
        '''

        return {"message": "user registered successfully"}, 201

@blp.route("/user/<string:user_id>")
class User(MethodView):
    @jwt_required()
    @blp.response(200, PlainUserSchema, description="success - user found")
    @blp.alt_response(404, description="user not found")
    def get(self, user_id):
        """list single user"""
        user = UserModel.query.filter_by(link_id = user_id).first()    

        if not user:
            abort(404, message="user not found")
  
        return user

    @jwt_required(fresh=True)
    @blp.response(202, description="accepted - user deleted")
    @blp.alt_response(404, description="user not found")
    def delete(self, user_id):
        """delete user"""
        jwt = get_jwt()
        
        if not jwt.get("admin"):
            abort(401, message="admin privilege is required")

        user = UserModel.query.filter_by(link_id = user_id).first()    

        if user:
            try:
                db.session.delete(user)
                db.session.commit()
            except SQLAlchemyError:
                abort(500, message="error occured during user deletion")
        else:
            abort(404, message="user does not exist")

        return {"message": "user deleted"}, 202

    @jwt_required(fresh=True)
    @blp.arguments(UserUpdateSchema)
    @blp.response(204, PlainUserSchema, description="success, no content - user modified")
    @blp.alt_response(409, description="error, database constraint violation occured")
    @blp.alt_response(404, description="user not found")
    def put(self, user_data, user_id):
        """modify user"""
        # TODO: USERS CAN ONLY MODIFY THEMSELVES, test
        user = UserModel.query.filter_by(link_id = user_id).first()   

        if user:
            user.email = user_data["email"]
            user.user_password = pbkdf2_sha256.hash(user_data["user_password"])
            try:
                db.session.add(user)
                db.session.commit()
            except IntegrityError:
                abort(409, message="error, database constraint violation occured") 
            except SQLAlchemyError:
                abort(500, message="error occured during user insertion")
        else:
            abort(404, message="error occurred, user not found")

        return user

@blp.route("/users")
class UserList(MethodView):
    @jwt_required()
    @blp.arguments(UserSearchQueryArgs, location="query")
    @blp.response(200, PlainUserSchema(many=True), description="success - users found")
    def get(self, search_value):
        """list multiple users"""

        name = search_value.get("name")
        result = UserModel.query

        if name:
            result = result.filter(UserModel.user_name.contains(search_value.get("name")))

        return result


# used in @jwt.additional_claims_loader, user not existing should not occur
# but is handled as False
# https://flask-jwt-extended.readthedocs.io/en/stable/add_custom_data_claims.html

def get_user_admin(user_id):
    user = UserModel.query.filter_by(link_id = user_id).first()    

    if not user:
        return False
    
    return user.is_admin