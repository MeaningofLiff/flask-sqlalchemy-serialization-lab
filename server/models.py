cat > server/models.py <<'PY'
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy
from marshmallow import Schema, fields

db = SQLAlchemy()


class DummyMarshmallow:
    def init_app(self, app):
        pass


ma = DummyMarshmallow()


class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    reviews = db.relationship('Review', back_populates='customer')
    items = association_proxy('reviews', 'item')

    def __repr__(self):
        return f'<Customer {self.id}, {self.name}>'


class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.Float)

    reviews = db.relationship('Review', back_populates='item')
    customers = association_proxy('reviews', 'customer')

    def __repr__(self):
        return f'<Item {self.id}, {self.name}, {self.price}>'


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))

    customer = db.relationship('Customer', back_populates='reviews')
    item = db.relationship('Item', back_populates='reviews')

    def __repr__(self):
        return f'<Review {self.id}, {self.comment}>'


class CustomerSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    reviews = fields.Nested(
        lambda: ReviewSchema(exclude=('customer',)),
        many=True
    )
    items = fields.List(
        fields.Nested(
            lambda: ItemSchema(exclude=('reviews', 'customers'))
        )
    )


class ItemSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    price = fields.Float()
    reviews = fields.Nested(
        lambda: ReviewSchema(exclude=('item',)),
        many=True
    )
    customers = fields.List(
        fields.Nested(
            lambda: CustomerSchema(exclude=('reviews', 'items'))
        )
    )


class ReviewSchema(Schema):
    id = fields.Int()
    comment = fields.Str()
    customer = fields.Nested(
        lambda: CustomerSchema(exclude=('reviews', 'items'))
    )
    item = fields.Nested(
        lambda: ItemSchema(exclude=('reviews', 'customers'))
    )
PY
