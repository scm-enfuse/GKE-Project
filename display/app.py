from flask import Flask
import json
import requests


cluster_ip_address = "10.83.241.140"
service_port = "80"

app = Flask(__name__)




@app.route('/')
def home():
    doc = requests.get(f"http://{cluster_ip_address}:{service_port}/")
    doc_text = doc.text
    return f"Value from service: {doc_text}"

if __name__ == '__main__':
    app.run(host='127.0.0.1', use_reloader=True, port=8000, debug=True)
