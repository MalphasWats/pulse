from flask import (Blueprint, request, session, redirect, 
                   url_for, abort, render_template, flash, make_response)
                   
import database
import datetime

from pyDimension.access_control import login_required

mod = Blueprint('pulse', __name__, template_folder='templates', static_folder='static')


@mod.route('/')
@login_required
def home():
    return render_template('pulse.html', requests=database.get_requests())
    

@mod.route('/log/')
def log_request():
    request_url = request.referrer
    remote_addr = request.remote_addr
    user_agent = request.headers['User-Agent']
    referrer = request.args.get('referrer')
        
    database.log_request(request_url, remote_addr, user_agent, referrer)
    
    r = make_response(redirect(url_for('pulse.static', filename='pulse.gif')))
    r.headers.add('Last-Modified', datetime.datetime.now())
    r.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0')
    r.headers.add('Pragma', 'no-cache')

    return r
    
@mod.route('/a/')
def analytics():
    r = make_response(render_template('pulse.js'))
    r.mimetype='text/javascript'

    return r