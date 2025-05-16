import os
import glob
import csv
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.ticker import MaxNLocator
from collections import defaultdict
#files=["10.191.12.6-output.csv", "10.191.12.130-output.csv", "10.191.12.4-output.csv", "10.191.12.129-output.csv", "10.191.12.132-output.csv" ,"10.191.12.3-output.csv"]
#"129.118.107.205" "129.118.107.234" "129.118.107.204" "129.118.107.233" "129.118.107.235" "129.118.107.232"
#naming_dict={"10.191.12.6-output.csv": "Pi A", "10.191.12.130-output.csv": "Pi B", "10.191.12.4-output.csv": "Pi C", "10.191.12.129-output.csv": "Pi D", "10.191.12.132-output.csv": "Pi E" ,"10.191.12.3-output.csv": "Pi F"}
def whats_the_weather():
    directory = "/home/daq2-admin/APD-WeatherStation/data_folder/"
    prefixes = {"p129.118.107.205": "Room D", "p129.118.107.234": "Room B", "p129.118.107.204": "Room C", "p129.118.107.233": "Room A", "p129.118.107.235": "Chase area", "p129.118.107.232": "Lobby"}
    grouped_files = defaultdict(list)
    output_figs=[]
    all_files = glob.glob(os.path.join(directory, "*.csv"))
    for filepath in all_files:
        filename = os.path.basename(filepath)
        for prefix in prefixes:
            if filename.startswith(prefix):
                grouped_files[prefix].append(filepath)
                break
            
    for prefix, files in grouped_files.items():
        label = prefixes.get(prefix, prefix)  # fallback to prefix if label missing
        print(f"\nProcessing {label} (prefix: {prefix})")
        print(f"\nProcessing {label} (prefix: {prefix})")
        for file_path in files:
            df = pd.read_csv(file_path)
            time=df["Time"].to_numpy()
        humidity=df["Humidity"].to_numpy()
        temperature=df["Temperature"].to_numpy()
        pressure=df["Pressure"].to_numpy()
        fig, axs = plt.subplots(1, 3, figsize=(15, 5))
        mask = (humidity >= 5) & (humidity <= 60)
        axs[0].plot(time[mask], humidity[mask],'go')
        #axs[0].set_ylim(0,100)
        axs[0].set_xlabel("Time")
        axs[0].set_ylabel("Humidity %%")
        axs[0].set_title(label)
        #plt.xticks(rotation=45)
        mask = (temperature >= 0) & (temperature <= 40)
        axs[1].plot(time[mask], temperature[mask],'ro')
        #axs[1].set_ylim(5,40)
        axs[1].set_xlabel("Time")
        axs[1].set_ylabel("Temperature C")
        axs[1].set_title(label)
        #plt.xticks(rotation=45)
        mask = (pressure >= 890) & (pressure <= 910)
        axs[2].plot(time[mask], pressure[mask],'bo')
        #axs[2].set_ylim(875,925)
        axs[2].set_xlabel("Time")
        axs[2].set_ylabel("Pressure [unit]")
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
        print(len(output_figs))
    return output_figs
    
    #plt.savefig(label+"weather_report.png")
'''
for i in files:
    df = pd.read_csv("/home/daq2-admin/APD-WeatherStation/"+i)
    time=df["Time"].to_numpy()
    humidity=df["Humidity"].to_numpy()
    temperature=df["Temperature"].to_numpy()
    pressure=df["Pressure"].to_numpy()
    fig, axs = plt.subplots(1, 3, figsize=(15, 5))
    mask = (humidity >= 5) & (humidity <= 60)
    axs[0].plot(time[mask], humidity[mask],marker='o')
    #axs[0].set_ylim(0,100)
    axs[0].set_xlabel("Time")
    axs[0].set_ylabel("Humidity %%")
    axs[0].set_title(naming_dict[i])
    #plt.xticks(rotation=45)
    mask = (temperature >= 0) & (temperature <= 40)
    axs[1].plot(time[mask], temperature[mask],marker='o')
    #axs[1].set_ylim(5,40)
    axs[1].set_xlabel("Time")
    axs[1].set_ylabel("Temperature C")
    axs[1].set_title(naming_dict[i])
    #plt.xticks(rotation=45)
    mask = (pressure >= 890) & (pressure <= 910)
    axs[2].plot(time[mask], pressure[mask],marker='o')
    #axs[2].set_ylim(875,925)
    axs[2].set_xlabel("Time")
    axs[2].set_ylabel("Pressure [unit]")
    axs[2].set_title(naming_dict[i])
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
    #plt.savefig("/Users/sloks/Public/TTU-MAC-SOFTWARE/APD_weatherstation/"+naming_dict[i]+"weather.pdf")
'''
