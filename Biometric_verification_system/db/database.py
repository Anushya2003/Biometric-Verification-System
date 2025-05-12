import psycopg2

def get_connection():
    return psycopg2.connect(
        dbname='life_certification_db',
        user='postgres',
        password='jiaamulu',
        host='localhost',
        port='5432'
    )
