from flask import Blueprint, jsonify, request
from flask_expects_json import expects_json
from flask_jwt_extended import jwt_required
import pika
import json

api_blueprint = Blueprint('api', __name__)

# In-memory database
books = [
    {"id": 1, "title": "Book One", "author": "Author One", "price": 10.99},
    {"id": 2, "title": "Book Two", "author": "Author Two", "price": 12.99},
    {"id": 3, "title": "Book Three", "author": "Author Three", "price": 15.99}
]

orders = []

# RabbitMQ connection parameters
rabbitmq_host = 'localhost'
rabbitmq_queue = 'order_queue'

def send_order_to_queue(order):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    channel = connection.channel()
    channel.queue_declare(queue=rabbitmq_queue)
    channel.basic_publish(exchange='', routing_key=rabbitmq_queue, body=json.dumps(order))
    connection.close()

# JSON schema for order validation
order_schema = {
    "type": "object",
    "properties": {
        "book_id": {"type": "integer"},
        "quantity": {"type": "integer", "minimum": 1}
    },
    "required": ["book_id"],
    "additionalProperties": False
}

@api_blueprint.route('/books', methods=['GET'])
def get_books():
    return jsonify({"books": books}), 200

@api_blueprint.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = next((book for book in books if book["id"] == book_id), None)
    if book:
        return jsonify({"book": book}), 200
    return jsonify({"error": "Book not found"}), 404

@api_blueprint.route('/orders', methods=['POST'])
@jwt_required()
@expects_json(order_schema)
def place_order():
    try:
        order_data = request.json
        book_id = order_data.get("book_id")
        quantity = order_data.get("quantity", 1)

        book = next((book for book in books if book["id"] == book_id), None)
        if not book:
            return jsonify({"error": "Book not found"}), 404

        order_id = len(orders) + 1
        order = {
            "id": order_id,
            "book_id": book_id,
            "quantity": quantity,
            "status": "processing"
        }
        orders.append(order)
        
        # Send order to RabbitMQ queue
        send_order_to_queue(order)

        return jsonify({"order": order}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api_blueprint.route('/orders/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order_status(order_id):
    order = next((order for order in orders if order["id"] == order_id), None)
    if order:
        return jsonify({"order": order}), 200
    return jsonify({"error": "Order not found"}), 404
