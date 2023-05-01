from flask_restx import fields,Namespace
from werkzeug.datastructures import FileStorage

dish_namespace=Namespace("dish",description="operation regarding recipe")
# A dish posting schema for json serialization 
dish_create=dish_namespace.model("dish_",{
    "id":fields.Integer(),
    "name":fields.String(required=True,description="name of the dish"),
    "instructions":fields.String(required=True,description="the instructions to follow while creating this dish"),
    "ingredients":fields.List(fields.String(),required=True,description="list of ingredients")
    ,"date_posted":fields.DateTime(dt_format='rfc822',description="time it was posted")
})

from .user import User_signup
# A dish schema for json
dish_view=dish_namespace.model("dishview",{
    "id":fields.Integer(dump_only=True),
    "name":fields.String(required=True,description="name of the dish"),
    "instructions":fields.String(required=True,description="the instructions to follow while creating this dish"),
    "ingredients":fields.List(fields.String(),required=True,description="list of ingredients")
    ,"date_posted":fields.DateTime(description="time it was posted"),
    "user_likes":fields.List(fields.Nested(User_signup),description="user who likes the dish"),
    "dish_image_url":fields.String(description="image url of the dish")
    ,"user_id":fields.Integer(description="user id ")
})
from marshmallow import fields,Schema

class FileStorageSchema(fields.Field):
    default_error_messages={"invaLid":"not a valid image"}

    def _deserialize(self,value,attr,data,*,partial=False)->FileStorage:
        if value is None:
            return None
        if  not isinstance(value,FileStorage):
            return self.fail("invalid")
        return value




class ImageSchema(Schema):
    image=FileStorageSchema(required=True)