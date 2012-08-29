import psycopg2
from pyDimension import app as pyDimension

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