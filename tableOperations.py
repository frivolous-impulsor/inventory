from getpass import getpass
from mysql.connector import connect, Error

class MysqlCMD:
    def __init__(self) -> None:
        pass

    def createStaff(self):
        firstName: str = input("First Name: ")
        lastName: str = input("Last Name: ")
        macId: str = input("macID: ")
        print("1: Aids Awards\n2: Systems\n3: Admission")
        departmentEnum: int = int(input("department: "))
        department: str
        fitDepart = False
        while not fitDepart:
            match departmentEnum:
                case 1:
                    department = "aids awards"
                    fitDepart = True
                case 2:
                    department = "Systems"
                    fitDepart = True
        record = (firstName, lastName, macId, department)
        query: str = "INSERT INTO staff VALUES (%s, %s, %s, %s);"
        return (query, record)
                
    def createComp(self):
        items = ["Host name", "Brand", "Model", "SN", "Purchase Date", "Warranty Date"]
        record = tuple([input(f"{item}: ") for item in items])
        query = "INSERT INTO comp VALUES (%s, %s, %s, %s, %s, %s)"
        return (query, record)
    
    def checkStaff(self, macId, cursor):
        query = "SELECT * FROM staff WHERE staff.macId = %s"
        cursor.executemany(query, [(macId,)])
        result = cursor.fetchall()
        print(result)
        return len(result) == 1

    
    def createAssign(self):
        items = ["Host name", "macID", "assignedDate"]
        record = tuple([input(f"{item}: ") for item in items])
        query = "INSERT INTO compToStaff VALUES (%s, %s, %s)"
        return (query, record)

def main():
    try:
        with connect(
            host="localhost",
            user = "root",
            password = "R05yste3Ad31n",
            database = "rodevices"
        ) as connection:
            with connection.cursor() as cursor:

                cmd = MysqlCMD()
                #query = cmd.createAssign()
                #cursor.executemany(query[0], [query[1]])
                #connection.commit()
                exist = cmd.checkStaff("wayneb", cursor)
                print(exist)
                print("committed")
                results = cursor.fetchall()
                for result in results:
                    print(result)

    except Error as e:
        print(e)


if __name__ == "__main__":
    main()