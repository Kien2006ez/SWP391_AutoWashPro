from src.database.db import db

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), default='pending')