from getpass import getpass
from mysql.connector import connect, Error
from datetime import datetime
import re



class MysqlCMD:
    def __init__(self, connection, cursor) -> None:
        self.connection = connection
        self.cursor = cursor
        self.dateFormat: str = "yyyy-mm-dd"

    def checkStaff(self, macId) -> bool:
        query = "SELECT * FROM staff WHERE macId = %s"
        self.cursor.execute(query, (macId,))
        result = self.cursor.fetchall()
        return len(result) == 1
    
    def checkComp(self, hostName) -> bool:
        query = "SELECT * FROM comp WHERE hostName = %s"
        self.cursor.execute(query, (hostName,))
        result = self.cursor.fetchall()
        return len(result) == 1

    def inputDate(self, occasion: str, allowEnterToday: bool):
        msg: str
        if allowEnterToday:
            msg = f"{occasion} <{self.dateFormat}>, <enter> for today: "
        else:
            msg = f"{occasion} <{self.dateFormat}>: "
        date: str = input(msg)

        date.strip()
        pattern = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}')

        while True:
            
            if(allowEnterToday and date == ''):
                date = datetime.today().strftime('%Y-%m-%d')
                break
            elif (len(date) == len(self.dateFormat) and pattern.match(date)):
                break
            date: str = input(f"date formate error! {occasion} <{self.dateFormat}>, <enter> for today: ")
            date.strip()
        return date
        

    def inputCreateStaff(self):
        macId: str = input("macID: ")
        firstName: str = input("First Name: ")
        lastName: str = input("Last Name: ")
        depts: list[str] = ["admissions", "aid and awards", "central office", "communications", "records", "recruitment", "ROIT inventory", "scheduling and exams", "student services", "systems", "UTS inventory"]
        for i, dept in enumerate(depts):
            print(f"{i} : {dept}")
        deptI: int = int(input("department: "))
        while deptI < 0 or deptI >= len(depts):
            deptI: int = int(input("invalid choice, pick the number that correspond to a department.\ndepartment: "))
        
        department: str = depts[deptI]

        record = (macId, firstName, lastName, department)
        return record

    def createStaff(self, record) -> str:

        macId = record[0]
        if self.checkStaff(macId):
            print("a user with same macId already exists!")
        else:
            command: str = "INSERT INTO staff VALUES (%s, %s, %s, %s);"
            self.cursor.execute(command, record)
            self.connection.commit()

        self.cursor.execute("SELECT * FROM staff WHERE macId = %s;", (macId,))
        results = self.cursor.fetchall()
        for result in results:
            print(result)
        return macId
    
    def inputCreateComp(self):
        nonDateItems = ["Host name", "Brand", "Model", "SN"]

        record = tuple([input(f"{item}: ") for item in nonDateItems] + [self.inputDate("purchase date", False), self.inputDate("warranty expire date", False)])
        return record

    def createComp(self, record) -> None:
        hostName = record[0]
        if self.checkComp(hostName):
            print(f"a computer with host name {hostName} already exists")
        else:
            command = "INSERT INTO comp VALUES (%s, %s, %s, %s, %s, %s)"
            self.cursor.execute(command, record)
            self.connection.commit()

        self.cursor.execute("SELECT * FROM comp WHERE hostName = %s;", (hostName,))
        results = self.cursor.fetchall()
        for result in results:
            print(result)

        commandCreateCurrent = "INSERT INTO currentCompToStaff VALUES (%s, %s, %s)"
        commandCreateHistory = "INSERT INTO compToStaff VALUES (%s, %s, %s)"
        self.cursor.execute(commandCreateCurrent, (record[0], "UTS_SPARE", datetime.today().strftime('%Y-%m-%d')))
        self.cursor.execute(commandCreateHistory, (record[0], "UTS_SPARE", datetime.today().strftime('%Y-%m-%d')))
        self.connection.commit()
        return record[0]
    


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

        date = self.inputDate("assignment date", True)
        return (hostName, macId, date)

    def createAssign(self, record):
        hostName = record[0]
        macId = record[1]
        assignedDate = record[2]
        commandHistory = "INSERT INTO comptostaff VALUES (%s, %s, %s)"
        self.cursor.execute(commandHistory, record)

        commandCurrent = "UPDATE currentCompToStaff SET macId = %s, assignedDate = %s WHERE hostName = %s"
        self.cursor.execute(commandCurrent, (macId, assignedDate, hostName))

        self.connection.commit()


        query = "SELECT * FROM comptostaff WHERE hostName = %s AND macId = %s"
        self.cursor.execute(query, (hostName, macId))
        results = self.cursor.fetchall()
        print("assignment sucessful:")
        for result in results:
            print(result)
        return (record[0], record[1])
    
    def getCurrentSheet(self):
        query = """
        SELECT comp.*, staff.*
        FROM currentCompToStaff AS cts
        LEFT JOIN comp ON comp.hostName = cts.hostName
        LEFT JOIN staff ON staff.macId = cts.macId
        """

        self.cursor.execute(query)
        results = self.cursor.fetchall()
        for result in results:
            print(result)

        return results
        
    def inputRetrieveComp(self):
        hostName = input("host name: ")
        while not self.checkComp(hostName):
            hostName = input(f"machine with host name {hostName} doesn't exist, try again: ")

        date = self.inputDate("retrieve date", True)
        return (hostName, "UTS_SPARE", date)

    def retrieveComp(self, record):
        hostName = record[0]
        macId = record[1]
        date = record[2]

        commandHistory = "INSERT INTO comptostaff VALUES (%s, %s, %s)"
        self.cursor.execute(commandHistory, record)

        commandCurrent = "UPDATE currentCompToStaff SET macId = %s, asssignedDate = %s WHERE hostName = %d"
        self.cursor.execute(commandCurrent, (macId, date, hostName))

        self.connection.commit()

        self.cursor.execute("SELECT * FROM currentComptostaff AS cts WHERE cts.hotsName = %s AND cts.date = %s", (hostName, date))
        results = self.cursor.fetchall()
        for result in results:
            print(result)
        return 0
    
    def inputCreateProblem(self):
        hostName: str = input("host name: ")
        while not self.checkComp(hostName):
            hostName = input(f"no computer with host name {hostName} exists, try again\nhost name: ")
        problem: str = input("problem: ")
        problemDate = self.inputDate("problem date", True)
        record = (hostName, problem, problemDate)
        return record
    
    def createProblem(self, record):
        hostName = record[0]
        problem = record[1]
        command = "INSERT INTO problem(hostName, problem, problemDate) VALUES (%s, %s, %s)"
        self.cursor.execute(command, record)
        self.connection.commit()

        self.cursor.execute("SELECT * FROM problem WHERE hostName = %s AND problem = %s", (hostName, problem))
        result = self.cursor.fetchall()
        print(result[0])
        return 0

    
    def shortCommand(self):
        while True:
            command: str = input("=> ").lower()
            if "add staff" == command:
                self.createStaff(self.inputCreateStaff())
            elif "add comp" == command:
                self.createComp(self.inputCreateComp())
            elif "add problem" == command:
                self.createProblem(self.inputCreateProblem())
            elif "assign" == command:
                self.createAssign(self.inputCreateAssign())
            elif "current" == command:
                self.getCurrentSheet()
            elif "select" in command:
                self.cursor.execute(command)
                results = self.cursor.fetchall()
                for result in results:
                    print(result)
            elif "update" in command:
                if not "where" in command:
                    print("udpate is not specified with WHERE clause, dangerouse")
                else:
                    self.cursor.execute(command)
                    self.connection.commit()
            else:
                print("unrecognized command, try again")


    


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