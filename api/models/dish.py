from ..utils import db

from datetime import datetime
#creating a database model for creating(posting) dishes
class Dish(db.Model):
    __tablename__ = 'dish'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ingredients = db.Column(db.JSON, nullable=False)
    instructions = db.Column(db.String(1000), nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False)
    date_posted=db.Column(db.DateTime,default=datetime.utcnow)
    user_likes=db.relationship("User",backref=db.backref('dishes_liked', lazy='dynamic'),cascade="all, delete",secondary="like")

   
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

