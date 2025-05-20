import asyncio
import asyncpg
import yaml
from datetime import datetime
import matplotlib.pyplot as plt



configuration = {}
with open('dbase_info/conn.yaml', 'r') as file:
    configuration = yaml.safe_load(file)
async def fetch_iv_grade(ass_date_start,cut1,cut2,name=[]):
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
    #v_info = {}
    i_ratio = {}
    if name!=[]:
        module_names_array=name
    for i in module_names_array:
        print(i)
        voltage_target1 = 600  # for example
        result1 = await conn.fetchval(
        """
SELECT 
  meas_i[array_position(program_v, 600)] AS current_at_600v
FROM module_iv_test
WHERE module_name = $1
ORDER BY date_test DESC        """,
        i,
        )
        print(f"Current at {voltage_target1} V: {result1} µA")
        voltage_target2 = 800  # for example
        result2 = await conn.fetchval(
        """
        SELECT 
  meas_i[array_position(program_v, 800)] AS current_at_800v
FROM module_iv_test
WHERE module_name = $1
ORDER BY date_test DESC
        """,
        i
        )
        print(f"Current at {voltage_target2} V: {result2} µA")
        try:
            print(result2 / result1)
        except:
    
            print("untested")
        if result2 is not None:
            if result2 / result1 <= 2.5 and result1 < cut1:
                i_ratio[i] = "A"
            elif result1 < cut2:
                i_ratio[i] = "B"
            elif result1 >= 0. :
                i_ratio[i] = "C"
        else:
            i_ratio[i]=[]
    return i_ratio
#test=asyncio.run(fetch_iv_grade('2025-05-01',0.0001,0.001))
#print(test)
