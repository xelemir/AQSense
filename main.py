import datetime
from sensor import SDS011
from sql_connector import SqlConnector
from push_notification import send
import time
from config import *

if __name__ == "__main__":
    sql = SqlConnector("database.db")
    sds011 = SDS011("/dev/ttyUSB0")
    
    
    while True:
        if SLEEP_HOURS_START is not None and SLEEP_HOURS_END is not None:
            current_time = datetime.datetime.now().time()
            if current_time >= SLEEP_HOURS_START or current_time < SLEEP_HOURS_END:
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

                    # Pollution spike detected, log and send notification if possible
                    if PUSH_NOTIFICATIONS is True:
                        try:
                            send(
                                title="Pollution Spike Detected!",
                                message=f"The PM2.5 level has just spiked to {pm25} µg/m³. AVG: {round(avg_pm25, 1)} µg/m³. Difference: {round(pm25 - avg_pm25, 1)} µg/m³.",
                                endpoint=PUSH_ENDPOINT,
                                p256dh=PUSH_P256DH,
                                auth=PUSH_AUTH,
                                vapid_private=PUSH_VAPID_PRIVATE_KEY,
                                email=PUSH_EMAIL
                            )
                        except Exception as e:
                            print(f"Failed to send push notification: {e}")
                    
                    sql.insert_marker()
                    
            sql.insert_particles(pm25, pm10)
        else:
            print("Failed to read data from the sensor.")
        time.sleep(20)