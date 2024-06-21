import pika
import json

# RabbitMQ connection parameters
rabbitmq_host = 'localhost'
rabbitmq_queue = 'order_queue'

def process_order(order):
    print(f"Processing order: {order}")
    # Here you can add the logic to process the order
    # For example, update the order status in your database

def callback(ch, method, properties, body):
    order = json.loads(body)
    process_order(order)

def start_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    channel = connection.channel()
    channel.queue_declare(queue=rabbitmq_queue)
    channel.basic_consume(queue=rabbitmq_queue, on_message_callback=callback, auto_ack=True)
    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    start_consumer()
