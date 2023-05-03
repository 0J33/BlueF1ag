from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is running."

def run():
  app.run(host='0.0.0.0',port=1111)

def keep_alive():
    t = Thread(target=run)
    t.start()
    
keep_alive()