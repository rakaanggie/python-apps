from flask import Flask, request, jsonify
from flask_mqtt import Mqtt
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os
load_dotenv()

app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = os.getenv("MQTT_BROKER_URL")
app.config['MQTT_BROKER_PORT'] = int(os.getenv("MQTT_BROKER_PORT"))
app.config['MQTT_USERNAME'] = os.getenv("MQTT_USERNAME")
app.config['MQTT_PASSWORD'] = os.getenv("MQTT_PASSWORD")
app.config['MQTT_KEEPALIVE'] = int(os.getenv("MQTT_KEEPALIVE"))
app.config['MQTT_TLS_ENABLED'] = False
app.config['MYSQL_HOST'] = os.getenv("MYSQL_HOST")
app.config['MYSQL_USER'] = os.getenv("MYSQL_USER")
app.config['MYSQL_PASSWORD'] = os.getenv("MYSQL_PASSWORD")
app.config['MYSQL_DB'] = os.getenv("MYSQL_DB")


topic = '/sensor/suhu'
mqtt_client = Mqtt(app)
mysql = MySQL(app)

@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
   if rc == 0:
       print('Connected successfully')
       mqtt_client.subscribe(topic) # subscribe topic
   else:
       print('Bad connection. Code:', rc)


@mqtt_client.on_message()
def handle_mqtt_message(client, userdata, message):
   data = dict(
       topic=message.topic,
       payload=message.payload.decode()
  )
   print('Received message on topic: {topic} with payload: {payload}'.format(**data))
   with app.app_context():
      cur = mysql.connection.cursor()
      cur.execute("INSERT INTO tbl_store (topic, message) VALUES(%s, %s)", (data["topic"], data["payload"]))
      mysql.connection.commit()
      cur.close()

@app.route('/', methods=['GET'])
def dashboard():
   cur = mysql.connection.cursor()
   cur.execute("SELECT message FROM tbl_store WHERE id=(SELECT MAX(id) FROM tbl_store)")
   data = cur.fetchone()
   return f"Suhu terahir adalah {data[0]}"


if __name__ == '_main_':
   app.run(host='0.0.0.0', port=5000)
