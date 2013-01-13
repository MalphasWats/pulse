import psycopg2
from instruments import app
import codecs

import datetime

#DSN = 'dbname=db_name user=user_name password=password'

def connect():
    DSN = app.config['PULSE_DSN']

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
    curs.close()
    conn.close()
    
    
def get_visit_totals():
    today = datetime.date.today()
    end_of_today = datetime.date.today().strftime('%Y-%m-%d 23:59:59')
    last_month = today - datetime.timedelta(31)
    
    visits_ever = get_visit_total_between('2012-08-29', end_of_today)
    
    visits_last_month = get_visit_total_between(last_month.strftime('%Y-%m-01'), today.strftime('%Y-%m-01'))
    visits_this_month = get_visit_total_between(today.strftime('%Y-%m-01'), end_of_today)
    visits_today = get_visit_total_between(today.strftime('%Y-%m-%d'), end_of_today)
    
    return (visits_ever, visits_last_month, visits_this_month, visits_today)
    
    
def get_visit_total_between(start_date, end_date):
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
    curs.close()
    conn.close()
    
    if result:
        return result[0]
    else:
        return 0
        
        
def get_page_visits():
    conn = connect()
    curs = conn.cursor()
    
    query = """select distinct substring(request_url, 0, position('/' in substring(request_url, 8))+7)
               from requests;"""
               
    curs.execute(query)
    sites = curs.fetchall()
    
    visits = {}
    
    for site in sites:
        root_url = site[0]
        
        query = """
                SELECT substring(request_url, position('/' in substring(request_url, 8))+7) as request_url, 
                        count(request_id) AS number_of_requests
                FROM requests
                WHERE request_url LIKE %s
                GROUP BY request_url 
                ORDER BY number_of_requests DESC;
        """
    
        curs.execute(query, (root_url+'%',))
        visits[root_url] = curs.fetchall()
    
    conn.rollback()
    curs.close()
    conn.close()
    
    return visits
    
    
def get_referrers():
    conn = connect()
    curs = conn.cursor()
    
    query = """select distinct substring(request_url, 0, position('/' in substring(request_url, 8))+7)
               from requests;"""
               
    curs.execute(query)
    sites = curs.fetchall()
    
    referrers = {}
    
    for site in sites:
        root_url = site[0]
        
        query = """
                SELECT substring(request_url, position('/' in substring(request_url, 8))+7) as request_url, 
                        referrer, timestamp
                FROM requests
                WHERE request_url LIKE %(site)s
                AND referrer NOT LIKE ''
                AND referrer NOT LIKE %(site)s
                AND referrer NOT LIKE '%%.google.%%'
                AND referrer NOT LIKE '%%.bing.%%'
                AND referrer NOT LIKE '%%.baidu.%%'
                ORDER BY timestamp DESC;
        """
        
        curs.execute(query, {'site': root_url+'%'})
        referrers[root_url] = curs.fetchall()
    
    conn.rollback()
    curs.close()
    conn.close()
    
    return referrers
    

def get_search_strings():
    #currently only finds google searches
    
    conn = connect()
    curs = conn.cursor()

    query = """SELECT queries, count(queries) AS count
        FROM
           (SELECT regexp_split_to_table(replace(replace(substring(q_string, 3), '+', ' '), '%20', ' '), E' ') AS queries
            FROM (
                SELECT regexp_split_to_table(referrer, E'&+') AS q_string
                FROM requests
                WHERE referrer LIKE '%google%'
                AND referrer NOT LIKE '%q=&%')
            AS q_strings
            WHERE q_string LIKE 'q=%')
        AS query_strings
        WHERE length(queries) > 3
        GROUP BY queries
        ORDER BY count DESC, queries
        LIMIT 20;"""
    
    curs.execute(query)
    results = curs.fetchall()
    
    conn.rollback()
    curs.close()
    conn.close()
    
    return results
    
    
def get_requests_today():
    conn = connect()
    
    curs = conn.cursor()
    
    today = datetime.date.today().strftime('%Y-%m-%d 00:00:00')
    end_of_today = datetime.date.today().strftime('%Y-%m-%d 23:59:59')
    
    query = """select distinct substring(request_url, 0, position('/' in substring(request_url, 8))+7)
               from requests;"""
               
    curs.execute(query)
    sites = curs.fetchall()
    
    requests = {}
    
    for site in sites:
        root_url = site[0]
        
        query = """
                SELECT substring(request_url, position('/' in substring(request_url, 8))+7) as request_url, 
                        timestamp, remote_addr
                FROM requests
                WHERE request_url LIKE %(site)s
                AND timestamp > %(today)s
                AND timestamp < %(end_of_today)s
                ORDER BY timestamp DESC;
        """
        
        curs.execute(query, {'site': root_url+'%', 'today': today, 'end_of_today':end_of_today})
        requests[root_url] = curs.fetchall()
    
    conn.rollback()
    curs.close()
    conn.close()
    
    return requests
    
    
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
    curs.close()
    conn.close()
    
    return results