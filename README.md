# AQSense - Measure and Visualize Air Quality

AQSense is an air quality monitoring project that leverages a Raspberry Pi and the SDS011 sensor to measure air quality. Data is stored in a SQLite database and visualized through a web server.


## Features:

- **Air Quality Measurement:** Collects data from the SDS011 sensor.
- **Data Logging:** Stores air quality measurements in a SQLite database.
- **Web Visualization:** Provides a web server for real-time visualization of air quality data.
- **Automated Services:** Uses systemd services for automatic startup and management of both measurement and web server components.


## Getting Started

### 1. Clone the Repository

Clone the repository to your local machine:
```bash
git clone https://github.com/xelemir/AQSense.git
cd AQSense
```

### 2. Set Up the Virtual Environment**

Create and activate a Python virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

With your virtual environment activated, install the required packages:
```bash
pip install -r requirements.txt
```
After installing the required packages, you can deactivate the virtual environment:
```bash
deactivate
```

### 4. Configure Systemd Services

AQSense uses two systemd services: one for the web server and one for the air quality measurement daemon.

**Note:** Replace USERNAME with your actual username and adjust paths if needed.

#### Web Server Service

Create the file /etc/systemd/system/webserver.service with the following content:
```ini
[Unit]
Description=Web Server for AQSense
After=network.target

[Service]
User=USERNAME
WorkingDirectory=/home/USERNAME/AQSense
ExecStart=/home/USERNAME/AQSense/.venv/bin/python /home/USERNAME/AQSense/web_app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

#### Air Quality Measurement Service

Create another service file (for example, /etc/systemd/system/air_quality.service) with the following content:
```ini
[Unit]
Description=Air Quality Measurement for AQSense
After=network.target sound.target

[Service]
User=USERNAME
WorkingDirectory=/home/USERNAME/AQSense
ExecStart=/home/USERNAME/AQSense/.venv/bin/python /home/USERNAME/AQSense/main.py
ExecStop=/home/Python/AQSense/.venv/bin/python /home/USERNAME/AQSense/stop_script.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 5. Enable and Start the Services

First, reload the systemd daemon:
```bash
sudo systemctl daemon-reload
```

Then, enable and start the services:
```bash
sudo systemctl enable webserver.service
sudo systemctl start webserver.service
sudo systemctl enable air_quality.service
sudo systemctl start air_quality.service
```

To check the status of the services, use:
```bash
sudo systemctl status webserver.service
sudo systemctl status air_quality.service
```

Stop the services with:
```bash
sudo systemctl stop webserver.service
sudo systemctl stop air_quality.service
```

Completly disable the services with:
```bash
sudo systemctl disable webserver.service
sudo systemctl disable air_quality.service
```

## Usage

Now that the services are running, you can access the web server by navigating to http://<HOSTNAME>:1337 in your web browser. The web server provides real-time visualization of the air quality data collected by the SDS011 sensor (Replace <HOSTNAME> with the actual hostname or IP address of your device, e.g. the Raspberry Pi).

## Acknowledgments

AQSense builds upon ideas and code from other projects. Special thanks to the [py-sds011](https://github.com/ikalchev/py-sds011) repository by [Ivan](https://github.com/ikalchev) for providing the SDS011 sensor interface.