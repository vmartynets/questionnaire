DEBUG = True
HOST = '0.0.0.0'
SECRET_KEY = 'development key'

DBSERVER = 'mysql://'
DBUSER = 'root'
DBPASSWORD = ''
DBNAME = 'course'
DBHOST = 'localhost'

DATABASE_QUERY_TIMEOUT = 0.5

if DBPASSWORD:
    SQLALCHEMY_DATABASE_URI = '%s%s:%s@%s/%s' % (DBSERVER, DBUSER, DBPASSWORD, DBHOST, DBNAME)
else:
    SQLALCHEMY_DATABASE_URI = '%s%s@%s/%s' % (DBSERVER, DBUSER, DBHOST, DBNAME)
