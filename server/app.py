#!/usr/bin/env python3
import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_restful import Api
from models import db, Restaurant, RestaurantPizza, Pizza

BASEDIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DBURI", f"sqlite:///{os.path.join(BASEDIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route("/restaurants", methods=['GET'])
def list_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([{
        "id": restaurant.id,
        "name": restaurant.name,
        "address": restaurant.address
    } for restaurant in restaurants])

@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant_by_id(id):
    restaurant = db.session.get(Restaurant, id)
    if restaurant is None:
        return jsonify({'error': 'Restaurant not found'}), 404

    restaurant_data = {
        "id": restaurant.id,
        "name": restaurant.name,
        "address": restaurant.address,
        "restaurant_pizzas": [
            {
                "id": rp.id,
                "pizza": {
                    "id": rp.pizza.id,
                    "name": rp.pizza.name,
                    "ingredients": rp.pizza.ingredients
                },
                "pizza_id": rp.pizza_id,
                "price": rp.price,
                "restaurant_id": rp.restaurant_id
            }
            for rp in restaurant.restaurant_pizzas
        ]
    }
    return jsonify(restaurant_data)

@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    if restaurant is None:
        return jsonify({"error": "Restaurant not found"}), 404

    db.session.delete(restaurant)
    db.session.commit()
    return jsonify({"message": "Restaurant deleted successfully"}), 204

@app.route("/pizzas", methods=["GET"])
def list_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([{
        "id": pizza.id,
        "name": pizza.name,
        "ingredients": pizza.ingredients
    } for pizza in pizzas])

@app.route("/restaurant_pizzas", methods=["POST"])
def add_restaurant_pizza():
    data = request.get_json()
    restaurant = db.session.get(Restaurant, data.get('restaurant_id'))
    pizza = db.session.get(Pizza, data.get('pizza_id'))

    if not restaurant or not pizza:
        return jsonify({"errors": ["validation errors"]}), 400

    try:
        new_restaurant_pizza = RestaurantPizza(
            price=data['price'],
            pizza_id=data['pizza_id'],
            restaurant_id=data['restaurant_id']
        )
        db.session.add(new_restaurant_pizza)
        db.session.commit()

        response_data = {
            "id": new_restaurant_pizza.id,
            "pizza": {
                "id": pizza.id,
                "name": pizza.name,
                "ingredients": pizza.ingredients
            },
            "pizza_id": pizza.id,
            "price": new_restaurant_pizza.price,
            "restaurant": {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address
            },
            "restaurant_id": restaurant.id
        }
        return jsonify(response_data), 201

    except ValueError:
        return jsonify({"errors": ["validation errors"]}), 400

if __name__ == "__main__":
    app.run(port=5555, debug=True)