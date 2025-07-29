import psycopg2

def get_db_connection(db_name, db_user, db_password, db_host, db_port="5432"):
    return psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )

