import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """ create a database connection to a SQLite database """

    conn = None

    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)

    # try:
    #     conn.execute('''CREATE TABLE BALL
    #                 (ID INT PRIMARY KEY     NOT NULL,
    #                 NAME            TEXT    NOT NULL,
    #                 STATUS          TEXT    NOT NULL);''')
    #     print("Table created sucsessfully")
    # except Error as e:
    #     print(e)

    # try:
    #     conn.execute("INSERT INTO BALL (ID,NAME,STATUS) \
    #         VALUES (1, 'ball', 'here')")
    #     conn.commit()
    #     print("Record status saccessfully")
    # except Error as e:
    #     print(e)

    try:
        conn.execute("UPDATE BALL set STATUS = True where ID = 1")
        conn.commit()
    except Error as e:
        print(e)
   

    try:
        cursor = conn.execute("SELECT id, name, status from BALL")
        for row in cursor:
            print ("ID = ", row[0])
            print ("NAME = ", row[1])
            print ("STATUS = ", row[2])
        print("Operation done successfully")
    except Error as e:
        print(e)

    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    create_connection(r"ball.db")
