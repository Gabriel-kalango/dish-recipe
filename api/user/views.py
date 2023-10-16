from flask_restx import abort,Resource
from werkzeug.security import check_password_hash,generate_password_hash
from flask_jwt_extended import create_access_token,create_refresh_token,get_jwt_identity,get_jwt,jwt_required
from ..models import User,BlockliskModel
from ..schema import user_namespace,User_login,User_signup

@user_namespace.route("/register")
class UserSignin(Resource):
    """endpoint for creating user"""
    @user_namespace.expect(User_signup)
    @user_namespace.response(200,"user created successfully")
    @user_namespace.response(400,"user with this email already exists")
    def post(self):
        """
            user registeration
        """
        data=user_namespace.payload
        if User.query.filter(User.email==data.get("email")).first():
            abort(400,message="user with this email already exists",status="error")
        else:
            first_name=data.get("first_name")
            last_name=data.get("last_name")
            email=data.get("email")
            password=generate_password_hash(data.get("password"))
            new_user=User(first_name=first_name,last_name=last_name,email=email,password=password)
            new_user.save()
            return {"status":"success","message":"user created successfully"},200
@user_namespace.route("/login")
class UserLogin(Resource):
    """endpoint for user logging in"""
    @user_namespace.expect(User_login)
    @user_namespace.response(200,"user has been logged in",User_login)
    @user_namespace.response(400,"invalid credentials")
    
    def post(self):
        """
        Generate access token
        """
        data=user_namespace.payload
        user= User.query.filter(User.email==data.get("email")).first()
        if user and check_password_hash(user.password,data.get("password")):
            access_token=create_access_token(identity=user.id)
            refresh_token=create_refresh_token(identity=user.id)
            return {"status":"success","id":user.id,"firstname":user.first_name,"last_name":user.last_name,"email":user.email,"access_token":access_token,"refresh_token":refresh_token},200
        return {"status":"error","message":"invalid credentials"},400
    
#endpoint for logging out users      
@user_namespace.route("/logout")   
class Logout(Resource):
    @jwt_required()
    @user_namespace.doc(security="jwt")
    @user_namespace.response(200,"user has been logged out")
    @user_namespace.response(400,"user not logged in")
    def post(self):
        """
            logout endpoint
        """
        jti=get_jwt().get("jti")
        j_ti=BlockliskModel(jwt=jti)
        j_ti.save()
        return {"status":"success","message":"user has been logged out "},200
    
@user_namespace.route('/refresh')
class Refresh(Resource):
    @user_namespace.doc(security="jwt")
    @user_namespace.response(201,"access token generated")
    @user_namespace.response(400,"user not logged in")
    @jwt_required(refresh=True)
    def post(self):
        """
            Generate Refresh Token
        """

        id= get_jwt_identity()

        access_token = create_access_token(identity=id)

        return {"status":"success","access_token": access_token},201