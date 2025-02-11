import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
import matplotlib.patches as mpatches
import numpy as np
import matplotlib
matplotlib.use('Agg')


def get_weather():
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 48.7823,
        "longitude": 9.177,
        "hourly": ["temperature_2m", "precipitation_probability", "precipitation", "wind_speed_10m"],
        "forecast_days": 1
        
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_precipitation_probability = hourly.Variables(1).ValuesAsNumpy()
    hourly_precipitation = hourly.Variables(2).ValuesAsNumpy()
    hourly_wind_speed_10m = hourly.Variables(3).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}

    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["precipitation_probability"] = hourly_precipitation_probability
    hourly_data["precipitation"] = hourly_precipitation
    hourly_data["wind_speed_10m"] = hourly_wind_speed_10m

    hourly_dataframe = pd.DataFrame(data = hourly_data)
    #print(hourly_dataframe)


    # Ensure all text is white globally
    plt.rcParams['text.color'] = 'gray'
    plt.rcParams['axes.labelcolor'] = 'gray'
    plt.rcParams['xtick.color'] = 'gray'
    plt.rcParams['ytick.color'] = 'gray'

    # Create the figure and a host subplot using axisartist
    fig = plt.figure(figsize=(12, 5))
    host = host_subplot(111, axes_class=AA.Axes)
    fig.patch.set_facecolor('#27272f')
    plt.subplots_adjust(left=0.25, right=0.75)

    # Create three parasite axes for the additional variables.
    par1 = host.twinx()  # Precipitation Probability
    par2 = host.twinx()  # Precipitation
    par3 = host.twinx()  # Wind Speed

    # Move all parasite axes to the left side
    offsets = [60, 120, 180]
    for ax, offset in zip([par1, par2, par3], offsets):
        ax.axis["left"] = ax.get_grid_helper().new_fixed_axis(loc="left", axes=ax, offset=(-offset, 0))
        ax.axis["left"].toggle(all=True)
        ax.axis["right"].set_visible(False)

    # ---------------------------
    # Plot the data
    # ---------------------------
    host.plot(hourly_dataframe['date'], hourly_dataframe['temperature_2m'], color='#ff6b6b', label='Temperature (°C)')
    par1.plot(hourly_dataframe['date'], hourly_dataframe['precipitation_probability'], color='#4e4ad9', label='Precipitation Probability (%)')
    date_nums = mdates.date2num(hourly_dataframe['date'])
    bar_width = (date_nums[1] - date_nums[0]) * 0.8 if len(date_nums) > 1 else 0.02
    par2.bar(hourly_dataframe['date'], hourly_dataframe['precipitation'], width=bar_width, color='#2196F3', alpha=0.2, label='Precipitation (mm)')
    par3.plot(hourly_dataframe['date'], hourly_dataframe['wind_speed_10m'], color='#66e17d', label='Wind Speed (m/s)')

    # ---------------------------
    # Format the axes (Make all tick labels white)
    # ---------------------------
    host.xaxis.set_major_locator(mdates.AutoDateLocator())
    host.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    host.tick_params(axis='x', colors='#27272f', rotation=45)  # Host (Time) x-axis white
    host.tick_params(axis='y', colors='#27272f')  # Host (Temperature) y-axis white
    par1.tick_params(axis='y', colors='#27272f')  # Precipitation Probability y-axis white
    par2.tick_params(axis='y', colors='#27272f')  # Precipitation y-axis white
    par3.tick_params(axis='y', colors='#27272f')  # Wind Speed y-axis white


    # Set the y-axis labels and their colors (variable colors remain as defined)
    host.set_ylabel("Temperature (°C)")
    host.axis["left"].label.set_color('#ff6b6b')

    par1.set_ylabel("Precipitation Probability (%)")
    par1.axis["left"].label.set_color('#4e4ad9')

    par2.set_ylabel("Precipitation (mm)")
    par2.axis["left"].label.set_color('#2196F3')

    par3.set_ylabel("Wind Speed (m/s)")
    par3.axis["left"].label.set_color('#66e17d')

    # Ensure the host axis background remains dark
    host.patch.set_facecolor('#27272f')

    # Set all axis spines to white
    for ax in [host, par1, par2, par3]:
        for side in ax.axis:
                ax.axis[side].line.set_color('#27272f')

    plt.savefig('data/weather.png', facecolor=fig.get_facecolor(), transparent=True)