import asyncpg
import asyncio
import yaml
#import ROOT
from datetime import datetime
from array import array
#import uproot
import matplotlib.pyplot as plt
import argparse
import numpy as np


#from fastapi import FastAPI
##from fastapi.responses import JSONResponse, HTMLResponse
#from fastapi.templating import Jinja2Templates
#from fastapi import Request
#app = FastAPI()

#templates = Jinja2Templates(directory="templates")

configuration = {}
with open('dbase_info/conn.yaml', 'r') as file:
    configuration = yaml.safe_load(file)

async def inventory_tracker(ass_date_start):
    conn = await asyncpg.connect(
            host = configuration['db_hostname'],
            database = configuration['dbname'],
            user = 'viewer', #configuration['postg']
            password = configuration['DBPassword']
        )
    ass_date = datetime.strptime(ass_date_start, '%Y-%m-%d').date()
    try:
        module_counting=f"""SELECT COUNT(*) from module_info WHERE assembled >= $1 ;"""
        module_count=await conn.fetch(module_counting,ass_date)
        print("number of modules assembled since start of v3b: ",module_count[0]['count'])

        hxb_counting=f"""SELECT COUNT(*) from hexaboard WHERE module_no >= 1;"""
        hxb_sum=await conn.fetch("""SELECT COUNT(*) from hexaboard;""")
        hxb_total=hxb_sum[0]['count'] - 12
        hxb_count=await conn.fetch(hxb_counting)
        print("number of hxb used since start of v3b: ",hxb_count[0]['count'])

        proto_counting=f"""SELECT COUNT(*) from proto_assembly WHERE ass_run_date >= $1 ;"""
        proto_count=await conn.fetch(proto_counting,ass_date)
        print("number of protomodules assembled since start of v3b: ",proto_count[0]['count'])

        bp_counting=f"""SELECT COUNT(*) from baseplate WHERE proto_no > 12 ;"""
        bp_count=await conn.fetch(bp_counting)
        bp_sum=await conn.fetch("""SELECT COUNT(*) from baseplate;""")
        bp_total=bp_sum[0]['count'] - 12
        print("number of baseplates used since start of v3b: ",bp_count[0]['count'])

        sens_counting=f"""SELECT COUNT(*) from sensor WHERE proto_no > 12 ;"""
        sens_count=await conn.fetch(sens_counting)
        sens_sum=await conn.fetch("""SELECT COUNT(*) from sensor;""")
        sens_total=sens_sum[0]['count'] - 12
        print("number of sensors used since start of v3b: ",sens_count[0]['count'])
    
        return [ {
        "module count": module_count[0]['count'],
        "protomodule count": proto_count[0]['count'],
        "hexaboard usage": f"{hxb_count[0]['count']} of {hxb_total}",
        "baseplate usage": f"{bp_count[0]['count']} of {bp_total}",
        "sensor usage": f"{sens_count[0]['count']} of {sens_total}"

        }]
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        await conn.close()

async def list_complete_module():
    conn = await asyncpg.connect(
            host = configuration['db_hostname'],
            database = configuration['dbname'],
            user = 'viewer', #configuration['postg']
            password = configuration['DBPassword']
        )
    assemb_date = datetime.strptime('2025-03-04', '%Y-%m-%d').date()#datetime.strptime(ass_date_start, '%Y-%m-%d').date()
    try:
        module_listing=f"""SELECT module_name,proto_name,hxb_name,roc_version,sen_name,bp_name,bp_material,assembled from module_info WHERE assembled >= $1 ORDER BY assembled DESC;"""
        module_list=await conn.fetch(module_listing,assemb_date)
        result = [dict(record) for record in module_list]
        #print("list of modules assembled since start of v3b: ",module_list['module_name'])

    
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        await conn.close()

async def status_complete():
    conn = await asyncpg.connect(
            host = configuration['db_hostname'],
            database = configuration['dbname'],
            user = 'viewer', #configuration['postg']
            password = configuration['DBPassword']
        )
    assemb_date = datetime.strptime('2025-03-04', '%Y-%m-%d').date()#datetime.strptime(ass_date_start, '%Y-%m-%d').date()
    try:
        donemodule_listing=f"""SELECT module_name 
        FROM module_info 
        WHERE 
            wb_back IS NOT NULL AND
            encap_back IS NOT NULL AND
            wb_front IS NOT NULL AND
            encap_front IS NOT NULL
        ORDER BY assembled DESC;"""
        donemodule_list=await conn.fetch(donemodule_listing)
        result = [dict(record) for record in donemodule_list]
        #print("list of modules assembled since start of v3b: ",module_list['module_name'])

    
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        await conn.close()

async def status_wb_back():
    conn = await asyncpg.connect(
            host = configuration['db_hostname'],
            database = configuration['dbname'],
            user = 'viewer', #configuration['postg']
            password = configuration['DBPassword']
        )
    assemb_date = datetime.strptime('2025-03-04', '%Y-%m-%d').date()#datetime.strptime(ass_date_start, '%Y-%m-%d').date()
    try:
        donemodule_listing=f"""SELECT module_name 
        FROM module_info 
        WHERE 
            wb_back IS NOT NULL AND
            encap_back IS NULL AND
            wb_front IS NULL AND
            encap_front IS NULL
        ORDER BY assembled DESC;"""
        donemodule_list=await conn.fetch(donemodule_listing)
        result = [dict(record) for record in donemodule_list]
        #print("list of modules assembled since start of v3b: ",module_list['module_name'])

    
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        await conn.close()

async def status_wb_front():
    conn = await asyncpg.connect(
            host = configuration['db_hostname'],
            database = configuration['dbname'],
            user = 'viewer', #configuration['postg']
            password = configuration['DBPassword']
        )
    assemb_date = datetime.strptime('2025-03-04', '%Y-%m-%d').date()#datetime.strptime(ass_date_start, '%Y-%m-%d').date()
    try:
        donemodule_listing=f"""SELECT module_name 
        FROM module_info 
        WHERE 
            wb_back IS NOT NULL AND
            encap_back IS NOT NULL AND
            wb_front IS NOT NULL AND
            encap_front IS NULL
        ORDER BY assembled DESC;"""
        donemodule_list=await conn.fetch(donemodule_listing)
        result = [dict(record) for record in donemodule_list]
        #print("list of modules assembled since start of v3b: ",module_list['module_name'])

    
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        await conn.close()
async def status_encap_back():
    conn = await asyncpg.connect(
            host = configuration['db_hostname'],
            database = configuration['dbname'],
            user = 'viewer', #configuration['postg']
            password = configuration['DBPassword']
        )
    #assemb_date = datetime.strptime('2025-03-04', '%Y-%m-%d').date()#datetime.strptime(ass_date_start, '%Y-%m-%d').date()
    try:
        donemodule_listing=f"""SELECT module_name 
        FROM module_info 
        WHERE 
            wb_back IS NOT NULL AND
            encap_back IS NOT NULL AND
            wb_front IS NULL AND
            encap_front IS NULL
        ORDER BY assembled DESC;"""
        donemodule_list=await conn.fetch(donemodule_listing)
        result = [dict(record) for record in donemodule_list]
        #print("list of modules assembled since start of v3b: ",module_list['module_name'])

    
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        await conn.close()