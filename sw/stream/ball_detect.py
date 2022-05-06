import sqlite3
from sqlite3 import Error

class ball_detected:
    ball_status: bool = False

    def ball_is(ball):
        if ball_detected != ball:
            ball_detected.ball_status = ball
            conn = sqlite3.connect(r"/home/pi/moab/sw/db/ball.db")
            if ball:
                try:
                    conn.execute("UPDATE BALL set STATUS = True where ID = 1")
                    conn.commit()
                except Error as e:
                    print(e)
                finally:
                    if conn:
                        conn.close()
            else:
                try:
                    conn.execute("UPDATE BALL set STATUS = False where ID = 1")
                    conn.commit()
                except Error as e:
                    print(e)
                finally:
                    if conn:
                        conn.close()
        
                
