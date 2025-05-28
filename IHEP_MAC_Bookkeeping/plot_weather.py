import os
import glob
import csv
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.ticker import MaxNLocator
from collections import defaultdict
import json
from matplotlib.dates import DateFormatter
#files=["10.191.12.6-output.csv", "10.191.12.130-output.csv", "10.191.12.4-output.csv", "10.191.12.129-output.csv", "10.191.12.132-output.csv" ,"10.191.12.3-output.csv"]
#"129.118.107.205" "129.118.107.234" "129.118.107.204" "129.118.107.233" "129.118.107.235" "129.118.107.232"
#naming_dict={"10.191.12.6-output.csv": "Pi A", "10.191.12.130-output.csv": "Pi B", "10.191.12.4-output.csv": "Pi C", "10.191.12.129-output.csv": "Pi D", "10.191.12.132-output.csv": "Pi E" ,"10.191.12.3-output.csv": "Pi F"}
def whats_the_weather():
    directory = "/home/daq2-admin/APD-WeatherStation/data_folder/"
    prefixes = {"p129.118.107.232": "Lobby","p129.118.107.233": "Room A", "p129.118.107.234": "Room B", "p129.118.107.204": "Room C", "p129.118.107.205": "Room D", "p129.118.107.235": "Chase area"}
    grouped_files = defaultdict(list)
    output_figs=[]
    all_files = glob.glob(os.path.join(directory, "*.csv"))
    #print(all_files)
    for filepath in all_files:
        filename = os.path.basename(filepath)
        for prefix in prefixes:
            if filename.startswith(prefix):
                grouped_files[prefix].append(filepath)
                break
    #required_columns = {"Time", "Humidity", "Temperature", "Pressure"}       
    for prefix, files in grouped_files.items():
        dfs=[]
        for file_path in files:
            try:
                df = pd.read_csv(file_path)
                df.columns = df.columns.str.strip()
                dfs.append(df)
            except Exception as e:
                print(f"❌ Failed reading {file_path}: {e}")
                continue
        df = pd.concat(dfs, ignore_index=True)
        label = prefixes.get(prefix, prefix)  # fallback to prefix if label missing
        print(f"\nProcessing {label} (prefix: {prefix})")
            #print(f"     ✅ Columns: {df.columns.tolist()} | Rows: {len(df)}")
        try:
            time=df["Time"].to_numpy()
            humidity=df["Humidity"].to_numpy()
            temperature=df["Temperature"].to_numpy()
            pressure=df["Pressure"].to_numpy()
            fig, axs = plt.subplots(1, 3, figsize=(15, 5))
            mask = (humidity >= 5) & (humidity <= 60)
            axs[0].plot(time[mask], humidity[mask],'g.')
            axs[0].set_ylim(0,80)
            axs[0].set_xlabel("Time")
            axs[0].set_ylabel("Humidity %%")
            axs[0].set_title(label)
            #plt.xticks(rotation=45)
            mask = (temperature >= 0) & (temperature <= 40)
            axs[1].plot(time[mask], temperature[mask],'r.')
            axs[1].set_ylim(15,30)
            axs[1].set_xlabel("Time")
            axs[1].set_ylabel("Temperature C")
            axs[1].set_title(label)
            #plt.xticks(rotation=45)
            mask = (pressure >= 890) & (pressure <= 910)
            axs[2].plot(time[mask], pressure[mask],'b.')
            axs[2].set_ylim(850,1000)
            axs[2].set_xlabel("Time")
            axs[2].set_ylabel("Pressure [hPa]")
            axs[2].set_title(label)
            axs[0].xaxis.set_major_locator(MaxNLocator(integer=True, prune='both', nbins=7))
            axs[1].xaxis.set_major_locator(MaxNLocator(integer=True, prune='both', nbins=7))
            axs[2].xaxis.set_major_locator(MaxNLocator(integer=True, prune='both', nbins=7))
            ticks = axs[0].get_xticklabels()
            for tick in ticks:
                tick.set_horizontalalignment('right')
            # Set horizontal alignment of x-tick labels to 'center'
            ticks = axs[1].get_xticklabels()
            for tick in ticks:
                tick.set_horizontalalignment('right')
            ticks = axs[2].get_xticklabels()
            for tick in ticks:
                tick.set_horizontalalignment('right')
            plt.tight_layout()
            #plt.xticks(rotation=45)
            for ax in axs:
                ax.tick_params(axis='x', rotation=30)
            plt.subplots_adjust(bottom=0.2)
            output_figs.append(fig)

        except:
            print(f"✅ Columns: {df.columns.tolist()} | Rows: {len(df)}")
        print(len(output_figs))
    return output_figs
    


