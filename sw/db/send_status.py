import time
import socket
import sqlite3
from sqlite3 import Error

from azure.data.tables import TableServiceClient, TableClient, UpdateMode
from azure.core.credentials import AzureNamedKeyCredential
from azure.core.exceptions import ResourceExistsError

from datetime import datetime

PRODUCT_ID = u'ball detect'
PRODUCT_NAME = u'Ball'

def getHostIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('1.1.1.1', 1))
    local_ip = s.getsockname()[0]
    return local_ip

class Ball:
    __moab_local_ip = None
    __local_ip = None
    __product = None
    __status_of_ball = None
    __ball = None

    def __init__(self) -> None:
        self.__local_ip = getHostIP()
        self.__moab_local_ip = str(self.__local_ip).replace(".", "")
        self.__product = u'ball detect'
        self.__status_of_ball = False
        self.__ball = {
            u'PartitionKey': self.__moab_local_ip,
            u'RowKey': self.__product,
            u'IP': self.__local_ip,
            u'STATUS': self.__status_of_ball
        }

    def getEntity(self, status_of_ball):
        self.__ball["STATUS"] = status_of_ball
        return self.__ball

class Send:
    __connection_string = None
    __table_service_client = None
    __table_name = None

    def __init__(self) -> None:
        self.__table_name = "BALL"
        self.__connection_string = "DefaultEndpointsProtocol=https;EndpointSuffix=core.windows.net;AccountName=moabseziuzmtc;AccountKey=nnQ2NJWQt8JAtU2mJNQ2+9SvpxatO3qvAo+4xIQRCPYycX5S+UlwF6c5awf743UXvKxmcstQZ3kGdFLJs5bIcw=="
        self.__table_service_client = TableServiceClient.from_connection_string(conn_str=self.__connection_string).get_table_client(table_name=self.__table_name)
    
    def sendStatusOfBall(self, ball):
        try:
            self.__table_service_client.update_entity(mode=UpdateMode.MERGE, entity=ball)
        except ResourceExistsError as e:
            print (e)
    
    def createRow(self, ball):
        try:
            entity = self.__table_service_client.create_entity(entity=ball)
        except ResourceExistsError as e:
            print(e)
        
def create_connection(db_file):
    """ create a database connection to a SQLite database """

    conn = None

    send = Send()
    ball = Ball()

    status_of_ball = ball.getEntity(False)
    send.createRow(status_of_ball)

    old_status_of_ball = None

    while True:
        try:
            statusOfBall = sqlite3.connect(db_file).execute("SELECT status from BALL").fetchone()[0]
            if old_status_of_ball != statusOfBall:
                if statusOfBall == "1":
                    status_of_ball = ball.getEntity(True)
                else:
                    status_of_ball = ball.getEntity(False)
                send.sendStatusOfBall(status_of_ball)
                old_status_of_ball = statusOfBall

        except Error as e:
            print(e)

        finally:
            if conn:
                conn.close()

        time.sleep(1)
                
if __name__ == '__main__':
    create_connection(r"/home/pi/moab/sw/db/ball.db")
