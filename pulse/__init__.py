from flask import Blueprint

blueprint = Blueprint('pulse', __name__, template_folder='templates', static_folder='static')

LABEL = 'Pulse'

import pulse.core