def scrollbar_weather():
    directory = "/path/to/APD_weatherstation/data_folder/"
    prefixes = {"p129.118.107.232": "Lobby","p129.118.107.233": "Room A", "p129.118.107.234": "Room B", "p129.118.107.204": "Room C", "p129.118.107.205": "Room D", "p129.118.107.235": "Chase area"}
    grouped_files = defaultdict(list)
    output_figs=[]
    all_files = glob.glob(os.path.join(directory, "*.csv"))
    #print(all_files)
    for filepath in all_files:
        filename = os.path.basename(filepath)
        for prefix in prefixes:
            if filename.startswith(prefix):
                grouped_files[prefix].append(filepath)
                break
    #required_columns = {"Time", "Humidity", "Temperature", "Pressure"}       
    for prefix, files in grouped_files.items():
        dfs=[]
        room_metadata = [] 
        for file_path in files:
            try:
                df = pd.read_csv(file_path)
                df.columns = df.columns.str.strip()
                dfs.append(df)
            except Exception as e:
                print(f"Failed reading {file_path}: {e}")
                continue
        df = pd.concat(dfs, ignore_index=True)
        label = prefixes.get(prefix, prefix)  # fallback to prefix if label missing
        print(f"\nProcessing {label} (prefix: {prefix})")
        try:
            df["Time"] = pd.to_datetime(df["Time"])
            latest_time = df["Time"].max().strftime("%Y-%m-%d %H:%M:%S")
            humidity=df["Humidity"].to_numpy()
            temperature=df["Temperature"].to_numpy()
            pressure=df["Pressure"].to_numpy()

            latest_humidity = round(humidity[-1], 1)
            latest_temp = round(temperature[-1], 1)
            latest_pressure = round(pressure[-1], 1)

            room_metadata.append({
                "label": label,
                "time": latest_time,
                "temp": latest_temp,
                "humidity": latest_humidity,
                "pressure": latest_pressure
            })
        except:
            print("FAILED TO GET METADATA!")
    return room_metadata
#plt.savefig(label+"weather_report.png")

def segment_data(timestamps, values, max_gap=timedelta(hours=(44/60))):
    """Split data into segments where time difference between points is <= max_gap."""
    segments = []
    seg_times = [timestamps[0]]
    seg_values = [values[0]]
    for i in range(1, len(timestamps)):
        if timestamps[i] - timestamps[i - 1] > max_gap:
            segments.append((seg_times, seg_values))
            seg_times = []
            seg_values = []
        seg_times.append(timestamps[i])
        seg_values.append(values[i])
    if seg_times:
        segments.append((seg_times, seg_values))
    return segments

def particle_count_plot():
    all_records = []
    directory="/home/daq2-admin/APD-WeatherStation/particle_counter/data_files"
    for filepath in glob(os.path.join(directory, "counter_data*.json")):
        with open(filepath, 'r') as f:
            try:
                data = json.load(f)
                # Handle both single object and list of objects
                if isinstance(data, dict):
                    data = [data]

                for entry in data:
                    record = {
                        "timestamp": entry.get("timestamp"),
                        **entry.get("diff_counts_m3", {})
                    }
                    all_records.append(record)

            except Exception as e:
                print(f"Error reading {filepath}: {e}")

    # Create DataFrame
    df = pd.DataFrame(all_records)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df=df.sort_values('timestamp').reset_index(drop=True)
    expected_channels = ["0.30 um", "0.50 um", "1.00 um", "2.50 um", "5.00 um", "10.00 um"]
    max_vals = [102000, 35200, 8320, 8320, 293, 293]

    fig, axs = plt.subplots(3, 2, figsize=(15, 8), sharex=True)
    axs = axs.flatten()

    date_format = DateFormatter("%Y-%m-%d %H:%M")

    for i, channel in enumerate(expected_channels):
        if channel in df.columns:
            ts = df['timestamp']
            vals = df[channel]

            # Drop NaNs
            valid = vals.notna()
            ts = ts[valid]
            vals = vals[valid]

            segments = segment_data(ts.tolist(), vals.tolist())

            for seg_times, seg_vals in segments:
                axs[i].plot(seg_times, seg_vals, marker='o', ms=3.0)

            axs[i].axhline(y=max_vals[i], color='r', linestyle='--')
            axs[i].text(
                ts.iloc[0],
                max_vals[i] * 0.9,
                f"ISO 6 max: {max_vals[i]} ct/m3",
                color='r', fontsize=8
            )
            axs[i].set_title(channel)
            axs[i].set_ylabel("count/m3")
            axs[i].xaxis.set_major_formatter(date_format)
            axs[i].tick_params(axis='x', rotation=45, labelsize=6)

    axs[-1].set_xlabel("Time")
    fig.suptitle("Particle Count Trends with ISO Limits", fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    return fig
