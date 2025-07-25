import sqlite3

conn = sqlite3.connect('noww_club.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables:", [t[0] for t in tables])

# Check for vision board related data
for table_name in [t[0] for t in tables]:
    if 'vision' in table_name.lower():
        print(f"\nTable {table_name}:")
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  Rows: {count}")
        
        # Show first few rows
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
        rows = cursor.fetchall()
        for row in rows:
            print(f"  Sample: {row}")

conn.close()
