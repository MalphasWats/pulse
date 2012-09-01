import psycopg2
from pyDimension import app as pyDimension

import datetime

#DSN = 'dbname=db_name user=user_name password=password'

def connect():
    DSN = pyDimension.config['PULSE_DSN']

    conn = psycopg2.connect(DSN)
    
    return conn
    
def create_tables():
    query = """
        CREATE TABLE requests (
            request_id SERIAL,
            request_url TEXT,
            remote_addr TEXT,
            user_agent TEXT,
            referrer TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
    """
    
    conn = connect()
    curs = conn.cursor()
    
    curs.execute(query)
    
    conn.commit()
    curs.close()
    conn.close()
    

def log_request(request_url, remote_addr, user_agent, referrer):
    conn = connect()
    
    curs = conn.cursor()
    
    query = """
        INSERT INTO requests (request_url, remote_addr, user_agent, referrer)
        VALUES (%s, %s, %s, %s);    
    """
    
    curs.execute(query, (request_url, remote_addr, user_agent, referrer))
    
    conn.commit()
    
    conn.close()
    
    
def get_visit_totals():
    ever = get_visit_total_between()
    today = datetime.date.today()
    last_month = today - datetime.timedelta(31)
    last_month = get_visit_total_between(last_month.strftime('%Y-%m-01'), today.strftime('%Y-%m-01'))
    this_month = get_visit_total_between(today.strftime('%Y-%m-01'))
    today = get_visit_total_between(today.strftime('%Y-%m-%d'))
    
    return (ever, last_month, this_month, today)
    
    
def get_visit_total_between(start_date='2012-08-29', end_date=datetime.date.today().strftime('%Y-%m-%d 23:59:59')): #'
    conn = connect()
    curs = conn.cursor()
    
    query = """
        SELECT count(request_id)
        FROM requests
        WHERE timestamp >= %s
        AND timestamp < %s
    """
    
    curs.execute(query, (start_date, end_date))
    result = curs.fetchone()
    conn.rollback()
    conn.close()
    
    if result:
        return result[0]
    else:
        return 0
        
        
def get_page_visits():
    conn = connect()
    curs = conn.cursor()

    query = """
        SELECT request_url, count(request_id) AS number_of_requests
        FROM requests 
        GROUP BY request_url 
        ORDER BY number_of_requests DESC;
    """
    
    curs.execute(query)
    results = curs.fetchall()
    
    conn.rollback()
    conn.close()
    
    return results
    
    
    
    
def get_requests():
    conn = connect()
    
    curs = conn.cursor()
    
    query = """
        SELECT * FROM requests
        ORDER BY timestamp DESC;
    """
    
    curs.execute(query)
    results = curs.fetchall()
    conn.rollback()
    
    conn.close()
    
    return results