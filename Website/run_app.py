# -*- coding: utf-8 -*-
from flask import Flask
from flask import render_template
from flask import request
from flask_cors import CORS

import os
import re
import json

app = Flask(__name__)

    
@app.route("/", methods=['GET','POST'])
def index():
    return render_template('index.html')


if __name__ == "__main__":
    CORS(app, supports_credentials=True)
    app.run(host='0.0.0.0',debug=True, port=80,threaded=True,processes=1)
