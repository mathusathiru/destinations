import time, bcrypt


def create_tables(c):
    c.execute("""CREATE TABLE IF NOT EXISTS users (
                 user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT NOT NULL,
                 password TEXT NOT NULL
                 )""")

    c.execute("""CREATE TABLE IF NOT EXISTS search_history (
                 search_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER NOT NULL,
                 place_name TEXT NOT NULL,
                 address TEXT NOT NULL,
                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                 FOREIGN KEY (user_id) REFERENCES users (user_id)
                 )""")


def login(c):
    username = input("\nEnter your username: ")
    password = input("Enter your password: ")
    c.execute("SELECT user_id, password FROM users WHERE username=?",
              (username,))
    user_data = c.fetchone()
    if user_data and bcrypt.checkpw(password.encode("utf-8"),
                                    user_data[1].encode("utf-8")):
        print("\nLogin successful!")
        time.sleep(0.65)
        return user_data[0]
    else:
        print("\nError: invalid username or password")
        time.sleep(0.65)
        return None


def delete_user(c, conn, user_id):
    c.execute("SELECT username FROM users WHERE user_id=?", (user_id,))
    username = c.fetchone()
    c.execute("DELETE FROM search_history WHERE user_id=?", (user_id,))
    c.execute("DELETE FROM users WHERE user_id=?", (user_id,))
    conn.commit()
    print("Account for", username, "has been successfully deleted")
    time.sleep(0.65)


def check_search_history(c, user_id):
    c.execute("SELECT place_name, address, timestamp FROM search_history "
              "WHERE user_id=?", (user_id,))
    search_history = c.fetchall()
    if not search_history:
        return False
    else:   
        return True


def print_search_history(c, user_id):
    c.execute("SELECT place_name, address, timestamp FROM search_history "
              "WHERE user_id=?", (user_id,))
    search_history = c.fetchall()
    if not search_history:
        print("\nSearch history is empty\n")
    else:
        print("\nSearch History:\n")
        for index, entry in enumerate(search_history):
            place_name, address, timestamp = entry
            print("Place Name:", place_name)
            print("Address:", address)
            print("Timestamp:", timestamp)
            if index < len(search_history) - 1:
                print("-" * 20)
            else:
                print()
    time.sleep(0.65)


def print_most_popular_searches(c, user_id):
    c.execute("SELECT place_name, address, COUNT(*) as search_count "
              "FROM search_history "
              "WHERE user_id=? "
              "GROUP BY place_name, address "
              "ORDER BY search_count DESC",
              (user_id,))
    popular_searches = c.fetchall()
    if not popular_searches:
        print("Search history is empty\n")
    else:
        print("\nMost Popular Searches:")
        ## show top 10s and indexes
        for index, entry in enumerate(popular_searches):
            place_name, address, search_count = entry
            print("Place Name:", place_name)
            print("Address:", address)
            print("Search Count:", search_count)
            if index < len(popular_searches) - 1:
                print("-" * 20)
            else:
                print()
    time.sleep(0.65)


def search_history(c, user_id, keyword):
    c.execute("SELECT place_name, address, timestamp "
              "FROM search_history "
              "WHERE user_id=? AND (place_name LIKE ? OR address LIKE ?)",
              (user_id, f"%{keyword}%", f"%{keyword}%"))
    search_results = c.fetchall()
    if not search_results:
        print("No matching records found\n")
    else:
        print("\nSearch Results:\n")
        for index, entry in enumerate(search_results):
            place_name, address, timestamp = entry
            print("Place Name:", place_name)
            print("Address:", address)
            print("Timestamp:", timestamp)
            if index < len(search_results) - 1:
                print("-" * 20)
            else:
                print()
    time.sleep(0.65)


def save_search_history(c, conn, user_id, results):
    for result in results:
        place_name = result["name"]
        address = result["location"]["formatted_address"]
        c.execute("INSERT INTO search_history (user_id, place_name, address) "
                  "VALUES (?, ?, ?)", (user_id, place_name, address))
    conn.commit()