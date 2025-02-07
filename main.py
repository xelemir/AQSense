from sensor import SDS011
from sql_connector import SqlConnector
from push_notification import send
import time

try:
    from push_secrets import *
except ImportError:
    endpoint, p256dh, auth, vapid_private, email = None, None, None, None, None
    print("Starting without push notification support.")

if __name__ == "__main__":
    sql = SqlConnector("database.db")
    sds011 = SDS011("/dev/ttyUSB0")
    
    
    while True:
        sds011.sleep(sleep=False)
        time.sleep(15)
        result = sds011.query()
        sds011.sleep()
        
        if result is not None:
            pm25, pm10 = result
            
            avg_last = sql.get_avg_last_particles(10, 4)
            if avg_last is not None:
                avg_pm25 = avg_last[0]
                if pm25 - avg_pm25 > 3 and sql.get_last_marker_within(3) is None and sql.get_last_particle(5) is not None:

                    # Pollution spike detected, log and send notification if possible
                    if endpoint is not None:
                        try:
                            send(
                                title="Pollution Spike Detected!",
                                message=f"The PM2.5 level has just spiked to {pm25} µg/m³.",
                                endpoint=endpoint,
                                p256dh=p256dh,
                                auth=auth,
                                vapid_private=vapid_private,
                                email=email,
                            )
                        except Exception as e:
                            print(f"Failed to send push notification: {e}")
                    
                    sql.insert_marker()
                    
            sql.insert_particles(pm25, pm10)
        else:
            print("Failed to read data from the sensor.")
        time.sleep(20)