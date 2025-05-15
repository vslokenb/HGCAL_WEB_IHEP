import asyncio
import asyncpg
import yaml
from datetime import datetime
import matplotlib.pyplot as plt

# Load configuration
configuration = {}
with open('dbase_info/conn.yaml', 'r') as file:
    configuration = yaml.safe_load(file)

async def fetch_module_info(ass_date_start):
    # instantiate db connection  
    conn = await asyncpg.connect(
            host = configuration['db_hostname'],
            database = configuration['dbname'],
            user = 'viewer',  # Use appropriate username
            password = configuration['DBPassword']
        )
    
    ass_date = datetime.strptime(ass_date_start, '%Y-%m-%d').date()

    # Get list of module names
    query_modules = """SELECT module_name FROM module_info WHERE assembled >= $1 ;"""
    result = await conn.fetch(query_modules, ass_date)
    module_names_array = [row['module_name'] for row in result]

    # Initialize dictionaries for storing the data
    v_info = {}
    i_info = {}
    adc_stdd = {}
    adc_mean = {}

    # Fetch the latest measurements for each module
    for i in module_names_array:
        query_v_scan = """SELECT meas_v FROM module_iv_test WHERE module_name=$1 ORDER BY date_test DESC LIMIT 1;"""
        query_i_scan = """SELECT meas_i FROM module_iv_test WHERE module_name=$1 ORDER BY date_test DESC LIMIT 1;"""
        query_adc_mean = """SELECT adc_mean FROM module_pedestal_test WHERE module_name=$1 ORDER BY date_test DESC LIMIT 1;"""
        query_adc_stdd = """SELECT adc_stdd FROM module_pedestal_test WHERE module_name=$1 ORDER BY date_test DESC LIMIT 1;"""
        
        # Fetch values
        result_v = await conn.fetch(query_v_scan, i)
        result_i = await conn.fetch(query_i_scan, i)
        result_adc_stdd = await conn.fetch(query_adc_stdd, i)
        result_adc_mean = await conn.fetch(query_adc_mean, i)
        
        # Assign data or empty list if no result
        v_info[i] = result_v[0]['meas_v'] if result_v else []
        i_info[i] = result_i[0]['meas_i'] if result_i else []
        adc_stdd[i] = result_adc_stdd[0]['adc_stdd'] if result_adc_stdd else []
        adc_mean[i] = result_adc_mean[0]['adc_mean'] if result_adc_mean else []
    
    await conn.close()
    return module_names_array, v_info, i_info, adc_stdd, adc_mean

def plot_iv_summary(module_names_array, v_info, i_info, ass_date_start):
    fig, ax = plt.subplots()
    for module in module_names_array:
        v = v_info.get(module, [])
        i = i_info.get(module, [])
        if v and i:  # Only plot if data exists
            ax.plot(v, i, label=module)
    
    ax.set_xlim(0, 850)
    ax.set_title(f'IV Summary of production since {ass_date_start}')
    ax.set_yscale('log')
    ax.set_xlabel('V')
    ax.set_ylabel('I [A]')
    ax.legend(fontsize='small')
    plt.show()
    return fig

def plot_adc_noise(module_names_array, adc_stdd, ass_date_start):
    fig, ax = plt.subplots()
    for module in module_names_array:
        std = adc_stdd.get(module, [])
        if std:
            ax.hist(std, bins=20, alpha=0.7, label=module)

    ax.set_xlim(0, 50)
    ax.set_title(f'ADC Noise - Summary of production since {ass_date_start}')
    ax.set_xlabel('ADC Standard Deviation')
    ax.set_ylabel('Frequency')
    ax.legend(fontsize='small')
    plt.show()
    return fig

def plot_adc_mean(module_names_array, adc_mean, ass_date_start):
    fig, ax = plt.subplots()
    for module in module_names_array:
        mean = adc_mean.get(module, [])
        if mean:
            ax.hist(mean, bins=20, alpha=0.7, label=module)
    
    ax.set_xlim(0, 500)
    ax.set_title(f'ADC Mean - Summary of production since {ass_date_start}')
    ax.set_xlabel('ADC Mean')
    ax.set_ylabel('Frequency')
    ax.legend(fontsize='small')
    plt.show()
    return fig

# Example of calling the functions
async def plot_workflow(ass_date_start):
    # Fetch data from PostgreSQL
    module_names_array, v_info, i_info, adc_stdd, adc_mean = await fetch_module_info(ass_date_start)
    
    # Plot the IV curve summary
    iv=plot_iv_summary(module_names_array, v_info, i_info, ass_date_start)
    
    # Plot ADC noise summary
    noise=plot_adc_noise(module_names_array, adc_stdd, ass_date_start)
    
    # Plot ADC mean summary
    mean=plot_adc_mean(module_names_array, adc_mean, ass_date_start)
    
    return iv,noise,mean