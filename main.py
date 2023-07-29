import sqlite3
import time

import core_utils
import database_utils

conn = sqlite3.connect("destination_finder.db")
c = conn.cursor()
database_utils.create_tables(c)

print("Destination Finder")
print("+-+-+-+-+-+-+-+-+-\n")

print("This destination finder shows tourist destinations in your chosen area")
print("For best results, enter zipcode or postcode followed by country name")
print("Example: 12345 United States of America")

time.sleep(0.65)

while True:

    user_id = None

    print("\n------------------\n")

    print("1: Guest Search")
    print("2: Login")
    print("3: Sign Up")
    print("Q: Quit")

    option = input("\nChoose an option: ")

    if option == "1":

        try:
            core_utils.search(c, conn)
        except TypeError:
            pass

    elif option == "2":

        user_id = database_utils.login(c)

        if user_id is not None:

            print()

            while True:
                print("------------------\n")
                print("1: Search")
                print("2: View Search History")
                print("3: Delete Account")
                print("Q: Return to Main Menu")
                sub_option = input("\nChoose an option: ")

                if sub_option == "1":

                    try:
                        core_utils.search(c, conn, user_id)
                    except TypeError:
                        pass

                elif sub_option == "2":

                    if database_utils.check_search_history(c, user_id):
                        time.sleep(0.65)
                        print("\n------------------\n")

                        while True:
                            print("1: View All Searches")
                            print("2: View Popular Searches")
                            print("3: Search For Record")
                            print("Q: Return to User Menu")
                            search_option = input("\nChoose an option: ")

                            if search_option == "1":
                                database_utils.print_search_history(c, user_id)

                            elif search_option == "2":
                                database_utils.print_most_popular_searches(
                                    c, user_id)

                            elif search_option == "3":
                                keyword = core_utils.get_keyword()
                                database_utils.search_history(
                                    c, user_id, keyword)

                            elif search_option.upper() == "Q":
                                print()
                                time.sleep(0.65)
                                break

                            else:
                                print("\nError: choose a valid option")
                                time.sleep(0.65)

                    else:
                        print("\nSearch history is empty\n")
                        time.sleep(0.65)

                elif sub_option == "3":
                    database_utils.delete_user(c, conn, user_id)
                    break

                elif sub_option.upper() == "Q":
                    time.sleep(0.65)
                    break

                else:
                    print("\nError: choose a valid option\n")
                    time.sleep(0.65)

    elif option == "3":

        while True:

            username, password = core_utils.signup()
            c.execute("SELECT username FROM users WHERE username=?",
                      (username,))

            if c.fetchone():
                print("\nError: sername already exists - try another")
            else:
                c.execute("INSERT INTO users (username, password) "
                          "VALUES (?, ?)", (username, password))
                conn.commit()
                print("\nAccount created successfully!")
                time.sleep(0.65)
                break

    elif option.upper() == "Q":
        break

c.close()
conn.close()
print("\nThank you for using Destination Finder!")
