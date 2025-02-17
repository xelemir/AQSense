import datetime
import os
from flask import Flask, jsonify, request
from flask import send_file, render_template
import pytz
from weather import get_weather
from visualize import visualize_data
from sensor import calculate_aqi_pm25
from sql_connector import SqlConnector
import subprocess
import psutil
import time
from config import TIMEZONE

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    sql = SqlConnector("database.db")
    spikes = [list(elem) for elem in sql.get_markers_desc()]
    for spike in spikes:
        try:
            spike[1] = datetime.datetime.strptime(spike[1], "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc).astimezone(pytz.timezone(TIMEZONE)).strftime("%d.%m.%Y %H:%M:%S")
        except:
            spike[1] = datetime.datetime.strptime(spike[1], "%Y-%m-%d %H:%M:%S%z").replace(tzinfo=pytz.utc).astimezone(pytz.timezone(TIMEZONE)).strftime("%d.%m.%Y %H:%M:%S")
    return render_template('dashboard.html', spikes=spikes)

@app.route('/logo.png')
def logo():
    return send_file("data/logo.png", mimetype='image/png')

@app.route('/site.webmanifest')
def manifest():
    return send_file("data/site.webmanifest")

@app.route('/javascript.js')
def js():
    return send_file("data/javascript.js")

@app.route('/image/<range_>')
def image(range_):
    offset = int(request.args.get('offset', 0))
    data_type = request.args.get('data_type', 'pm_2_point_5')
    visualize_data(range_, offset, data_type)
    return send_file("data/plot.png", mimetype='image/png')

@app.route('/weather')
def weather():
    get_weather()
    return send_file("data/weather.png", mimetype='image/png')

@app.route('/set_marker', methods=['POST'])
def set_marker():
    sql = SqlConnector("database.db")
    sql.create_table("markers")
    
    date = request.json["date"]    
    sql.insert_marker(date) 
    return jsonify({"status": "success"})

@app.route('/get_aqi_label', methods=['GET'])
def get_aqi_label():
    sql = SqlConnector("database.db")
    pm25_reading = sql.get_last_particle()
    if pm25_reading is None: return jsonify({ "aqi_class": 0, "description": "No data" })
    pm25_reading = float(pm25_reading[2])
    aqi_class, description = calculate_aqi_pm25(pm25_reading)
    return jsonify({ "aqi_class": aqi_class, "description": description })

@app.route('/get_service_status', methods=['GET'])
def get_service_status():
    try:
        # Run the systemctl command to get the status of "air_quality"
        result = subprocess.run(
            ["sudo", "systemctl", "status", "air_quality"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True  # ensures the output is returned as a string
        )
        
        # Return the output of the command as part of the JSON response
        if "active (running)" in result.stdout:
            return jsonify({
                "service": "air_quality",
                "status": "Running",
                "output": result.stdout
            })
        elif "inactive (dead)" in result.stdout:
            return jsonify({
                "service": "air_quality",
                "status": "Stopped",
                "output": result.stdout
            })
        else:
            return jsonify({
                "service": "air_quality",
                "status": "Unknown",
                "output": result.stdout
            })    
            
    except Exception as e:
        # Catch any exceptions and return an error response
        return jsonify({
            "service": "air_quality",
            "status": "Error",
            "error": str(e)
        }), 200
        
@app.route('/start_service', methods=['POST'])
def start_service():
    try:
        # Run the systemctl command to start the "air_quality" service
        result = subprocess.run(
            ["sudo", "systemctl", "start", "air_quality"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True  # ensures the output is returned as a string
        )
        
        # Return the output of the command as part of the JSON response
        return jsonify({
            "service": "air_quality",
            "status": "Running",
            "output": result.stdout
        })
        
    except Exception as e:
        # Catch any exceptions and return an error response
        return jsonify({
            "service": "air_quality",
            "status": "exception",
            "error": str(e)
        }), 200
        
@app.route('/stop_service', methods=['POST'])
def stop_service():
    try:
        # Run the systemctl command to stop the "air_quality" service
        result = subprocess.run(
            ["sudo", "systemctl", "stop", "air_quality"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True  # ensures the output is returned as a string
        )
        
        # Return the output of the command as part of the JSON response
        return jsonify({
            "service": "air_quality",
            "status": "Stopped",
            "output": result.stdout
        })
        
    except Exception as e:
        # Catch any exceptions and return an error response
        return jsonify({
            "service": "air_quality",
            "status": "exception",
            "error": str(e)
        }), 200
        
@app.route('/get_system_load', methods=['GET'])
def get_system_load():
    # Get CPU utilization (percentage over a 1 second interval)
    cpu_util = psutil.cpu_percent(interval=1)
    
    # Get RAM (virtual memory) details
    ram = psutil.virtual_memory()
    ram_info = {
        "total": ram.total,
        "available": ram.available,
        "percent": ram.percent,
        "used": ram.used,
        "free": ram.free,
    }
    
    # Get Disk usage details for the root filesystem
    disk = psutil.disk_usage('/')
    disk_info = {
        "total": disk.total,
        "used": disk.used,
        "free": disk.free,
        "percent": disk.percent,
    }
    
    # Get the total size of the databse.db file in bytes
    
    db_size = os.path.getsize("database.db")
    db_size_mb = db_size / (1024 * 1024)
    
    
    ram_info["total"] = round(ram_info["total"] / (1024 * 1024 * 1024), 2)
    ram_info["available"] = round(ram_info["available"] / (1024 * 1024 * 1024), 2)
    ram_info["used"] = round(ram_info["used"] / (1024 * 1024 * 1024), 2)
    ram_info["free"] = round(ram_info["free"] / (1024 * 1024 * 1024), 2)
    
    disk_info["total"] = round(disk_info["total"] / (1024 * 1024 * 1024), 2)
    disk_info["used"] = round(disk_info["used"] / (1024 * 1024 * 1024), 2)
    disk_info["free"] = round(disk_info["free"] / (1024 * 1024 * 1024), 2)
        
    return jsonify({
        "hostname": os.uname().nodename,
        "cpu": cpu_util,
        "ram": ram_info,
        "disk": disk_info,
        "db_size": db_size_mb
    })    
    
@app.route('/clear_db', methods=['POST'])
def clear_db():
    sql = SqlConnector("database.db")
    sql.delete_markers()
    sql.delete_particles()
    return jsonify({"status": "success"})

@app.route('/clear_db_today', methods=['POST'])
def clear_db_today():
    sql = SqlConnector("database.db")
    sql.delete_markers("today")
    sql.delete_particles("today")
    return jsonify({"status": "success"})

@app.route('/delete_spike/', methods=['POST'])
def delete_spike():
    sql = SqlConnector("database.db")
    id_ = request.json["id"]
    sql.delete_marker(id_)
    return jsonify({"status": "success"})

if __name__ == '__main__':
    # Bind to 0.0.0.0 so the app is accessible on your local networkt
    app.run(host='0.0.0.0', port=1337, debug=True)