function toggleButtons() {
    var buttons = document.getElementById('buttons');
    if (buttons.style.display === 'none') {
        document.getElementById('toggle-button').innerHTML = 'close';
        buttons.classList.remove('animate__slideOutRight');
        buttons.classList.add('animate__slideInRight');
        buttons.style.display = 'block';

        // if useragent contains ios 
        if (navigator.userAgent.match(/(iPod|iPhone|iPad)/)) {
            document.getElementById('log-button').style.display = 'none';
            document.getElementById('dateInputDummy').classList.remove('invisible-date');
            document.getElementById('dateInputDummy').value = new Date().toISOString().slice(0, 16);
        }

    } else {
        cancelLogging();
        document.getElementById('toggle-button').innerHTML = 'add';
        buttons.classList.remove('animate__slideInRight');
        buttons.classList.add('animate__slideOutRight');
        setTimeout(function() {
            buttons.style.display = 'none';
            buttons.classList.remove('animate__slideOutRight');
        }, 750);
        // if useragent contains ios 
        if (navigator.userAgent.match(/(iPod|iPhone|iPad)/)) {
            document.getElementById('log-button').style.display = 'none';
            document.getElementById('dateInputDummy').classList.add('invisible-date');
        }
    }
}

function cancelLogging() {
    document.getElementById('dateInput').value = '';
    document.getElementById('dateInputDummy').value = '';
    document.getElementById('time-selection-window').style.display = 'none';
    document.getElementById('log-button').style.display = 'flex';

    if (navigator.userAgent.match(/(iPod|iPhone|iPad)/)) {
        document.getElementById('toggle-button').innerHTML = 'add';
        buttons.classList.remove('animate__slideInRight');
        buttons.classList.add('animate__slideOutRight');
        setTimeout(function() {
            buttons.style.display = 'none';
            buttons.classList.remove('animate__slideOutRight');
        }, 750);
        // if useragent contains ios 
        if (navigator.userAgent.match(/(iPod|iPhone|iPad)/)) {
            document.getElementById('log-button').style.display = 'none';
            document.getElementById('dateInputDummy').classList.add('invisible-date');
        }
    }
}

function confirmLogging() {
    fetch('/set_marker', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            date: document.getElementById('dateInput').value
        })
    }).then(response => {
        document.getElementById('graph').src = '/image/last_30_min?' + new Date().getTime();
        cancelLogging();
        document.getElementById('toggle-button').innerHTML = 'add';
        buttons.classList.remove('animate__slideInRight');
        buttons.classList.add('animate__slideOutRight');
        setTimeout(function() {
            buttons.style.display = 'none';
            buttons.classList.remove('animate__slideOutRight');
        }, 750);
    });
}

function setMarker() {
    if (document.getElementById('dateInput').value === '') {
        document.getElementById('dateInputDummy').showPicker();
        return;
    }
}

function changeInterval(button, interval) {
    global_offset = 0;
    document.getElementById('graph').src = '/image/' + interval + '?' + new Date().getTime();

    const buttons = document.getElementsByClassName('interval-button');
    for (let i = 0; i < buttons.length; i++) {
        buttons[i].style.backgroundColor = 'transparent';
    }
    
    button.style.backgroundColor = '#4e4ad9';
}

function changeOffset(button, offset) {
    var interval_buttons = document.getElementsByClassName('interval-button');
    var interval = '';

    for (let i = 0; i < interval_buttons.length; i++) {
        if (interval_buttons[i].style.backgroundColor === 'rgb(78, 74, 217)') {
            interval = interval_buttons[i].innerText;
            break;
        }
    }
    
    global_offset += offset;
    if (global_offset < 0) {
        global_offset = 0;
    }
    

    if (interval === '30m') {
        document.getElementById('graph').src = '/image/last_30_min?offset=' + global_offset + '&t=' + new Date().getTime();
    } else if (interval === '2h') {
        document.getElementById('graph').src = '/image/last_2_hours?offset=' + global_offset + '&t=' + new Date().getTime();
    }
}

