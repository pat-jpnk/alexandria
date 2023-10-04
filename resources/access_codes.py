import secrets 

blp = Blueprint("AccessCodes", __name__, description="Access code resource")


# https://docs.python.org/3/library/secrets.html

@blp.route("/access_code/<string:code_id>")
class AccessCode(MethodView):
    @jwt.required(fresh=True)
    def get(self, code_id):
        """list single access code"""
        jwt = get_jwt()
        
        if not jwt.get("admin"):
            abort(401, message="admin privilege is required")

    @jwt.required(fresh=True)
    def delete(self, code_id):
        """delete access code"""
        jwt = get_jwt()
        
        if not jwt.get("admin"):
            abort(401, message="admin privilege is required")


@blp.route("/access_codes")
class AccessCodeList(MethodView):
    @jwt.required(fresh=True)
    def get(self):
        """list multiple access codes"""
        jwt = get_jwt()
        
        if not jwt.get("admin"):
            abort(401, message="admin privilege is required")
    
    @jwt.required(fresh=True)
    def post(self):
        """create access code"""
        jwt = get_jwt()
        
        if not jwt.get("admin"):
            abort(401, message="admin privilege is required")

        access_code = 


def deactivate_access_code(link_id):
    pass
    # set active to False
