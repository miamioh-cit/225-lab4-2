import sqlite3, os
DB = os.environ.get('DEMO_DB', '/nfs/demo.db')
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("INSERT INTO contacts (name,email) VALUES (?,?)", ("Test User","test@example.com"))
conn.commit()
conn.close()
print("Inserted test row")
