import sqlite3, os
DB = os.environ.get('DEMO_DB', '/nfs/demo.db')
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute('DELETE FROM contacts')
conn.commit()
conn.close()
print("Cleared contacts")
