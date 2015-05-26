#!/usr/bin/env python
import pika

#Connect to the broker
connection = pika.BlockingConnection(pika.ConnectionParameters(
               'localhost'))
channel = connection.channel()

channel.queue_declare(queue='hello_queue')


channel.basic_publish(exchange='',
                      routing_key='hello_queue',
                      body='Hello World!')
print " [x] Sent 'Hello World!'"

connection.close()


