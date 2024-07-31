from getpass import getpass
from mysql.connector import connect, Error

try:
    with connect(
        host="localhost",
        user=input("ener username: "),
        password = getpass("enter password: "),
    ) as connection:
        print(connection)

except Error as e:
    print(e)