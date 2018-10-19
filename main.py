from flask import Flask, request, render_template, url_for, redirect
import re
app = Flask(__name__)

app.config['DEBUG'] = True

@app.route('/')
def index():
    return render_template('index.html')


app.run()