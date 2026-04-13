from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "App Running Successfully"

@app.route("/test")
def test():
    return "Server working"
