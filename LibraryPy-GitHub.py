import pyodbc # Connects to a SQL database using pyodbc
import uuid
# Connect to the database.
def connect_to_database():
    print("---- Connecting to the Library Server ----")
    # Please obtain the credentials for the database.
    connection_data = (
        "Driver = {SQL Server};"
        "Server = HostName/IP;"
        "Database = your DataBase;"
    )
    try:
        connection = pyodbc.connect(connection_data)
        print("\n---- Connection Successful ----")
        return connection.cursor()
    except pyodbc.Error as e:
        print("Error connecting to the database:", e)
        return None
# Step 1 - List all books in the library.
def list_books(cursor):
    print("List of books in the Library")
    try:
        cursor.execute("SELECT title, author FROM library")
        books = cursor.fetchall()
        for index, book in enumerate(books, start=1):
            print(index, "-", "\n--- Title:", book[0], "\n--- Author:", book[1])
    except pyodbc.Error as e:
        print("Error listing books:", e)
# Step 2 - Check the availability of a book in the library.
def check_availability(cursor):
    title = input("Enter the Book Title: ").lower()
    try:
        cursor.execute("SELECT title, availability FROM library WHERE LOWER(title) = ?", (title,))
        book = cursor.fetchone()
        if book:
            if book[1].lower() == "yes":
                print(f"\nThe book '{book[0]}' is available.")
            else:
                print(f"\nThe book '{book[0]}' is not available at the moment.")
        else:
            print(f"\nThe book '{title}' is not registered in the library.")
    except pyodbc.Error as e:
        print("Error checking availability:", e)
# Step 3 - Allow a student to reserve a book.
def reserve_book(cursor):
    name = input("Enter the student's full name: ").lower()
    try:
        cursor.execute("SELECT id, name FROM users WHERE LOWER(name) = ?", (name,))
        student = cursor.fetchone()
        if student:
            student_id = student[0]
        else:
            student_id = str(uuid.uuid4())
            cursor.execute("INSERT INTO users (id, name) VALUES (?, ?)", (student_id, name))
            cursor.connection.commit()
            print(f"\nThe student {name} has been successfully registered.")
    except pyodbc.Error as e:
        print("Error registering user:", e)
        return

    book_title = input("\nEnter the Title of the Book you want to reserve: ").lower()
    try:
        cursor.execute("SELECT title, availability FROM library WHERE LOWER(title) = ?", (book_title,))
        book = cursor.fetchone()
        if book:
            if book[1].lower() == "yes":
                cursor.execute("UPDATE library SET availability = 'no' WHERE LOWER(title) = ?", (book_title,))
                cursor.connection.commit()
                cursor.execute("INSERT INTO reservations (id, book) VALUES (?, ?)", (student_id, book[0]))
                cursor.connection.commit()
                print(f"\nThe book '{book_title}' has been successfully reserved.")
            else:
                print(f"\nThe book '{book[0]}' is not available for reservation at the moment.")
        else:
            print(f"\nThe book '{book_title}' is not registered in the library.")
    except pyodbc.Error as e:
        print("Error reserving book:", e)
# Step 4 - Allow a student to return a reserved book.
def return_book(cursor):
    name = input("Enter the student's full name: ").lower()
    try:
        cursor.execute("SELECT id, name FROM users WHERE LOWER(name) = ?", (name,))
        student = cursor.fetchone()
        if student:
            student_id = student[0]
            book_title = input("\nEnter the Title of the Book you want to return: ").lower()
            try:
                cursor.execute("SELECT id, book FROM reservations WHERE id = ? AND LOWER(book) = ?", (student_id, book_title))
                book = cursor.fetchone()
                if book:
                    cursor.execute("UPDATE library SET availability = 'yes' WHERE LOWER(title) = ?", (book_title,))
                    cursor.connection.commit()
                    cursor.execute("DELETE FROM reservations WHERE id = ? AND LOWER(book) = ?", (student_id, book_title))
                    cursor.connection.commit()
                    print(f"\nThe book '{book[1]}' has been successfully returned to the library.")
                else:
                    print(f"\nThe book '{book_title}' is not reserved by the student {name}.")
            except pyodbc.Error as e:
                print("Error returning book:", e)
        else:
            print(f"\nThe student {name} is not registered in the system.")
    except pyodbc.Error as e:
        print("Error querying database:", e)
# Step 5 - Add a new book to the library.
def add_book(cursor):
    title = input("Enter the Book Title: ").lower()
    author = input("Enter the Author's Name: ").lower()
    while True:
        availability = input("Is the Book available? (Yes/No): ").lower()
        if availability in ["yes", "no"]:
            break
        else:
            print("Please enter 'Yes' or 'No'.")
    date = input("Enter today's date (DD/MM/YYYY): ")
    try:
        cursor.execute(
            "INSERT INTO library (title, author, availability, date_add) VALUES (?, ?, ?, ?)",
            (title, author, availability, date)
        )
        cursor.connection.commit()
        print(f"\nThe Book '{title}' has been successfully added!")
    except pyodbc.Error as e:
        print("Error adding book:", e)
# Step 6 - Remove a book from the library.
def remove_book(cursor):
    title = input("Enter the Title of the book to be removed: ").lower()
    try:
        cursor.execute("SELECT title FROM library WHERE LOWER(title) = ?", (title,))
        book = cursor.fetchone()
        if book:
            cursor.execute("DELETE FROM library WHERE LOWER(title) = ?", (title,))
            cursor.connection.commit()
            print(f"\nThe book '{book[0]}' has been successfully removed from the library.")
        else:
            print(f"\nThe book '{title}' is not registered in the library.")
    except pyodbc.Error as e:
        print("Error removing book:", e)
# Step 0 - Display the menu and manage user options.
def menu():
    cursor = connect_to_database()
    if not cursor:
        return
    while True:
        print("\nMenu: ")
        print("1. List Books")
        print("2. Check Availability")
        print("3. Reserve Book")
        print("4. Return Book")
        print("5. Add Book")
        print("6. Remove Book")
        print("0. Exit")
        option = input("Enter the number of the desired option: ")
        if option == '1':
            list_books(cursor)
        elif option == '2':
            check_availability(cursor)
        elif option == '3':
            reserve_book(cursor)
        elif option == '4':
            return_book(cursor)
        elif option == '5':
            add_book(cursor)
        elif option == '6':
            remove_book(cursor)
        elif option == '0':
            print("Exiting the Program...")
            break
        else:
            print("\nInvalid option. Please try again and choose a valid option.")
# Start the program
menu()

#References:
#https://mayurbirle.medium.com/uuids-with-python-b133cead1b4c
#https://learn.microsoft.com/pt-br/sql/connect/python/pyodbc/python-sql-driver-pyodbc?view=sql-server-ver16