from flask import (Blueprint, request, session, redirect, 
                   url_for, abort, render_template, flash, make_response)
                   
import database
import datetime

from instruments.core import public_endpoint

blueprint = Blueprint('pulse', __name__, template_folder='templates', static_folder='static')

LABEL = 'Pulse'


@blueprint.route('/')
def index():
    return render_template('pulse.html',
                           visits=database.get_visit_totals(),
                           pages=database.get_page_visits(),
                           requests=database.get_requests(),
                           search_terms=database.get_search_strings()
                           )
    

@blueprint.route('/log/')
@public_endpoint
def log_request():
    request_url = request.referrer
    remote_addr = request.remote_addr
    user_agent = request.headers['User-Agent']
    referrer = request.args.get('referrer')
        
    database.log_request(request_url, remote_addr, user_agent, referrer)
    
    r = make_response(blueprint.send_static_file('pulse.gif'))
    r.headers.add('Last-Modified', datetime.datetime.now())
    r.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0')
    r.headers.add('Pragma', 'no-cache')

    return r
    
@blueprint.route('/a/')
@public_endpoint
def analytics():
    r = make_response(render_template('pulse.js'))
    r.mimetype='text/javascript'

    return r