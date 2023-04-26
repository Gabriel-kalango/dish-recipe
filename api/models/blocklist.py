from ..utils import db 
#creating a database model to handle logging out a user
class BlockliskModel(db.Model):
    __tablename__="blocklist"
    id=db.Column(db.Integer,primary_key=True)
    jwt=db.Column(db.String(1000), nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()