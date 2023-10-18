from flask_restx import Namespace,fields
user_namespace=Namespace("user",description="operations on user")
# user sign up schema for json serialization
User_signup=user_namespace.model("usersignup",{
    "id":fields.Integer(dump_only=True),
    "first_name":fields.String(required=True,description="the first name of the user")
    , "last_name":fields.String(required=True,description="the last name of the user"),
 "email":fields.String(required=True,description="the email of the user"),
 "password":fields.String(required=True,description="the password of the user"),
 "phone_number":fields.String(required=True,description="the phone number of the user")

}) 
# user log in schema for json serialization
User_login=user_namespace.model("userlogin",{
 "email":fields.String(required=True,description="the email of the user"),
 "password":fields.String(required=True,description="the password of the user")
}) 

User_signup_return=user_namespace.model("usersignup_return",{
    "id":fields.Integer(dump_only=True),
    "first_name":fields.String(required=True,description="the first name of the user")
    , "last_name":fields.String(required=True,description="the last name of the user"),
 "email":fields.String(required=True,description="the email of the user"),
 "phone_number":fields.String(required=True,description="the phone number of the user")

}) 