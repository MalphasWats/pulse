from flask import Blueprint

blueprint = Blueprint('pulse', __name__, template_folder='templates', static_folder='static')

LABEL = 'Pulse'
ICON = 'bar-chart'

import pulse.core