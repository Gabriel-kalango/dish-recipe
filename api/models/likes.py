from ..utils import db
class Like(db.Model):
    __tablename__="like"
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False)
    dish_id=db.Column(db.Integer,db.ForeignKey("dish.id"),nullable=False)
    