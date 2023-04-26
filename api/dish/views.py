from flask_restx import Resource,abort
from ..models import User,Dish
from ..schema import dish_create,dish_namespace,dish_view,ImageSchema
from flask_jwt_extended import jwt_required,get_jwt_identity
from flask_socketio import emit
from flask import request,send_file
from ..libs import image_helper
from flask_uploads import UploadNotAllowed
import os
from mimetypes import guess_type
import traceback

@dish_namespace.route("")
class Recipes(Resource):
    #get all dishes
    @dish_namespace.marshal_with(dish_view,as_list=True)
    def get(self):
        dishes=Dish.query.all()
    
    
        return dishes
    #posting your dish
    @dish_namespace.expect(dish_create)
    @jwt_required()
    def post(self):
        user_id=get_jwt_identity()
        data=dish_namespace.payload
        name=data.get("name")
        instructions=data.get("instructions")   
        ingredients=data.get("ingredients")
        new_dish=Dish(name=name,instructions=instructions,ingredients=ingredients,user_id=user_id)
        new_dish.save()
        return {"message":"dish uploaded successfully"},201

@dish_namespace.route("/<int:id>")
class GetUpdateDeleteDish(Resource):
    #get a particular dish
    @dish_namespace.marshal_with(dish_view)
    def get(self,id):
        dish=Dish.query.get_or_404(id)
        dish.ingredients=dish.get_ingredients()
        return dish,200
    #creating an endpoint to update dishes
    @jwt_required()
    @dish_namespace.expect(dish_create)
    def put(self,id):
        user_id=get_jwt_identity()
        if Dish.query.filter(Dish.user_id==user_id).first():
            data=dish_namespace.payload
            dish=Dish.query.get(id)
            if dish:
                dish.name=data.get("name")
                dish.instructions=data.get("instructions")
                dish.ingredients=data.get("ingredients")
                dish.set_ingredients(dish.ingredients)
                dish.update()
                return {"message":"dish has been updated"}
            abort(400,message="this post doesnt exist")
        abort(403,message="you are not the owner of this account")
    #creating an endpoint to delete dish
    @jwt_required()
    def delete(self,id):
        user_id=get_jwt_identity()
        if Dish.query.filter(Dish.user_id==user_id).first():
            dish=Dish.query.get_or_404(id)
            dish.delete()
            return {"message":"dish deleted successfully"},200
        abort(403,message="you are not the owner of this account")
    # creating an endpoint to handle the liking and disliking a dish
@dish_namespace.route("/likes/<int:id>")
class postlikes(Resource):
        @jwt_required()
        def post(self,id):
            user_id=get_jwt_identity()
            user=User.query.get(user_id)
            dish=Dish.query.get_or_404(id)
            if user is None:
                if user not in dish.user_likes:
                    dish.user_likes.append(user)
                    dish.update()
                    
                else:
                    dish.user_likes.remove(user)
                    dish.update()
                updated_likes=len(dish.user_likes)
                emit('like', {'dish_id': dish.id, 'like_count': updated_likes}, broadcast=True)

                return {"number_of_likes":updated_likes}

            abort(400,message="user doesnt exist")

@dish_namespace.route("/image")
class Imagee(Resource):
    @jwt_required()
    def post(self):
        data=ImageSchema().load(request.files)
        user_id=get_jwt_identity()
        folder=f"user_{user_id}"
        try:
            image_path=image_helper.save_image(data["image"],folder=folder)
            basename=image_helper.get_basename(image_path)
            return {"message":f"{basename} has been uploaded"},201
        except UploadNotAllowed:
            extension=image_helper.get_extension(data["image"])
            return {"message":f"this {extension} is not allowed"},400


@dish_namespace.route("/images/<filename>")
class image(Resource):
    @jwt_required()
    def get(self,filename):
        user_id=get_jwt_identity()
        folder=f"user_{user_id}"
        if not image_helper.is_filename_safe(filename):
            abort(400,message=f"this {filename} is not supported")
        try:
            # get the current working directory
            current_dir = os.getcwd()



            file_path=image_helper.get_path(filename,folder=folder)
            file_path_=os.path.join(current_dir,file_path)
            absolute_path=os.path.abspath(file_path_)
        
            return send_file(absolute_path,mimetype=guess_type(file_path)[0])

   

        except FileNotFoundError:
            abort(404,message=f"file with name {filename} not found ")
    @jwt_required()
    def delete(self,filename):
        user_id=get_jwt_identity()
        folder=f"user_{user_id}"
        if not image_helper.is_filename_safe(filename):
            abort(400,message=f"this {filename} is not supported")
        try:
            # get the current working directory
            current_dir = os.getcwd()



            file_path=image_helper.get_path(filename,folder=folder)
            file_path_=os.path.join(current_dir,file_path)
            absolute_path=os.path.abspath(file_path_)
        
            os.remove(absolute_path)
            return {"message":"image deleted successfully"}

   

        except FileNotFoundError:
            abort(404,message=f"file with name {filename} not found ")
        
        except:
            traceback.print_exc()
            abort(500,message="image deletion failed")




@dish_namespace.route("/avatar")
class Avatarupload(Resource):
    @jwt_required()
    def put(self):
        data=ImageSchema().load(request.files)
        user_id=get_jwt_identity()
        filename=f"user_{user_id}"
        folder="avatars"
        avatar_path=image_helper.find_image_format(filename,folder)
        if avatar_path:
            try:
                os.remove(avatar_path)
            except:
                abort(500,message="avatar deletion failed")
        try:
            ext=image_helper.get_extension(data["image"].filename)
            avatar=filename+ext
            avatar_path=image_helper.save_image(data["image"],folder=folder,name=avatar)
            basename=image_helper.get_basename(avatar_path)
            return {"message":f"avatar with the basename {basename} has been uploaded"},200
        except UploadNotAllowed:
            extension=image_helper.get_extension(data["image"])
            return {"message":f"this extension {extension} is not accepted  "},400
@dish_namespace.route("/avatar/<id>")       
class GetAvatar(Resource):
    def get(self,id):
        filename=f"user_{id}"
        folder="avatars"
        avatar=image_helper.find_image_format(filename,folder)
        if avatar:
            current_dir = os.getcwd()



            
            file_path_=os.path.join(current_dir,avatar)
            absolute_path=os.path.abspath(file_path_)
        
            return send_file(absolute_path)
        else:
            return {"message":"avarar not found"},404
