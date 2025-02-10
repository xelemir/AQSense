import datetime
from sensor import SDS011
from sql_connector import SqlConnector
from push_notification import send
import time
from config import *
from threading import Thread
import requests

if __name__ == "__main__":
    sql = SqlConnector("database.db")
    sds011 = SDS011("/dev/ttyUSB0")
    
    while True:
        if SLEEP_HOURS_START is not None and SLEEP_HOURS_END is not None:
            start = datetime.datetime.strptime(SLEEP_HOURS_START, "%H:%M").time()
            end = datetime.datetime.strptime(SLEEP_HOURS_END, "%H:%M").time()
            current_time = datetime.datetime.now().time()
            
            if current_time >= start or current_time < end:
                sds011.sleep()
                time.sleep(60)
                continue
        
        sds011.sleep(sleep=False)
        time.sleep(15)
        result = sds011.query()
        sds011.sleep()
        
        if result is not None:
            pm25, pm10 = result
            
            avg_last = sql.get_avg_last_particles(4, 2)
            if avg_last[0] is not None:
                avg_pm25 = avg_last[0]
                if pm25 - avg_pm25 > 3.5 and sql.get_last_marker_within(4) is None and sql.get_last_particle(5) is not None:

                    if PUSH_NOTIFICATIONS:
                        # Send push notification
                        Thread(
                            target=requests.post, 
                            args=("https://www.gruettecloud.com/sendpush",), 
                            kwargs={
                                "json": {
                                    "title": "Pollution Alert",
                                    "message": f"The PM2.5 level has just spiked to {pm25} µg/m³. AVG: {round(avg_pm25, 1)} µg/m³. Difference: {round(pm25 - avg_pm25, 1)} µg/m³.",
                                    "authenticity_key": PUSH_KEY
                                },
                                "headers": {"Content-Type": "application/json"}
                            }
                        ).start()
                        
                    sql.insert_marker()
                    
            sql.insert_particles(pm25, pm10)
        else:
            print("Failed to read data from the sensor.")
        time.sleep(20)