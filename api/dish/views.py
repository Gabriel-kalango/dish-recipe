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
    @dish_namespace.marshal_list_with(dish_view)
    def get(self):
        dishes=Dish.query.all()
    

        try:
            return dishes, 200
        except AttributeError as e:
            print("Error serializing field: ", e)
            return {'message': 'Error serializing data'}, 500
    
        
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
    @dish_namespace.marshal_with(dish_create,envelope="resource")
    def get(self,id):
        dish=Dish.query.get_or_404(id)
        print(dish.__dict__)  # print the keys of the 'Dish' object
        print(dish_view.keys())  
        
        return  {
            "id": dish.id,
            "name": dish.name,
            "ingredients": dish.ingredients,
            "instructions": dish.instructions,
        }, 200
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
            if user is not  None:
                if user not in dish.user_likes:
                    dish.user_likes.append(user)
                    dish.update()
                    
                else:
                    dish.user_likes.remove(user)
                    dish.update()
                updated_likes=len(dish.user_likes)
                emit('like', {'dish_id': dish.id, 'like_count': updated_likes}, broadcast=True , namespace=dish_namespace)

                return {"number_of_likes":updated_likes}

            abort(400,message="user doesnt exist")

@dish_namespace.route("/image/<id>")
class Imagee(Resource):
    @jwt_required()
    def put(self,id):
        # a put method used to upload the image , the image path is then saved in the database while the image is saved in a folder (static/images)
        data=ImageSchema().load(request.files)
        user_id=get_jwt_identity()
        
        avatar_path=image_helper.find_image_format(data["image"].filename)
        if avatar_path:
            try:
                print(avatar_path)
                os.remove(avatar_path)
            except:
                abort(500,message="avatar deletion failed")
        try:
            dish=Dish.query.get_or_404(id)
            if dish.user_id!=user_id:
                abort(403,message="you are not authorized to make this change")
            image_path=image_helper.save_image(data["image"])
            file_path=image_helper.get_path(image_path)
            dish.dish_image_url=file_path
            dish.update()
            basename=image_helper.get_basename(image_path)
            return {"message":f"{basename} has been uploaded"},201
        except UploadNotAllowed:
            extension=image_helper.get_extension(data["image"])
            return {"message":f"this {extension} is not allowed"},400


@dish_namespace.route("/images/<id>")
class image(Resource):
# a get method for reading the images 
    def get(self,id):
        dish=Dish.query.get_or_404(id)
        image_path=dish.dish_image_url
        try:
            # get the current working directory
            current_dir = os.getcwd()


            
            
            
            file_path_=os.path.join(current_dir,image_path)
            absolute_path=os.path.abspath(file_path_)
            print(absolute_path)
        
            return send_file(absolute_path)

   

        except FileNotFoundError:
            abort(404,message=f"file not found ")
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




