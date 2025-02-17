import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from sql_connector import SqlConnector
import pytz
from config import TIMEZONE

def round_down_to_x_minutes(dt, x):
    """
    Round down a datetime to the nearest x-minute interval.
    """
    total_minutes = dt.hour * 60 + dt.minute
    remainder = total_minutes % x
    new_total = total_minutes - remainder
    new_hour = new_total // 60
    new_minute = new_total % 60
    return dt.replace(hour=new_hour, minute=new_minute, second=0, microsecond=0)

def round_down_to_day(dt):
    """
    Round down a datetime to the start of the day (midnight).
    """
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)

def visualize_data(range_="last_2_hours", offset=0, data_type="pm_2_point_5"):
    # Decide on binning function based on the range_
    if range_ == "today":
        bin_size_minutes = 10
        bin_func = lambda d: round_down_to_x_minutes(d, bin_size_minutes)
    elif range_ == "total":
        # Group by day
        bin_func = round_down_to_day
    elif range_ == "last_30_min":
        bin_size_minutes = 1
        bin_func = lambda d: round_down_to_x_minutes(d, bin_size_minutes)
    elif range_ == "last_2_hours":
        bin_size_minutes = 5
        bin_func = lambda d: round_down_to_x_minutes(d, bin_size_minutes)
    elif range_ == "last_10_min":
        bin_size_minutes = 1
        bin_func = lambda d: round_down_to_x_minutes(d, bin_size_minutes)
    else:
        # Default if none of the above matches
        bin_size_minutes = 5
        bin_func = lambda d: round_down_to_x_minutes(d, bin_size_minutes)

    sql = SqlConnector("database.db")
    data = sql.get_particles(range_, offset)
    verified_data = sql.get_marker_times(range_, offset)

    # --------------------------------------------------------
    # 1) Group data by the chosen binning function
    # --------------------------------------------------------
    grouped_pm_2_point_5 = {}
    grouped_pm_10 = {}
    for entry in data:
        dt_str = entry[1]             # "YYYY-mm-dd HH:MM:SS"
        data_value_pm_2_point_5 = entry[2]
        data_value_pm_10 = entry[3]
        try:
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S%z")
            
        dt_bin = bin_func(dt)         # Round down to the bin

        grouped_pm_2_point_5.setdefault(dt_bin, []).append(data_value_pm_2_point_5)
        grouped_pm_10.setdefault(dt_bin, []).append(data_value_pm_10)

    # Compute average (or another aggregate) for each bin
    times_binned = []
    data_binned_pm_2_point_5 = []
    data_binned_max_pm_2_point_5 = []
    data_binned_min_pm_2_point_5 = []
    data_binned_pm_10 = []
    data_binned_max_pm_10 = []
    data_binned_min_pm_10 = []
    
    for key_dt in sorted(grouped_pm_2_point_5.keys()):
        values_pm_2_point_5 = grouped_pm_2_point_5[key_dt]
        avg_val = sum(values_pm_2_point_5) / len(values_pm_2_point_5)
        max_val = max(values_pm_2_point_5)
        min_val = min(values_pm_2_point_5)
        times_binned.append(key_dt)
        data_binned_pm_2_point_5.append(avg_val)
        data_binned_max_pm_2_point_5.append(max_val)
        data_binned_min_pm_2_point_5.append(min_val)
        
    for key_dt in sorted(grouped_pm_10.keys()):
        values_pm_10 = grouped_pm_10[key_dt]
        avg_val = sum(values_pm_10) / len(values_pm_10)
        max_val = max(values_pm_10)
        min_val = min(values_pm_10)
        data_binned_pm_10.append(avg_val)
        data_binned_max_pm_10.append(max_val)
        data_binned_min_pm_10.append(min_val)

    # --------------------------------------------------------
    # 2) Handle verified data the same way
    # --------------------------------------------------------
    verified_binned = []
    for entry in verified_data:
        dt_str = entry[1]        
        try:
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S%z")
        dt_bin = bin_func(dt)
        verified_binned.append(dt_bin)

    # Verified points at the maximum value of the data for that bin
    y = max(data_binned_pm_2_point_5 + [0])  # If no data, use 0
    verified_y_values = [y] * len(verified_binned)

    # --------------------------------------------------------
    # 3) Plot
    # --------------------------------------------------------
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor('#22222a')  # Figure background
    ax.set_facecolor('#22222a')         # Axes background

    # Plot the aggregated data
    ax.plot(times_binned, data_binned_pm_2_point_5, marker='o', linestyle='-', color='#4e4ad9')
    
    # Plot the max data
    ax.scatter(times_binned, data_binned_max_pm_2_point_5, color='#4e4ad9')
    
    # Plot the min data
    ax.scatter(times_binned, data_binned_min_pm_2_point_5, color='#4e4ad9')
    
    if data_type == "pm_10":
        # Plot the PM10 data
        ax.plot(times_binned, data_binned_pm_10, marker='o', linestyle='-', color='#d94a4e')
        ax.scatter(times_binned, data_binned_max_pm_10, color='#d94a4e')
        ax.scatter(times_binned, data_binned_min_pm_10, color='#d94a4e')

    # Plot the verified data
    ax.scatter(verified_binned, verified_y_values, color='red', zorder=10)
    #ax.bar(verified_binned, verified_y_values, width=0.0003, color='red', alpha=0.5)
    
    # Format the x-axis as dates/times
    if range_ == "total":
        date_format = mdates.DateFormatter("%Y-%m-%d")
    else:
        date_format = mdates.DateFormatter("%H:%M", tz=pytz.timezone(TIMEZONE))
    ax.xaxis.set_major_formatter(date_format)
    fig.autofmt_xdate()  # Automatically rotate date labels

    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')

    for spine in ax.spines.values():
        spine.set_edgecolor('#22222a')

    ax.grid(True, color='gray', linestyle='--', linewidth=0.5)
    
    # legend and labels
    if data_type == "pm_2_point_5":
        ax.set_ylabel("PM2.5 (µg/m³)", color='white')
    elif data_type == "pm_10":
        ax.plot([], [], marker='o', linestyle='-', color='#4e4ad9', label='PM2.5')
        ax.plot([], [], marker='o', linestyle='-', color='#d94a4e', label='PM10')
        ax.legend(loc='upper left', facecolor='#333339', edgecolor='#333339', framealpha=0.6, labelcolor='white')

    plt.tight_layout()
    plt.savefig('data/plot.png')
    plt.close()

if __name__ == "__main__":
    visualize_data("last_2_hours")