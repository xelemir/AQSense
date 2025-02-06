import sqlite3

class SqlConnector:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        
    def create_table(self, table_name):
        if table_name == "markers":
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS markers (id INTEGER PRIMARY KEY AUTOINCREMENT, time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)''')
        elif table_name == "particles":
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS particles (id INTEGER PRIMARY KEY AUTOINCREMENT, time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, two_point_five FLOAT NOT NULL, ten FLOAT NOT NULL)''')
        
    def insert_marker(self):
        self.create_table('markers')
        self.cursor.execute('''INSERT INTO markers DEFAULT VALUES''')
        self.conn.commit()
        
    def insert_particles(self, two_point_five, ten):
        self.create_table('particles')
        self.cursor.execute('''INSERT INTO particles (two_point_five, ten) VALUES (?, ?)''', (two_point_five, ten))
        self.conn.commit()
    
    def get_marker_times(self, date=None):
        self.create_table('markers')
        if date == "today":
            self.cursor.execute('''SELECT * FROM markers WHERE time >= date('now')''')
        elif date == "last_2_hours":
            self.cursor.execute('''SELECT * FROM markers WHERE time >= datetime('now', '-2 hours')''')
        elif date == "last_30_min":
            self.cursor.execute('''SELECT * FROM markers WHERE time >= datetime('now', '-30 minutes')''')
        elif date == "last_10_min":
            self.cursor.execute('''SELECT * FROM markers WHERE time >= datetime('now', '-10 minutes')''')
        else:
            self.cursor.execute('''SELECT * FROM markers''')
        return self.cursor.fetchall()
    
    def get_particles(self, date=None):
        self.create_table('particles')
        if date == "today":
            self.cursor.execute('''SELECT * FROM particles WHERE time >= date('now')''')
        elif date == "last_2_hours":
            self.cursor.execute('''SELECT * FROM particles WHERE time >= datetime('now', '-2 hours')''')
        elif date == "last_30_min":
            self.cursor.execute('''SELECT * FROM particles WHERE time >= datetime('now', '-30 minutes')''')
        elif date == "last_10_min":
            self.cursor.execute('''SELECT * FROM particles WHERE time >= datetime('now', '-10 minutes')''')
        else:
            self.cursor.execute('''SELECT * FROM particles''')
        return self.cursor.fetchall()
    
    def get_last_particle(self):
        self.create_table('particles')
        self.cursor.execute('''SELECT * FROM particles ORDER BY time DESC LIMIT 1''')
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
    db.create_table('markers')