from datetime import datetime
import json
import pika
from pika.exceptions import AMQPConnectionError
import django
import os
import sys
import time


sys.path.append("")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "attendees_bc.settings")
django.setup()

from attendees.models import AccountVO

def update_account_vo(ch, method, properties, body):
    content = json.load(body)
    first_name = content["first_name"]
    last_name = content["last_name"]
    email = content["email"]
    is_active=content["is_active"]
    updated_string = content["updated"]
    updated = datetime.isoformat(updated_string)
    if is_active:
       obj, created = AccountVO.objects.update_or_create(
           first_name = first_name,
           last_name= last_name,
           email = email,
           is_active = is_active,
           updated = updated,
           defaults ={"first_name": first_name,
                      "last_name": last_name,
                      "email": email,
                      "is_active": is_active,
                      "updated": updated,
                      }
       )
    else:
        AccountVO.objects.delete()

def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()

    channel.exchange_declare(exchange='account_info', exchange_type='fanout')

    result = channel.queue_declare(queue='account_queue', exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange='account_info', queue=queue_name)

    print(' [*] Waiting for logs. To exit press CTRL+C')
    channel.basic_consume(
        queue=queue_name, on_message_callback=update_account_vo, auto_ack=True)

    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
