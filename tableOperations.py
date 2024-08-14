from getpass import getpass
from mysql.connector import connect, Error


class MysqlCMD:
    def __init__(self, connection, cursor) -> None:
        self.connection = connection
        self.cursor = cursor

    def inputCreateStaff(self):
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
        return record

    def createStaff(self, record) -> None:


        command: str = "INSERT INTO staff VALUES (%s, %s, %s, %s);"
        self.cursor.execute(command, record)
        self.connection.commit()

        self.cursor.execute("SELECT * FROM staff WHERE macId = %s;", (record[0],))
        results = self.cursor.fetchall()
        for result in results:
            print(result)
        return record[0]
    
    def inputCreateComp(self):
        items = ["Host name", "Brand", "Model", "SN", "Purchase Date", "Warranty Date"]
        record = tuple([input(f"{item}: ") for item in items])
        return record

    def createComp(self, record) -> None:
        command = "INSERT INTO comp VALUES (%s, %s, %s, %s, %s, %s)"
        self.cursor.execute(command, record)
        self.connection.commit()

        self.cursor.execute("SELECT * FROM comp WHERE hostName = %s;", (record[0],))
        results = self.cursor.fetchall()
        for result in results:
            print(result)
        return record[0]
    
    def checkStaff(self, macId) -> bool:
        query = "SELECT * FROM staff WHERE macId = %s OR firstName = %s OR lastName = %s;"
        self.cursor.execute(query, (macId,macId, macId))
        result = self.cursor.fetchall()
        return len(result) == 1
    
    def checkComp(self, hostName) -> bool:
        query = "SELECT * FROM comp WHERE hostName = %s"
        self.cursor.execute(query, (hostName,))
        result = self.cursor.fetchall()
        return len(result) == 1

    def inputCreateAssign(self):
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
            answer: str = input(f"staff of macId {macId} not found, would you like to create first? [y/n]")
            if (answer.lower() == 'n'):
                raise Exception("macId not found, cannot assign to unknown staff")
            elif(answer.lower() == 'y'):
                macId = self.createStaff()
            else:
                print("invalid answer")
                continue

        date = input("date assigned: ")
        return (hostName, macId, date)

    def createAssign(self, record):
        
        command = "INSERT INTO comptostaff VALUES (%s, %s, %s)"
        self.cursor.execute(command, record)
        self.connection.commit()

        query = "SELECT * FROM comptostaff WHERE hostName = %s AND macId = %s"
        self.cursor.execute(query, (record[0], record[1]))
        results = self.cursor.fetchall()
        for result in results:
            print(result)
        return (record[0], record[1])
    
    def getCurrentSheet(self):
        earlierAssignment = """
        SELECT cts1.hostName, cts1.macId
        FROM comptostaff AS cts1, comptostaff AS cts2
        WHERE cts1.hostName = cts2.hostName AND cts1.assignedDate < cts2.assignedDate
        """

        laterAssignment = f"""
        SELECT comp.*, cts3.assignedDate, staff.*
        FROM comptostaff AS cts3
        LEFT JOIN staff ON staff.macId = cts3.macId
        LEFT JOIN comp ON comp.hostName = cts3.hostName
        WHERE (cts3.hostName, cts3.macId) NOT IN ({earlierAssignment})
        """

        self.cursor.execute(laterAssignment)
        results = self.cursor.fetchall()
        for result in results:
            print(result)

        return len(results)
        
    def inputRetrieveComp(self):
        hostName = input("host name: ")
        if not self.checkComp(hostName):
            raise Exception(f"machine with host name {hostName} doesn't exist")
        date = input("retrieve date: ")
        return (hostName, "UTS_SPARE", date)

    def retrieveComp(self, record):
        command = "INSERT INTO comptostaff VALUES (%s, %s, %s)"
        self.cursor.execute(command, record)
        self.connection.commit()

        self.cursor.execute("SELECT * FROM comptostaff AS cts WHERE cts.hotsName = %s AND cts.date = %s", (record[0], record[2]))
        results = self.cursor.fetchall()
        for result in results:
            print(result)
        return 0
    
    def shortCommand(self):
        command: str = input("=>").lower()
        if "create staff" in command:
            self.createStaff(self.inputCreateStaff())
        elif "create comp" in command:
            self.createComp(self.inputCreateComp())
        elif "assign" in command:
            self.createAssign(self.inputCreateAssign())
        elif "current" in command:
            self.getCurrentSheet()
        elif "select" in command:
            self.cursor.execute(command)
            results = self.cursor.fetchall()
            for result in results:
                print(result)
        else:
            raise Exception("unrecognized command")


    


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
                cmd.shortCommand()




    except Error as e:
        print(e)


if __name__ == "__main__":
    main()