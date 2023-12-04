import secrets 
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_jwt_extended import get_jwt, jwt_required

blp = Blueprint("AccessCodes", __name__, description="Access code resource")

# https://docs.python.org/3/library/secrets.html

@blp.route("/access_code/<string:code_id>")
class AccessCode(MethodView):
    @jwt_required(fresh=True)
    def get(self, code_id):
        """list single access code"""
        jwt = get_jwt()
        
        if not jwt.get("admin"):
            abort(401, message="admin privilege is required")

    @jwt_required(fresh=True)
    def delete(self, code_id):
        """delete access code"""
        jwt = get_jwt()
        
        if not jwt.get("admin"):
            abort(401, message="admin privilege is required")


@blp.route("/access_codes")
class AccessCodeList(MethodView):
    @jwt_required(fresh=True)
    def get(self):
        """list multiple access codes"""
        jwt = get_jwt()
        
        if not jwt.get("admin"):
            abort(401, message="admin privilege is required")
    
    @jwt_required(fresh=True)
    # argument 
    def post(self):
        """create access code"""
        jwt = get_jwt()
        
        if not jwt.get("admin"):
            abort(401, message="admin privilege is required")

        #access_code = 


def deactivate_access_code(access_code_link_id):
    access_code = AccessCodeModel.query.filter_by(link_id == access_code_link_id).first()
    if access_code:
        access_code.active = False
        try:
            db.session.add(access_code)
            db.session.commit()
        except IntegrityError:
            abort(409, message="error, database constraint violation occured") 
        except SQLAlchemyError:
            abort(500, message="error occured during user insertion")    


