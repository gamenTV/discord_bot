import mysql.connector


class Database:
    def __init__(self):
        try:
            self.database = mysql.connector.connect(
                host="192.167.178.152",
                user="discord",
                password="V8a952a2;",
                database=""
            )
        except:
            print("Connection Failed!")

    def check_con(self):
        return self.database.is_connected()
