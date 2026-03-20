import psycopg2
conn = psycopg2.connect('postgresql://user:onion123@localhost:5432/scoinvestigator')
print("SUCCESS")
conn.close()
