from getpass import getpass
from mysql.connector import connect, Error

class MysqlCMD:
    def __init__(self, connection, cursor) -> None:
        self.connection = connection
        self.cursor = cursor

    def createStaff(self) -> None:
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
        record = (macId, firstName, lastName, department)
        query: str = "INSERT INTO staff VALUES (%s, %s, %s, %s);"
        self.cursor.execute(query, record)
        self.connection.commit()

        self.cursor.execute("SELECT * FROM staff WHERE macId = %s;", (macId,))
        results = self.cursor.fetchall()
        for result in results:
            print(result)
        return record[0]
                
    def createComp(self) -> None:
        items = ["Host name", "Brand", "Model", "SN", "Purchase Date", "Warranty Date"]
        record = tuple([input(f"{item}: ") for item in items])
        query = "INSERT INTO comp VALUES (%s, %s, %s, %s, %s, %s)"
        self.cursor.execute(query, record)
        self.connection.commit()

        self.cursor.execute("SELECT * FROM comp WHERE hostName = %s;", (record[0],))
        results = self.cursor.fetchall()
        for result in results:
            print(result)
        return record[0]
    
    def checkStaff(self, macId):
        query = "SELECT * FROM staff WHERE macId = %s OR firstName = %s OR lastName = %s;"
        self.cursor.execute(query, (macId,macId, macId))
        result = self.cursor.fetchall()
        return len(result) == 1
    
    def checkComp(self, hostName):
        query = "SELECT * FROM comp WHERE hostName = %s"
        self.cursor.execute(query, (hostName,))
        result = self.cursor.fetchall()
        return len(result) == 1

    
    def createAssign(self):
        hostName = input("host name: ")
        while not self.checkComp(hostName):
            answer: str = input(f"machine of host name {hostName} not found, would you like to create first? [y/n]")
            if (answer.lower() == 'n'):
                raise Exception("host name not found, cannot assign unknown machine")
            elif(answer.lower() == 'y'):
                hostName = self.createComp()
            else:
                print("invalid answer")
                continue
        macId = input("macId: ")
        while not self.checkStaff(macId):
            answer: str = input(f"staff of macId {hostName} not found, would you like to create first? [y/n]")
            if (answer.lower() == 'n'):
                raise Exception("macId not found, cannot assign to unknown staff")
            elif(answer.lower() == 'y'):
                macId = self.createStaff()
            else:
                print("invalid answer")
                continue

        date = input("date assigned: ")
        command = "INSERT INTO comptostaff VALUES (%s, %s, %s)"
        record = (hostName, macId, date)
        self.cursor.execute(command, record)
        self.connection.commit()

        query = "SELECT * FROM comptostaff WHERE hostName = %s AND macId = %s"
        self.cursor.execute(query, (hostName, macId))
        results = self.cursor.fetchall()
        for result in results:
            print(result)
        return (hostName, macId)
        



def main():
    try:
        with connect(
            host="localhost",
            user = "root",
            password = "R05yste3Ad31n",
            database = "rodevices"
        ) as connection:
            with connection.cursor() as cursor:

                cmd = MysqlCMD(connection, cursor)
                cmd.createAssign()



    except Error as e:
        print(e)


if __name__ == "__main__":
    main()