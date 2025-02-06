from sensor import SDS011
from sql_connector import SqlConnector
import time

if __name__ == "__main__":
    #pn = PushNotification()
    sql = SqlConnector("database.db")
    sds011 = SDS011("/dev/ttyUSB0")
    
    
    while True:
        sds011.sleep(sleep=False)
        time.sleep(15)
        result = sds011.query()
        sds011.sleep()
        
        if result is not None:
            pm25, pm10 = result
            sql.insert_particles(pm25, pm10)
        else:
            print("Failed to read data from the sensor.")
        
        
        time.sleep(20)