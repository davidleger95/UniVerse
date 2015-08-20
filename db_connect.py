

import MySQLdb


def connection():
    conn = MySQLdb.connect(host="localhost",
                          user = "root",
                          passwd = "root",
                          db = "universe_db")
    
    c = conn.cursor()
    
    return c, conn
    