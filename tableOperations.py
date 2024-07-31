from getpass import getpass
from mysql.connector import connect, Error



try:
    with connect(
        host="localhost",
        user = "root",
        password = "R05yste3Ad31n",
        database = "rodevices"
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM staff;")
            results = cursor.fetchall()
            for result in results:
                print(result)



except Error as e:
    print(e)