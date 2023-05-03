from flask_restx import abort,Resource
from werkzeug.security import check_password_hash,generate_password_hash
from flask_jwt_extended import create_access_token,create_refresh_token,get_jwt_identity,get_jwt,jwt_required
from ..models import User,BlockliskModel
from ..schema import user_namespace,User_login,User_signup

@user_namespace.route("/register")
class UserSignin(Resource):
    # endpoint for creating users
    @user_namespace.expect(User_signup)
    def post(self):
        data=user_namespace.payload
        if User.query.filter(User.email==data.get("email")).first():
            abort(400,message="user with this email already exists")
        else:
            first_name=data.get("first_name")
            last_name=data.get("last_name")
            email=data.get("email")
            password=generate_password_hash(data.get("password"))
            new_user=User(first_name=first_name,last_name=last_name,email=email,password=password)
            new_user.save()
            return {"message":"user created successfully"}
@user_namespace.route("/login")
class UserLogin(Resource):
    #endpoint for logging in users
    @user_namespace.expect(User_login)
    
    def post(self):
        data=user_namespace.payload
        user= User.query.filter(User.email==data.get("email")).first()
        if user and check_password_hash(user.password,data.get("password")):
            access_token=create_access_token(identity=user.id)
            refresh_token=create_refresh_token(identity=user.id)
            return {"id":user.id,"firstname":user.first_name,"last_name":user.last_name,"email":user.email,"access_token":access_token,"refresh_token":refresh_token}
        return {"message":"invalid credentials"}
#endpoint for logging out users      
@user_namespace.route("/logout")   
class Logout(Resource):
    @jwt_required()
    def post(self):
        jti=get_jwt().get("jti")
        j_ti=BlockliskModel(jwt=jti)
        j_ti.save()
        return {"message":"user has been logged out "}
    
@user_namespace.route('/refresh')
class Refresh(Resource):

    @jwt_required(refresh=True)
    def post(self):
        """
            Generate Refresh Token
        """

        id= get_jwt_identity()

        access_token = create_access_token(identity=id)

        return {"access_token": access_token},201