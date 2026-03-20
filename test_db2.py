import psycopg2
import sys

try:
    conn = psycopg2.connect("postgresql://user:onion123@127.0.0.1:5432/scoinvestigator")
    print("CONNECTION SUCESSFUL!")
    conn.close()
except psycopg2.OperationalError as e:
    print("OPERATIONAL ERROR DETAILS:")
    print(repr(e))
    print(e.pgerror)
    print(e.pgcode)
except Exception as e:
    print("OTHER ERROR:", type(e), str(e))
