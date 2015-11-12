

import MySQLdb


def connection():
    conn = MySQLdb.connect(host="localhost",
                           user = "root",
                           passwd = "root",
                           db = "universe_db",
                           use_unicode=True, 
                           charset='utf8')
    
    c = conn.cursor(MySQLdb.cursors.DictCursor)
    
    return c, conn
    