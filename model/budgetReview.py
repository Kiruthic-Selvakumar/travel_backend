import logging
from sqlite3 import IntegrityError
from sqlalchemy import Text, Integer, String, DateTime
from sqlalchemy.exc import IntegrityError
from __init__ import app, db
from model.user import User
from model.group import Group 
from datetime import datetime

class BudgetReview(db.Model):
    __tablename__ = 'budget_reviews'

    id = db.Column(db.Integer, primary_key=True)
    _title = db.Column(db.String(255), nullable=False)
    _comment = db.Column(db.String(255), nullable=False)
    _rating = db.Column(db.Integer, nullable=False)
    _hashtag = db.Column(db.String(255), nullable=True)
    _user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    _group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False) 

    def __init__(self, title, comment, rating, hashtag=None, user_id=None, group_id=None):
        """
        Constructor for BudgetReview object creation.
        """
        self._title = title
        self._comment = comment
        self._rating = rating
        self._hashtag = hashtag
        self._user_id = user_id
        self._group_id = group_id 

    def __repr__(self):
        return f"BudgetReview(id={self.id}, title={self._title}, comment={self._comment}, rating={self._rating}, hashtag={self._hashtag}, user_id={self._user_id}, group_id={self._group_id})"  # Changed to group_id

    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            logging.warning(f"IntegrityError: Could not create review with title '{self._title}' due to {str(e)}.")
            return None
        return self
        
    def read(self):
        user = User.query.get(self._user_id)
        group = Group.query.get(self._group_id)  
        data = {
            "id": self.id,
            "title": self._title,
            "comment": self._comment,
            "rating": self._rating,
            "hashtag": self._hashtag,
            "user_name": user.name if user else None,
            "group_name": group.name if group else None 
        }
        return data

    def update(self):
        inputs = BudgetReview.query.get(self.id)
        
        title = inputs._title
        comment = inputs._comment
        rating = inputs._rating
        hashtag = inputs._hashtag
        group_id = inputs._group_id 
        user_id = inputs._user_id

        if title:
            self._title = title
        if comment:
            self._comment = comment
        if rating:
            self._rating = rating
        if hashtag:
            self._hashtag = hashtag
        if group_id:
            self._group_id = group_id 
        if user_id:
            self._user_id = user_id

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            logging.warning(f"IntegrityError: Could not update review with title '{title}'.")
            return None
        return self
    
    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def restore(data):
        for review_data in data:
            _ = review_data.pop('id', None)
            group_name = review_data.get("group", None)
            group = Group.query.filter_by(name=group_name).first()
            if group:
                budget_review = BudgetReview(
                    review_data['title'],
                    review_data['comment'],
                    review_data['rating'],
                    review_data.get('hashtag', None),
                    review_data['user_id'],
                    group.id
                )
                budget_review.create()
    
def initBudgetReviews():
    with app.app_context():
        db.create_all()
        budget_reviews = [
            BudgetReview(title='Test Food Review', comment='Reviewing the new restaurant menu for Q1.', rating=4, hashtag='food', user_id=1, group_id=1),
            BudgetReview(title='Test Activity Review', comment='Reviewing the new hiking trail experience in Q1.', rating=5, hashtag='activity', user_id=2, group_id=2),
            BudgetReview(title='Test Hotel Review', comment='Reviewing the Q1 hotel stay for a corporate event.', rating=3, hashtag='hotel', user_id=1, group_id=3),
        ]
        
        for review in budget_reviews:
            try:
                review.create()
                print(f"Record created: {repr(review)}")
            except IntegrityError:
                db.session.remove()
                print(f"Records exist, duplicate data, or error: {review._title}")
