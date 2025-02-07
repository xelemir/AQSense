import sqlite3
from datetime import datetime
import pytz

class SqlConnector:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        
    def create_table(self, table_name):
        if table_name == "markers":
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS markers (id INTEGER PRIMARY KEY AUTOINCREMENT, time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)''')
        elif table_name == "particles":
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS particles (id INTEGER PRIMARY KEY AUTOINCREMENT, time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, two_point_five FLOAT NOT NULL, ten FLOAT NOT NULL)''')
        elif table_name == "webpush_subscriptions":
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS webpush_subscriptions (id INTEGER PRIMARY KEY AUTOINCREMENT, endpoint TEXT NOT NULL, p256dh TEXT NOT NULL, auth TEXT NOT NULL)''')
        
    def insert_marker(self, date=None):
        self.create_table('markers')
        
        if date is None:
            self.cursor.execute('''INSERT INTO markers DEFAULT VALUES''')
            self.conn.commit()
            return
        
        date = datetime.strptime(date, "%Y-%m-%dT%H:%M")
        germany_tz = pytz.timezone("Europe/Berlin")

        # Localize the naive datetime object.
        date_in_germany = germany_tz.localize(date)

        # Convert the datetime to UTC.
        date_utc = date_in_germany.astimezone(pytz.utc)
        self.cursor.execute('''INSERT INTO markers (time) VALUES (?)''', (date_utc,))
        
        #self.cursor.execute('''INSERT INTO markers DEFAULT VALUES''')
        self.conn.commit()
        
    def insert_particles(self, two_point_five, ten):
        self.create_table('particles')
        self.cursor.execute('''INSERT INTO particles (two_point_five, ten) VALUES (?, ?)''', (two_point_five, ten))
        self.conn.commit()
    
    def get_marker_times(self, date=None, offset=0):
        self.create_table('markers')
        
        # For windows that have a fixed duration we define the duration (in SQLite modifier format)
        if date == "last_10_min":
            # Window size is 10 minutes.
            if offset == 0:
                # Base window: from now-10 minutes to now.
                query = (
                    "SELECT * FROM markers "
                    "WHERE time >= datetime('now', '-10 minutes') "
                    "  AND time < datetime('now')"
                )
            else:
                # For offset k, we want:
                #    lower_bound = now - (k+1)*10 minutes
                #    upper_bound = now - (k*10) minutes
                query = (
                    "SELECT * FROM markers "
                    "WHERE time >= datetime('now', '-{} minutes') "
                    "  AND time < datetime('now', '-{} minutes')"
                    .format((offset + 1) * 10, offset * 10)
                )
        elif date == "last_30_min":
            # Window size is 30 minutes.
            if offset == 0:
                query = (
                    "SELECT * FROM markers "
                    "WHERE time >= datetime('now', '-30 minutes') "
                    "  AND time < datetime('now')"
                )
            else:
                query = (
                    "SELECT * FROM markers "
                    "WHERE time >= datetime('now', '-{} minutes') "
                    "  AND time < datetime('now', '-{} minutes')"
                    .format((offset + 1) * 30, offset * 30)
                )
        elif date == "last_2_hours":
            # Window size is 2 hours.
            if offset == 0:
                query = (
                    "SELECT * FROM markers "
                    "WHERE time >= datetime('now', '-2 hours') "
                    "  AND time < datetime('now')"
                )
            else:
                query = (
                    "SELECT * FROM markers "
                    "WHERE time >= datetime('now', '-{} hours') "
                    "  AND time < datetime('now', '-{} hours')"
                    .format((offset + 1) * 2, offset * 2)
                )
        elif date == "today":
            # The base window here is from today’s midnight until now.
            # (SQLite’s date('now') returns the current date with time 00:00:00.)
            if offset == 0:
                query = (
                    "SELECT * FROM markers "
                    "WHERE time >= datetime(date('now')) "
                    "  AND time < datetime('now')"
                )
            else:
                # For a nonzero offset we assume you want the complete previous day(s).
                # For example, offset==1 returns all markers from yesterday.
                # The window is defined as:
                #    lower_bound = midnight of (now - offset days)
                #    upper_bound = midnight of (now - (offset-1) days)
                query = (
                    "SELECT * FROM markers "
                    "WHERE time >= datetime(date('now', '-{} day', 'start of day')) "
                    "  AND time < datetime(date('now', '-{} day', 'start of day'))"
                    .format(offset, offset - 1)
                )
        else:
            # If no date parameter is given, return all markers.
            query = "SELECT * FROM markers"
        
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_particles(self, date=None, offset=0):
        self.create_table('particles')
        
        # For windows that have a fixed duration we define the duration (in SQLite modifier format)
        if date == "last_10_min":
            # Window size is 10 minutes.
            if offset == 0:
                # Base window: from now-10 minutes to now.
                query = (
                    "SELECT * FROM particles "
                    "WHERE time >= datetime('now', '-10 minutes') "
                    "  AND time < datetime('now')"
                )
            else:
                # For offset k, we want:
                #    lower_bound = now - (k+1)*10 minutes
                #    upper_bound = now - k*10 minutes
                query = (
                    "SELECT * FROM particles "
                    "WHERE time >= datetime('now', '-{} minutes') "
                    "  AND time < datetime('now', '-{} minutes')"
                    .format((offset + 1) * 10, offset * 10)
                )
        elif date == "last_30_min":
            # Window size is 30 minutes.
            if offset == 0:
                query = (
                    "SELECT * FROM particles "
                    "WHERE time >= datetime('now', '-30 minutes') "
                    "  AND time < datetime('now')"
                )
            else:
                query = (
                    "SELECT * FROM particles "
                    "WHERE time >= datetime('now', '-{} minutes') "
                    "  AND time < datetime('now', '-{} minutes')"
                    .format((offset + 1) * 30, offset * 30)
                )
        elif date == "last_2_hours":
            # Window size is 2 hours.
            if offset == 0:
                query = (
                    "SELECT * FROM particles "
                    "WHERE time >= datetime('now', '-2 hours') "
                    "  AND time < datetime('now')"
                )
            else:
                query = (
                    "SELECT * FROM particles "
                    "WHERE time >= datetime('now', '-{} hours') "
                    "  AND time < datetime('now', '-{} hours')"
                    .format((offset + 1) * 2, offset * 2)
                )
        elif date == "today":
            # The base window here is from today’s midnight until now.
            # (SQLite’s date('now') returns the current date with time 00:00:00.)
            if offset == 0:
                query = (
                    "SELECT * FROM particles "
                    "WHERE time >= datetime(date('now')) "
                    "  AND time < datetime('now')"
                )
            else:
                # For a nonzero offset we assume you want the complete previous day(s).
                # For example, offset==1 returns all particles from yesterday.
                # The window is defined as:
                #    lower_bound = midnight of (now - offset days)
                #    upper_bound = midnight of (now - (offset-1) days)
                query = (
                    "SELECT * FROM particles "
                    "WHERE time >= datetime(date('now', '-{} day', 'start of day')) "
                    "  AND time < datetime(date('now', '-{} day', 'start of day'))"
                    .format(offset, offset - 1)
                )
        else:
            # If no date parameter is given, return all particles.
            query = "SELECT * FROM particles"
            
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_last_particle(self, minutes=None):
        self.create_table('particles')
        if minutes is not None:
            self.cursor.execute('''SELECT * FROM particles WHERE time >= datetime('now', '-{} minutes') ORDER BY time DESC LIMIT 1'''.format(minutes))
        else:      
            self.cursor.execute('''SELECT * FROM particles ORDER BY time DESC LIMIT 1''')
        return self.cursor.fetchone()
    
    def get_last_marker_within(self, minutes):
        self.create_table('markers')
        self.cursor.execute('''SELECT * FROM markers WHERE time >= datetime('now', '-{} minutes') ORDER BY time DESC LIMIT 1'''.format(minutes))
        return self.cursor.fetchone()
    
    def get_avg_last_particles(self, sample_size, offset=0):
        """ Get the average of the last n particles with optional offset.

        Args:
            sample_size (_type_): _description_
            offset (int, optional): _description_. Defaults to 0.

        Returns:
            _type_: _description_
        """
        self.create_table('particles')
        self.cursor.execute(''' SELECT AVG(two_point_five), AVG(ten) FROM particles WHERE time >= datetime('now', '-{} minutes') AND time < datetime('now', '-{} minutes') ORDER BY time DESC '''.format(sample_size + offset, offset))
        return self.cursor.fetchone()
    
    def delete_markers(self):
        self.cursor.execute('''DELETE FROM markers''')
        self.conn.commit()

    def delete_particles(self):
        self.cursor.execute('''DELETE FROM particles''')
        self.conn.commit()
        
    def __del__(self):
        self.conn.close()
        
if __name__ == "__main__":
    db = SqlConnector("database.db")
    print(db.get_avg_last_particles(30, 5))