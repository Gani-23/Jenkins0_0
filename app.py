from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/hello')
def hello():
    return "Hello, I'm still alive!"

app.run(port=5000, debug=True, host='0.0.0.0')
