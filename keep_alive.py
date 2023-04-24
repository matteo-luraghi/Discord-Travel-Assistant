from flask import Flask
from threading import Thread
import os

app = Flask('')

@app.route('/')
def home():
  return "Hello, I'm alive"

host = '0.0.0.0'
port = 8080

def run():
  app.run(host=host, port=port)

def keep_alive():
  t = Thread(target=run)
  t.start()