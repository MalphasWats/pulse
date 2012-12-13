from flask import request, session, redirect, url_for, abort, render_template, flash, make_response
                   
import datetime

from instruments.core import public_endpoint

from pulse import blueprint
import database


@blueprint.route('/')
def index():
    return render_template('pulse.html',
                           visits=database.get_visit_totals(),
                           pages_today=database.get_requests_today(),
                           referrers=database.get_referrers(),
                           pages=database.get_page_visits(),
                           search_terms=database.get_search_strings()
                          )
    

@blueprint.route('/log/')
@public_endpoint
def log_request():
    request_url = request.referrer
    remote_addr = request.remote_addr
    user_agent = request.headers['User-Agent']
    referrer = request.args.get('referrer')
    
    if request_url:
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
    
    
def get_content_widget():
    return render_template('pulse_content_widget.html', visits=database.get_visit_totals())