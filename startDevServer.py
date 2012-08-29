from flask import Flask

import pulse.core

app = Flask(__name__)

app.register_blueprint(pulse.core.mod)

app.run(host='0.0.0.0', debug=True)