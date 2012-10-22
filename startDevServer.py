from flask import Flask

import pulse.pulse as pulse

app = Flask(__name__)
app.config.from_object('settings')

app.register_blueprint(pulse.blueprint)

app.run(host='0.0.0.0', debug=True)