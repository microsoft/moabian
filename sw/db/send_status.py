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

class ball_detected:
    ball_status = None

    IP = getHostIP()
    PRODUCT_ID = u'ball detect'
    PRODUCT_NAME = str(IP).replace(".", "")

    my_entity = {
        u'PartitionKey': PRODUCT_NAME,
        u'RowKey': PRODUCT_ID,
        u'IP': IP,
        u'STATUS': False
    }

    replaced = {
        u'PartitionKey': PRODUCT_NAME,
        u'RowKey': PRODUCT_ID,
        u'IP': IP,
        u'STATUS': False
    }

    connection_string = "DefaultEndpointsProtocol=https;EndpointSuffix=core.windows.net;AccountName=moabseziuzmtc;AccountKey=nnQ2NJWQt8JAtU2mJNQ2+9SvpxatO3qvAo+4xIQRCPYycX5S+UlwF6c5awf743UXvKxmcstQZ3kGdFLJs5bIcw=="
    
    my_filter = "PartitionKey eq '{}'".format(PRODUCT_NAME)
    table_service_client = TableServiceClient.from_connection_string(conn_str=connection_string)
    table_client = table_service_client.get_table_client(table_name="BALL")
        
def create_connection(db_file):
    """ create a database connection to a SQLite database """

    conn = None

    connection_string = "DefaultEndpointsProtocol=https;EndpointSuffix=core.windows.net;AccountName=moabseziuzmtc;AccountKey=nnQ2NJWQt8JAtU2mJNQ2+9SvpxatO3qvAo+4xIQRCPYycX5S+UlwF6c5awf743UXvKxmcstQZ3kGdFLJs5bIcw=="
    table_service_client = TableServiceClient.from_connection_string(conn_str=connection_string)
    table_client = table_service_client.get_table_client(table_name="BALL")

    try:
        entity = ball_detected.table_client.create_entity(entity=ball_detected.my_entity)
    except ResourceExistsError as e:
        print(e)

    # finally:
    #     if conn:
    #         conn.close()

    while True:
        try:
            statusOfBall = sqlite3.connect(db_file).execute("SELECT status from BALL").fetchone()[0]
            # cursor = conn.execute("SELECT status from BALL")
            if statusOfBall == "1":
                ball_detected.replaced["STATUS"] = True
            else:
                ball_detected.replaced["STATUS"] = False
            ball_detected.table_client.update_entity(mode=UpdateMode.MERGE, entity=ball_detected.replaced)

            time.sleep(1)
        except Error as e:
            print(e)

        finally:
            if conn:
                conn.close()

                
if __name__ == '__main__':
    create_connection(r"/home/pi/moab/sw/db/ball.db")
