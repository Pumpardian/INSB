import sqlite3

def create_db():
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            email TEXT
        )
    ''')
    
    users = [
        ('admin', 'admin123', 'admin@example.com'),
        ('john_doe', 'pass456', 'john@example.com'),
        ('alice', 'alice789', 'alice@example.com'),
        ('bob', 'bob321', 'bob@example.com')
    ]
    
    cursor.executemany(
        'INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
        users
    )
    conn.commit()
    conn.close()

def vulnerable_login(username, password):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    print(f"Executing query: {query}")
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        print(f"Error: {e}")
        conn.close()
        return None

def secure_login(username, password):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    try:
        cursor.execute(query, (username, password))
        result = cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        print(f"Error: {e}")
        conn.close()
        return None

if __name__ == "__main__":
    create_db()

    print("Parametrized approach: SQL-Injection wont work here")
    result = secure_login("admin' --", "tryingtohackthis")
    if not result:
        print("SQL-Injection is not working!")
    else:
        print("This is not possible")

    print("\nBasic login using unsecure method")
    result = vulnerable_login("admin", "admin123")
    if result:
        print(f"Log in successfull: {result}")
    else:
        print("Invalid credentials")

    print("\nSQL-Injection - getting access")
    injected_username = "admin' --"
    result = vulnerable_login(injected_username, "anypasshere")
    print(f"Success, data: {result}")

    print("\nSQL-Injection - getting all users data")
    injected_username = "' OR '1'='1' --"
    result = vulnerable_login(injected_username, "anypasshereagain")
    print(f"Success, here is all users data: {result}")

    print("\nSQL-Injection - getting data from other tables")
    injected_username = "' UNION SELECT id, username, password, email FROM users --"
    result = vulnerable_login(injected_username, "doesntmatterasalways")
    print(f"Success, here is the data: {result}")