function updateAirQuality(rgb) {
    // make indicator blink
    const intervalId = setInterval(() => {
        const indicator = document.getElementById('quality-indicator');
        const quality = document.getElementById('quality');
        if (indicator.style.backgroundColor === 'rgb(' + rgb[0] + ', ' + rgb[1] + ', ' + rgb[2] + ')') {
            indicator.style.backgroundColor = 'rgba(' + rgb[0] + ', ' + rgb[1] + ', ' + rgb[2] + ', 0.33)';
            quality.style.color = 'rgba(' + rgb[0] + ', ' + rgb[1] + ', ' + rgb[2] + ', 0.33)';
        } else {
            indicator.style.backgroundColor = 'rgb(' + rgb[0] + ', ' + rgb[1] + ', ' + rgb[2] + ')';
            quality.style.color = 'rgb(' + rgb[0] + ', ' + rgb[1] + ', ' + rgb[2] + ')';
        }
    }, 600);

    fetch('/get_aqi_label')
        .then(response => response.json())
        .then(data => {
            if (data.description == "Good") {
                clearInterval(intervalId);
                document.getElementById('quality').style.color = "rgb(102, 225, 125)";
                document.getElementById('quality').innerText = data.description;
                document.getElementById('quality-indicator').style.backgroundColor = "rgb(102, 225, 125)";
                rgb = [102, 225, 125];
            } else if (data.description == "Moderate") {
                clearInterval(intervalId);
                document.getElementById('quality').style.color = "rgb(253, 226, 47)";
                document.getElementById('quality').innerText = data.description;
                document.getElementById('quality-indicator').style.backgroundColor = "rgb(253, 226, 47)";
                rgb = [253, 226, 47];
            } else if (data.description == "Unhealthy for Sensitive Groups") {
                clearInterval(intervalId);
                document.getElementById('quality').style.color = "rgb(255, 186, 24)";
                document.getElementById('quality').innerText = data.description;
                document.getElementById('quality-indicator').style.backgroundColor = "rgb(255, 186, 24)";
                rgb = [255, 186, 24];
            } else if (data.description == "Unhealthy") {
                clearInterval(intervalId);
                document.getElementById('quality').style.color = "rgb(255, 84, 42)";
                document.getElementById('quality').innerText = data.description;
                document.getElementById('quality-indicator').style.backgroundColor = "rgb(255, 84, 42)";
                rgb = [255, 84, 42];
            } else if (data.description == "Very Unhealthy") {
                clearInterval(intervalId);
                document.getElementById('quality').style.color = "rgb(155, 16, 255)";
                document.getElementById('quality').innerText = data.description;
                document.getElementById('quality-indicator').style.backgroundColor = "rgb(155, 16, 255)";
                rgb = [155, 16, 255];
            } else if (data.description == "Hazardous") {
                clearInterval(intervalId);
                document.getElementById('quality').style.color = "rgb(157, 27, 27)";
                document.getElementById('quality').innerText = data.description;
                document.getElementById('quality-indicator').style.backgroundColor = "rgb(157, 27, 27)";
                rgb = [157, 27, 27];
            } else {
                clearInterval(intervalId);
                document.getElementById('quality').style.color = "rgb(189, 189, 189)";
                document.getElementById('quality').innerText = "Unknown";
                document.getElementById('quality-indicator').style.backgroundColor = "rgb(189, 189, 189)";
                rgb = [189, 189, 189];
            }
        })
        .catch(error => {
            console.error('Error:', error);
            clearInterval(intervalId);
            document.getElementById('quality').style.color = "rgb(189, 189, 189)";
            document.getElementById('quality').innerText = "Unknown";
            document.getElementById('quality-indicator').style.backgroundColor = "rgb(189, 189, 189)";
            rgb = [189, 189, 189];
        });
    rgb = document.getElementById('quality-indicator').style.backgroundColor;
    str = rgb.replace('rgb(', '').replace(')', '').split(', ');
    rgb = [parseInt(str[0]), parseInt(str[1]), parseInt(str[2])];
    return rgb;
}

function updateSystemLoad() {
    fetch('/get_system_load')
        .then(response => response.json())
        .then(data => {
            document.getElementById('hostname').innerText = data.hostname;
            document.getElementById('cpu-util').innerText = `${data.cpu} %`;
            document.getElementById('ram-util').innerText = `${data.ram.used} GB of ${data.ram.total} GB used`;
            document.getElementById('disk-util').innerText = `${data.disk.used} GB of ${data.disk.total} GB used`;
            document.getElementById('db-size').innerText = `${data.db_size} MB`;
            document.getElementById('system-load-last-updated').innerText = `Last updated: ${new Date().toLocaleString('de-DE')}`;
        })
        .catch(error => {
            document.getElementById('hostname').innerText = `Error`;
            document.getElementById('cpu-util').innerText = `Error`;
            document.getElementById('ram-util').innerText = `Error`;
            document.getElementById('disk-util').innerText = `Error`;
            document.getElementById('db-size').innerText = `Error`;
            document.getElementById('system-load-last-updated').innerText = `Last updated: ${new Date().toLocaleString('de-DE')}`;
        });
}

function controlSystem(action) {
    var url = '/stop_service';
    if (action === 'start') {
        url = '/start_service';
    }

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            action: action
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'Running') {
                document.getElementById('status-air-quality-status').style.color = "rgb(102, 225, 125)";
                document.getElementById('status-air-quality-status').innerText = "Active";
                document.getElementById('controlSystem').innerText = "Stop Service";
                document.getElementById('controlSystem').onclick = () => controlSystem("stop");
            } else if (data.status === 'Stopped') {
                document.getElementById('status-air-quality-status').style.color = "rgb(255, 107, 107)";
                document.getElementById('status-air-quality-status').innerText = "Disabled";
                document.getElementById('controlSystem').innerText = "Start Service";
                document.getElementById('controlSystem').onclick = () => controlSystem("start");
            } else {
                document.getElementById('status-air-quality-status').style.color = "rgb(255, 107, 107)";
                document.getElementById('status-air-quality-status').innerText = "Unknown";
                document.getElementById('controlSystem').innerText = "Unavailable";
                document.getElementById('controlSystem').disabled = true;
                document.getElementById('controlSystem').style.cursor = 'not-allowed';
                document.getElementById('controlSystem').onclick = null;
            }
            document.getElementById('status-air-quality-last-updated').innerText = `Last updated: ${new Date().toLocaleString('de-DE')}`;
        })
        .catch(error => {
            document.getElementById('status-air-quality-status').innerText = "Error";
            document.getElementById('status-air-quality-status').style.color = "rgb(255, 107, 107)";
            document.getElementById('status-air-quality-last-updated').innerText = `Last updated: ${new Date().toLocaleString('de-DE')}`;
            document.getElementById('controlSystem').innerText = "Unknown";
            document.getElementById('controlSystem').disabled = true;
            document.getElementById('controlSystem').style.cursor = 'not-allowed';
            document.getElementById('controlSystem').onclick = null;
        });
}

function clearDB() {
    var result = confirm('Are you sure you want to clear the database? This action is irreversible.');
    if (!result) {
        return;
    }

    fetch('/clear_db', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            action: 'clear'
        })
    });
}