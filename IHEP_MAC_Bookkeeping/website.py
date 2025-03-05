import streamlit as st
import csv
import pandas as pd
import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Initialize flag status as global variables
ogp_before_assembly_flags = {
    'Visual inspection for damage and thickness for sensor': 'red',
    'Thickness and inspection for baseplate': 'red',
    'Thickness and inspection for hexboard': 'red',
    'Cleaning of Sensor, baseplate and Hexa- board': 'red'
}

# Flag for the OGP Check List title
assembly1_flags={
    "Gluing of Silicon Sensor on base plate":"red",
}

ogp_after_assembly1_flags = {
    'Inspection of glued Base plate + Sensor': "red",
}

assembly2_flags={
    "Gluing of Hexa-board on Protomodule":"red",
}

ogp_after_assembly2_flags = {
    'Inspection of Module': "red",
}

electrical_before_backside_bonding_flags={
    'delay scan':'red',
    'pedestal run':'red',
}

Backside_bonding_flags={
    'Backside Wire Bonding of the module':'red',
}
ogp_after_backside_bonding_flags={
    'Visual Inspection of backside wirebonds':'red',
}

Backside_encapsolation_flags={
    'Encapsulation of backside and curing':'red'
}

ogp_after_backside_encapsolation_flags={
    'Visual Inspection of backside encapsulation':'red',
}

Pull_test_flags={
    'Pull Testing for frontside bonding':'red',
}

Frontside_bonding_flags={
    'Wire Bonding frontside of the module':'red',
}

OGP_after_frontside_bounding_flags={
    'Visual Inspection of Bonded module before encapsulation':
    'red'
}

Module_encapsolation_flags={
    'Encapsulation of the module and curing':'red',
}

OGP_after_module_encapsolation_flags={
    'Visual Inspection of encapsulated module':'red',
}

Final_electrical_test_flags={
    "Electrical Test of the final module":'red',
    'IV Curves':'red',
    'Single Module Test Stand':'red'
}
click_counts_ogp_before_assembly = {step: 0 for step in ogp_before_assembly_flags}
click_counts_assembly1={step: 0 for step in assembly1_flags}
click_counts_ogp_after_assembly1={step: 0 for step in ogp_after_assembly1_flags}
click_counts_assembly2={step: 0 for step in assembly2_flags}
click_counts_ogp_after_assembly2={step: 0 for step in ogp_after_assembly2_flags}
click_counts_electrical_before_backside_bonding={step: 0 for step in electrical_before_backside_bonding_flags}
click_counts_Backside_bonding={step: 0 for step in Backside_bonding_flags}
click_counts_ogp_after_backside_bonding={step: 0 for step in ogp_after_backside_bonding_flags}
click_counts_Backside_encapsolation={step: 0 for step in Backside_encapsolation_flags}
click_counts_ogp_after_backside_encapsolation={step: 0 for step in ogp_after_backside_encapsolation_flags}
click_counts_Pull_test={step: 0 for step in Pull_test_flags}
click_counts_Frontside_bonding={step: 0 for step in Frontside_bonding_flags}
click_counts_OGP_after_frontside_bounding={step: 0 for step in OGP_after_frontside_bounding_flags}
click_counts_Module_encapsolation={step: 0 for step in Module_encapsolation_flags}
click_counts_OGP_after_module_encapsolation={step: 0 for step in OGP_after_module_encapsolation_flags}
click_counts_Final_electrical_test={step: 0 for step in Final_electrical_test_flags}
###############################################################################################
def read_user_group(username):
    user_info = pd.read_csv("user_info.csv")
    user_group = user_info.loc[user_info['username'] == username, 'group'].values
    return user_group[0] if len(user_group) > 0 else None
##################################################################################################

def authenticate_user(username, password):
    user_info = pd.read_csv("user_info.csv")   
    user_info['password'] = user_info['password'].astype(str) 
    print(user_info['username'])
    print(user_info['password'])
    if ((user_info['username'] == username) & (user_info['password'] == password)).any():
        return True
    else:
        return False
#################################################################################################

def initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number,remeasurement_number):
    if os.path.exists("output.csv"):
        existing_flags_df = pd.read_csv("output.csv", dtype={'Module Number': str, 'Sensor ID': str, 'Hexboard Number': str, 'Baseplate Number': str, 'Remeasurement Number':str})

        existing_flags = existing_flags_df[
            (existing_flags_df['Module Number'] == module_number) &
            (existing_flags_df['Sensor ID'] == sensor_id) &
            (existing_flags_df['Hexboard Number'] == hexboard_number) &
            (existing_flags_df['Baseplate Number'] == baseplate_number)&
            (existing_flags_df['Remeasurement Number'] == remeasurement_number)
        ]

        if not existing_flags.empty:
            for index, row in existing_flags.iterrows():
                step_ = row['Step']
                flag_ = row['Flag']
                # Update the flags if found in existing data
                for flags in [ogp_before_assembly_flags, assembly1_flags, ogp_after_assembly1_flags,
    assembly2_flags, ogp_after_assembly2_flags, electrical_before_backside_bonding_flags,
    Backside_bonding_flags, ogp_after_backside_bonding_flags,
    Backside_encapsolation_flags, ogp_after_backside_encapsolation_flags,
    Pull_test_flags, Frontside_bonding_flags, OGP_after_frontside_bounding_flags,
    Module_encapsolation_flags, OGP_after_module_encapsolation_flags,
    Final_electrical_test_flags]:
                    if step_ in flags:
                        flags[step_] = flag_
        else:
            # Set default values for all flags if not found in existing data
            for flags in [ogp_before_assembly_flags, assembly1_flags, ogp_after_assembly1_flags,
    assembly2_flags, ogp_after_assembly2_flags, electrical_before_backside_bonding_flags,
    Backside_bonding_flags, ogp_after_backside_bonding_flags,
    Backside_encapsolation_flags, ogp_after_backside_encapsolation_flags,
    Pull_test_flags, Frontside_bonding_flags, OGP_after_frontside_bounding_flags,
    Module_encapsolation_flags, OGP_after_module_encapsolation_flags,
    Final_electrical_test_flags]:
                for step_ in flags:
                    flags[step_] = 'red'
#################################################################################################

def Module_Assembly_Check_List(username):
    st.title("Welcome to the HGCal module assembly")
    module_number = st.text_input("Enter Module Number")
    sensor_id = st.text_input("Enter Sensor ID")
    hexboard_number = st.text_input("Enter Hexboard Number")
    baseplate_number = st.text_input("Enter Baseplate Number")
    remeasurement_number=st.text_input("Enter Remeasurement Number(0 for the first measurement)")
    comment = st.text_input("Entre Comment(Can be empty)")
    usergroup=read_user_group(username)
        # Checkbox to submit the details
    if st.checkbox("Submit"):
        if module_number and sensor_id and hexboard_number and baseplate_number and remeasurement_number:
            option1=st.selectbox("Select an option", ("Overview","OGP before assembly","Assembly1","OGP after assembly1","Assembly2","OGP after assembly2","Electrical before backside bonding","Backside bonding","OGP after backside bonding","Backside encapsolation","OGP after backside encapsolation","Pull test","Frontside bonding","OGP after frontside bonding","Module encapsolation","OGP after module encapsolation","Final electrical test"),key="option1")
            if option1=='Overview':
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                ogp_before_assembly_completed = all(flag == 'green' for flag in ogp_before_assembly_flags.values())
                Ogp_Before_Assembly_Flag = 'green' if ogp_before_assembly_completed else 'red'
                Ogp_Before_Assembly_Icon = '\u2705' if Ogp_Before_Assembly_Flag == 'green' else '\u274C'
                st.header(f"OGP Before Assembly: {Ogp_Before_Assembly_Icon}")


                assembly1_steps_completed = all(flag == 'green' for flag in assembly1_flags.values())
                Assembly1_Checklist_Flag = 'green' if assembly1_steps_completed else 'red'
                Assembly1_Flag_Icon = '\u2705' if Assembly1_Checklist_Flag == 'green' else '\u274C'
                st.header(f"Assembly1: {Assembly1_Flag_Icon}")

                ogp_after_assembly1_steps_completed = (all(flag == 'green' for flag in ogp_after_assembly1_flags.values()))
                Ogp_After_Assembly1_Checklist_Flag = 'green' if ogp_after_assembly1_steps_completed else 'red'
                Ogp_After_Assembly1_Checklist_Flag_Icon = '\u2705' if Ogp_After_Assembly1_Checklist_Flag == 'green' else '\u274C'
                st.header(f"Ogp After Assembly1: {Ogp_After_Assembly1_Checklist_Flag_Icon}")

                assembly2_steps_completed = (all(flag == 'green' for flag in assembly2_flags.values()))
                Assembly2_Checklist_Flag = 'green' if assembly2_steps_completed else 'red'
                Assembly2_Checklist_Flag_Icon = '\u2705' if Assembly2_Checklist_Flag == 'green' else '\u274C'
                st.header(f"Assembly2: {Assembly2_Checklist_Flag_Icon}")

                ogp_after_assembly2_steps_completed = (all(flag == 'green' for flag in ogp_after_assembly2_flags.values()))
                Ogp_After_Assembly2_Flags = 'green' if ogp_after_assembly2_steps_completed else 'red'
                Ogp_After_Assembly2_Flags_Icon = '\u2705' if Ogp_After_Assembly2_Flags == 'green' else '\u274C'
                st.header(f"Ogp After Assembly2: {Ogp_After_Assembly2_Flags_Icon}")

                electrical_before_backside_bonding_steps_completed = (all(flag == 'green' for flag in ogp_after_assembly2_flags.values()))
                Electrical_Before_Backside_Bonding_Flags = 'green' if electrical_before_backside_bonding_steps_completed else 'red'
                Electrical_Before_Backside_Bonding_Flags_Icon = '\u2705' if Electrical_Before_Backside_Bonding_Flags == 'green' else '\u274C'
                st.header(f"Electrical test Before Backside Bonding: {Electrical_Before_Backside_Bonding_Flags_Icon}")

                Backside_bonding_steps_completed = (all(flag == 'green' for flag in Backside_bonding_flags.values()))
                Backside_Bonding_Flags = 'green' if Backside_bonding_steps_completed else 'red'
                Backside_Bonding_Flags_Icon = '\u2705' if Backside_Bonding_Flags == 'green' else '\u274C'
                st.header(f"Backside_Bonding: {Backside_Bonding_Flags_Icon}")

                ogp_after_backside_bonding_steps_completed = (all(flag == 'green' for flag in ogp_after_backside_bonding_flags.values()))
                Ogp_After_Backside_Bonding_Flags = 'green' if ogp_after_backside_bonding_steps_completed else 'red'
                Ogp_After_Backside_Bonding_Flags_Icon = '\u2705' if Ogp_After_Backside_Bonding_Flags == 'green' else '\u274C'
                st.header(f"Ogp After Backside Bonding: {Ogp_After_Backside_Bonding_Flags_Icon}")

                Backside_encapsolation_steps_completed = (all(flag == 'green' for flag in Backside_encapsolation_flags.values()))
                Backside_Encapsolation_Flags = 'green' if Backside_encapsolation_steps_completed else 'red'
                Backside_Encapsolation_Flags_Icon = '\u2705' if Backside_Encapsolation_Flags == 'green' else '\u274C'
                st.header(f"Backside Encapsolation: {Backside_Encapsolation_Flags_Icon}")

                ogp_after_backside_encapsolation_steps_completed = (all(flag == 'green' for flag in ogp_after_backside_encapsolation_flags.values()))
                Ogp_After_Backside_Encapsolation_Flags = 'green' if ogp_after_backside_encapsolation_steps_completed else 'red'
                Ogp_After_Backside_Encapsolation_Flags_Icon = '\u2705' if Ogp_After_Backside_Encapsolation_Flags == 'green' else '\u274C'
                st.header(f"Ogp after backside encapsolation: {Ogp_After_Backside_Encapsolation_Flags_Icon}")

                Pull_test_steps_completed = (all(flag == 'green' for flag in Pull_test_flags.values()))
                Pull_Test_Flags = 'green' if Pull_test_steps_completed else 'red'
                Pull_Test_Flags_Icon = '\u2705' if Pull_Test_Flags == 'green' else '\u274C'
                st.header(f"Pull Test: {Pull_Test_Flags_Icon}")

                Frontside_bonding_steps_completed = (all(flag == 'green' for flag in Frontside_bonding_flags.values()))
                Frontside_Bonding_Flags = 'green' if Frontside_bonding_steps_completed else 'red'
                Frontside_Bonding_Flags_Icon = '\u2705' if Frontside_Bonding_Flags == 'green' else '\u274C'
                st.header(f"Frontside Bonding: {Frontside_Bonding_Flags_Icon}")

                OGP_after_frontside_bounding_steps_completed = (all(flag == 'green' for flag in OGP_after_frontside_bounding_flags.values()))
                OGP_After_Frontside_Bounding_Flags = 'green' if OGP_after_frontside_bounding_steps_completed else 'red'
                OGP_After_Frontside_Bounding_Flags_Icon = '\u2705' if OGP_After_Frontside_Bounding_Flags == 'green' else '\u274C'
                st.header(f"OGP After Frontside Bounding: {OGP_After_Frontside_Bounding_Flags_Icon}")

                Module_encapsolation_steps_completed = (all(flag == 'green' for flag in Module_encapsolation_flags.values()))
                Module_Encapsolation_Flags = 'green' if Module_encapsolation_steps_completed else 'red'
                Module_Encapsolation_Flags_Icon = '\u2705' if Module_Encapsolation_Flags == 'green' else '\u274C'
                st.header(f"Module Encapsolation: {Module_Encapsolation_Flags_Icon}")

                OGP_after_module_encapsolation_steps_completed = (all(flag == 'green' for flag in OGP_after_module_encapsolation_flags.values()))
                OGP_After_Module_Encapsolation_Flags = 'green' if OGP_after_module_encapsolation_steps_completed else 'red'
                OGP_After_Module_Encapsolation_Flags_Icon = '\u2705' if OGP_After_Module_Encapsolation_Flags == 'green' else '\u274C'
                st.header(f"OGP After Module Encapsolation: {OGP_After_Module_Encapsolation_Flags_Icon}")

                Final_electrical_test_steps_completed = (all(flag == 'green' for flag in Final_electrical_test_flags.values()))
                Final_Electrical_Test_Flags = 'green' if Final_electrical_test_steps_completed else 'red'
                Final_Electrical_Test_Flags_Icon = '\u2705' if Final_Electrical_Test_Flags == 'green' else '\u274C'
                st.header(f"Final Electrical Test: {Final_Electrical_Test_Flags_Icon}")


            if option1=="OGP before assembly":
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                OGP_before_assembly(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment)
            if option1=="Assembly1":
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Assembly1(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment)
            if option1=='OGP after assembly1':
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                OGP_after_assembly1(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment)
            if option1=='Assembly2':
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Assembly2(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment)
            if option1=='OGP after assembly2':
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                OGP_after_assembly2(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment)
            if option1=='Electrical before backside bonding':
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Electrical_before_backside_bonding(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment)
            if option1=='Backside bonding':
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Backside_bonding(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment)
            if option1=='OGP after backside bonding':
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Ogp_after_backside_bonding(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment)
            if option1=='Backside encapsolation':
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Backside_encapsolation(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment)
            if option1=='OGP after backside encapsolation':
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Ogp_after_backside_encapsolation(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment)
            if option1=='Pull test':
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Pull_test(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment)
            if option1=='Frontside bonding':
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Frontside_bonding(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment)
            if option1=='OGP after frontside bonding':
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                OGP_after_frontside_bounding(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment)
            if option1=='Module encapsolation':
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Module_encapsolation(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment)
            if option1=='OGP after module encapsolation':
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                OGP_after_module_encapsolation(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment)
            if option1=='Final electrical test':
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Final_electrical_test(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment)

#######################################################################################################
def OGP_before_assembly(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment):
    if(read_user_group(username) == 'OGP' or read_user_group(username) == 'All'):
        for step, flag in ogp_before_assembly_flags.items():
            selected_flag = st.selectbox(f"{step} Flag:", ['green', 'yellow', 'red'], index=['green', 'yellow', 'red'].index(flag), key=f'{step}_selectbox', help=f'Click count: {click_counts_ogp_before_assembly[step]}')
            
            # Update flag and click count based on selected option
            ogp_before_assembly_flags[step] = selected_flag
            click_counts_ogp_before_assembly[step] += 1

        for step, flag in ogp_before_assembly_flags.items():
            ogp_before_assembly_flag_icon = '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C'
            st.write(f"{step}: {ogp_before_assembly_flag_icon}")

    ogp_before_assembly_completed = all(flag == 'green' for flag in ogp_before_assembly_flags.values())
    Ogp_Before_Assembly_Flag = 'green' if ogp_before_assembly_completed else 'red'

    Ogp_Before_Assembly_Icon = '\u2705' if Ogp_Before_Assembly_Flag == 'green' else '\u274C'
    st.header(f"OGP Before Assembly Check List: {Ogp_Before_Assembly_Icon}")

    if st.button("Save Flags to File"):
        all_checklists_flags = {
                'OGP before assembly': ogp_before_assembly_flags,
                'Assembly1':assembly1_flags,
                'OGP after assembly1':ogp_after_assembly1_flags,
                'Assembly2':assembly2_flags,
                'OGP after assembly2':ogp_after_assembly2_flags,
                'Electrical before backside bonding':electrical_before_backside_bonding_flags,
                'Backside bonding':Backside_bonding_flags,
                'OGP after backside bonding':ogp_after_backside_bonding_flags,
                'Backside encapsolation':Backside_encapsolation_flags,
                'OGP after backside encapsolation':ogp_after_backside_encapsolation_flags,
                'Pull test':Pull_test_flags,
                'Frontside bonding':Frontside_bonding_flags,
                'OGP after frontside bonding':OGP_after_frontside_bounding_flags,
                'Module encapsolation':Module_encapsolation_flags,
                'OGP after module encapsolation':OGP_after_module_encapsolation_flags,
                'Final electrical test':Final_electrical_test_flags
            }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
                   
        save_flags_to_file(all_checklists_flags, details,"output.csv",username,usergroup,comment)
        find_unfinished_modules()
#####################################################################################################################################
def Assembly1(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment):

    ogp_before_assembly_completed = all(flag == 'green' for flag in ogp_before_assembly_flags.values())
    Ogp_Before_Assembly_Flag = 'green' if ogp_before_assembly_completed else 'red'

    if Ogp_Before_Assembly_Flag=='red':
        st.write("Please finish the previous step first")

    if (read_user_group(username)=='Gantry' or read_user_group(username)=='All') and Ogp_Before_Assembly_Flag=='green':
        for step, flag in assembly1_flags.items():
            selected_flag = st.selectbox(f"{step} Flag:", ['green', 'yellow', 'red'], index=['green', 'yellow', 'red'].index(flag), key=f'{step}_selectbox', help=f'Click count: {click_counts_assembly1[step]}')
            assembly1_flags[step] = selected_flag
            click_counts_assembly1[step] += 1

        for step, flag in assembly1_flags.items():
            assembly_flag_icon = '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C'
            st.write(f"{step}: {assembly_flag_icon}")

    assembly1_steps_completed = (all(flag == 'green' for flag in assembly1_flags.values()))
    Assembly1_Checklist_Flag = 'green' if assembly1_steps_completed else 'red'
    Assembly1_Flag_Icon = '\u2705' if Assembly1_Checklist_Flag == 'green' else '\u274C'
    st.header(f"Assembly Check List: {Assembly1_Flag_Icon}")

    if st.button("Save Flags to File"):
        all_checklists_flags = {
                'OGP before assembly': ogp_before_assembly_flags,
                'Assembly1':assembly1_flags,
                'OGP after assembly1':ogp_after_assembly1_flags,
                'Assembly2':assembly2_flags,
                'OGP after assembly2':ogp_after_assembly2_flags,
                'Electrical before backside bonding':electrical_before_backside_bonding_flags,
                'Backside bonding':Backside_bonding_flags,
                'OGP after backside bonding':ogp_after_backside_bonding_flags,
                'Backside encapsolation':Backside_encapsolation_flags,
                'OGP after backside encapsolation':ogp_after_backside_encapsolation_flags,
                'Pull test':Pull_test_flags,
                'Frontside bonding':Frontside_bonding_flags,
                'OGP after frontside bonding':OGP_after_frontside_bounding_flags,
                'Module encapsolation':Module_encapsolation_flags,
                'OGP after module encapsolation':OGP_after_module_encapsolation_flags,
                'Final electrical test':Final_electrical_test_flags
            }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
                   
        save_flags_to_file(all_checklists_flags, details,"output.csv",username,usergroup,comment)
        find_unfinished_modules()
######################################################################################################################################
def OGP_after_assembly1(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment):
    assembly1_steps_completed = all(flag == 'green' for flag in assembly1_flags.values())
    Assembly1_Checklist_Flag = 'green' if assembly1_steps_completed else 'red'

    if Assembly1_Checklist_Flag=='red':
        st.write("Please finish the previous step first")

    if (read_user_group(username)=='OGP' or read_user_group(username)=='All') and Assembly1_Checklist_Flag=='green':
        for step, flag in ogp_after_assembly1_flags.items():

            selected_flag = st.selectbox(f"{step} Flag:", ['green', 'yellow', 'red'], index=['green', 'yellow', 'red'].index(flag), key=f'{step}_selectbox', help=f'Click count: {click_counts_ogp_after_assembly1[step]}')
            ogp_after_assembly1_flags[step] = selected_flag
            click_counts_ogp_after_assembly1[step] += 1

        for step, flag in ogp_after_assembly1_flags.items():
            ogp_after_assembly1_flags_icon ='\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C'
            st.write(f"{step}: {ogp_after_assembly1_flags_icon}")

    ogp_after_assembly1_steps_completed = (all(flag == 'green' for flag in ogp_after_assembly1_flags.values()))
    Ogp_After_Assembly1_Checklist_Flag = 'green' if ogp_after_assembly1_steps_completed else 'red'
    Ogp_After_Assembly1_Checklist_Flag_Icon = '\u2705' if Ogp_After_Assembly1_Checklist_Flag == 'green' else '\u274C'
    st.header(f"Assembly Check List: {Ogp_After_Assembly1_Checklist_Flag_Icon}")

    if st.button("Save Flags to File"):
        all_checklists_flags = {
                'OGP before assembly': ogp_before_assembly_flags,
                'Assembly1':assembly1_flags,
                'OGP after assembly1':ogp_after_assembly1_flags,
                'Assembly2':assembly2_flags,
                'OGP after assembly2':ogp_after_assembly2_flags,
                'Electrical before backside bonding':electrical_before_backside_bonding_flags,
                'Backside bonding':Backside_bonding_flags,
                'OGP after backside bonding':ogp_after_backside_bonding_flags,
                'Backside encapsolation':Backside_encapsolation_flags,
                'OGP after backside encapsolation':ogp_after_backside_encapsolation_flags,
                'Pull test':Pull_test_flags,
                'Frontside bonding':Frontside_bonding_flags,
                'OGP after frontside bonding':OGP_after_frontside_bounding_flags,
                'Module encapsolation':Module_encapsolation_flags,
                'OGP after module encapsolation':OGP_after_module_encapsolation_flags,
                'Final electrical test':Final_electrical_test_flags
            }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
                   
        save_flags_to_file(all_checklists_flags, details,"output.csv",username,usergroup,comment)
        find_unfinished_modules()
######################################################################################################################################
def Assembly2(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment):
    ogp_after_assembly1_steps_completed = (all(flag == 'green' for flag in ogp_after_assembly1_flags.values()))
    Ogp_After_Assembly1_Checklist_Flag = 'green' if ogp_after_assembly1_steps_completed else 'red'

    if Ogp_After_Assembly1_Checklist_Flag=='red':
        st.write("Please finish the previous step first")

    if (read_user_group(username)=='Gantry' or read_user_group(username)=='All') and Ogp_After_Assembly1_Checklist_Flag=='green':
        for step, flag in assembly2_flags.items():
            selected_flag = st.selectbox(f"{step} Flag:", ['green', 'yellow', 'red'], index=['green', 'yellow', 'red'].index(flag), key=f'{step}_selectbox', help=f'Click count: {click_counts_assembly2[step]}')
            assembly2_flags[step] = selected_flag
            click_counts_assembly2[step] += 1

        for step, flag in assembly2_flags.items():
            assembly2_flags_icon = '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C'
            st.write(f"{step}: {assembly2_flags_icon}")

    assembly2_steps_completed = (all(flag == 'green' for flag in assembly2_flags.values()))
    Assembly2_Checklist_Flag = 'green' if assembly2_steps_completed else 'red'

    Assembly2_Checklist_Flag_Icon = '\u2705' if Assembly2_Checklist_Flag == 'green' else '\u274C'
    st.header(f"Assembly Check List: {Assembly2_Checklist_Flag_Icon}")

    if st.button("Save Flags to File"):
        all_checklists_flags = {
                'OGP before assembly': ogp_before_assembly_flags,
                'Assembly1':assembly1_flags,
                'OGP after assembly1':ogp_after_assembly1_flags,
                'Assembly2':assembly2_flags,
                'OGP after assembly2':ogp_after_assembly2_flags,
                'Electrical before backside bonding':electrical_before_backside_bonding_flags,
                'Backside bonding':Backside_bonding_flags,
                'OGP after backside bonding':ogp_after_backside_bonding_flags,
                'Backside encapsolation':Backside_encapsolation_flags,
                'OGP after backside encapsolation':ogp_after_backside_encapsolation_flags,
                'Pull test':Pull_test_flags,
                'Frontside bonding':Frontside_bonding_flags,
                'OGP after frontside bonding':OGP_after_frontside_bounding_flags,
                'Module encapsolation':Module_encapsolation_flags,
                'OGP after module encapsolation':OGP_after_module_encapsolation_flags,
                'Final electrical test':Final_electrical_test_flags
            }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
                   
        save_flags_to_file(all_checklists_flags, details,"output.csv",username,usergroup,comment)
        find_unfinished_modules()
###############################################################################################################################
def OGP_after_assembly2(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment):
    assembly2_steps_completed = (all(flag == 'green' for flag in assembly2_flags.values()))
    Assembly2_Checklist_Flag = 'green' if assembly2_steps_completed else 'red'

    if Assembly2_Checklist_Flag=='red':
        st.write("Please finish the previous step first")

    if (read_user_group(username)=='OGP' or read_user_group(username)=='All') and Assembly2_Checklist_Flag=='green':
        for step, flag in ogp_after_assembly2_flags.items():

            selected_flag = st.selectbox(f"{step} Flag:", ['green', 'yellow', 'red'], index=['green', 'yellow', 'red'].index(flag), key=f'{step}_selectbox', help=f'Click count: {click_counts_ogp_after_assembly2[step]}')
            ogp_after_assembly2_flags[step] = selected_flag
            click_counts_ogp_after_assembly2[step] += 1

        for step, flag in ogp_after_assembly2_flags.items():
            ogp_after_assembly2_flags_icon = '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C'
            st.write(f"{step}: {ogp_after_assembly2_flags_icon}")

    ogp_after_assembly2_steps_completed = (all(flag == 'green' for flag in ogp_after_assembly2_flags.values()))
    Ogp_After_Assembly2_Flags = 'green' if ogp_after_assembly2_steps_completed else 'red'

    Ogp_After_Assembly2_Flags_Icon = '\u2705' if Ogp_After_Assembly2_Flags == 'green' else '\u274C'
    st.header(f"Assembly Check List: {Ogp_After_Assembly2_Flags_Icon}")

    if st.button("Save Flags to File"):
        all_checklists_flags = {
                'OGP before assembly': ogp_before_assembly_flags,
                'Assembly1':assembly1_flags,
                'OGP after assembly1':ogp_after_assembly1_flags,
                'Assembly2':assembly2_flags,
                'OGP after assembly2':ogp_after_assembly2_flags,
                'Electrical before backside bonding':electrical_before_backside_bonding_flags,
                'Backside bonding':Backside_bonding_flags,
                'OGP after backside bonding':ogp_after_backside_bonding_flags,
                'Backside encapsolation':Backside_encapsolation_flags,
                'OGP after backside encapsolation':ogp_after_backside_encapsolation_flags,
                'Pull test':Pull_test_flags,
                'Frontside bonding':Frontside_bonding_flags,
                'OGP after frontside bonding':OGP_after_frontside_bounding_flags,
                'Module encapsolation':Module_encapsolation_flags,
                'OGP after module encapsolation':OGP_after_module_encapsolation_flags,
                'Final electrical test':Final_electrical_test_flags
            }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
                   
        save_flags_to_file(all_checklists_flags, details,"output.csv",username,usergroup,comment)
        find_unfinished_modules()
###########################################################################################################################
def Electrical_before_backside_bonding(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment):
    ogp_after_assembly2_steps_completed = (all(flag == 'green' for flag in ogp_after_assembly2_flags.values()))
    Ogp_After_Assembly2_Flags = 'green' if ogp_after_assembly2_steps_completed else 'red'

    if Ogp_After_Assembly2_Flags=='red':
        st.write("Please finish the previous step first")

    if (read_user_group(username)=='Electrical' or read_user_group(username)=='All') and Ogp_After_Assembly2_Flags=='green':
        for step, flag in electrical_before_backside_bonding_flags.items():
            selected_flag = st.selectbox(f"{step} Flag:", ['green', 'yellow', 'red'], index=['green', 'yellow', 'red'].index(flag), key=f'{step}_selectbox', help=f'Click count: {click_counts_electrical_before_backside_bonding[step]}')
            electrical_before_backside_bonding_flags[step] = selected_flag
            click_counts_electrical_before_backside_bonding[step] += 1

        for step, flag in electrical_before_backside_bonding_flags.items():
            electrical_before_backside_bonding_flags_icon = '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C'
            st.write(f"{step}: {electrical_before_backside_bonding_flags_icon}")

    electrical_before_backside_bonding_steps_completed = (all(flag == 'green' for flag in ogp_after_assembly2_flags.values()))
    Electrical_Before_Backside_Bonding_Flags = 'green' if electrical_before_backside_bonding_steps_completed else 'red'

    Electrical_Before_Backside_Bonding_Flags_Icon = '\u2705' if Electrical_Before_Backside_Bonding_Flags == 'green' else '\u274C'
    st.header(f"Assembly Check List: {Electrical_Before_Backside_Bonding_Flags_Icon}")

    if st.button("Save Flags to File"):
        all_checklists_flags = {
                'OGP before assembly': ogp_before_assembly_flags,
                'Assembly1':assembly1_flags,
                'OGP after assembly1':ogp_after_assembly1_flags,
                'Assembly2':assembly2_flags,
                'OGP after assembly2':ogp_after_assembly2_flags,
                'Electrical before backside bonding':electrical_before_backside_bonding_flags,
                'Backside bonding':Backside_bonding_flags,
                'OGP after backside bonding':ogp_after_backside_bonding_flags,
                'Backside encapsolation':Backside_encapsolation_flags,
                'OGP after backside encapsolation':ogp_after_backside_encapsolation_flags,
                'Pull test':Pull_test_flags,
                'Frontside bonding':Frontside_bonding_flags,
                'OGP after frontside bonding':OGP_after_frontside_bounding_flags,
                'Module encapsolation':Module_encapsolation_flags,
                'OGP after module encapsolation':OGP_after_module_encapsolation_flags,
                'Final electrical test':Final_electrical_test_flags
            }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
                   
        save_flags_to_file(all_checklists_flags, details,"output.csv",username,usergroup,comment)
        find_unfinished_modules()
########################################################################################################
def Backside_bonding(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment):
    electrical_before_backside_bonding_steps_completed = (all(flag == 'green' for flag in ogp_after_assembly2_flags.values()))
    Electrical_Before_Backside_Bonding_Flags = 'green' if electrical_before_backside_bonding_steps_completed else 'red'

    if Electrical_Before_Backside_Bonding_Flags=='red':
        st.write("Please finish the previous step first")

    if (read_user_group(username)=='Bonding' or read_user_group(username)=='All') and Electrical_Before_Backside_Bonding_Flags=='green':
        for step, flag in Backside_bonding_flags.items():

            selected_flag = st.selectbox(f"{step} Flag:", ['green', 'yellow', 'red'], index=['green', 'yellow', 'red'].index(flag), key=f'{step}_selectbox', help=f'Click count: {click_counts_Backside_bonding[step]}')
            Backside_bonding_flags[step] = selected_flag
            click_counts_Backside_bonding[step] += 1

        for step, flag in Backside_bonding_flags.items():
            Backside_bonding_flags_icon = '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C'
            st.write(f"{step}: {Backside_bonding_flags_icon}")

    Backside_bonding_steps_completed = (all(flag == 'green' for flag in Backside_bonding_flags.values()))
    Backside_Bonding_Flags = 'green' if Backside_bonding_steps_completed else 'red'

    Backside_Bonding_Flags_Icon = '\u2705' if Backside_Bonding_Flags == 'green' else '\u274C'
    st.header(f"Backside_Bonding: {Backside_Bonding_Flags_Icon}")

    if st.button("Save Flags to File"):
        all_checklists_flags = {
                'OGP before assembly': ogp_before_assembly_flags,
                'Assembly1':assembly1_flags,
                'OGP after assembly1':ogp_after_assembly1_flags,
                'Assembly2':assembly2_flags,
                'OGP after assembly2':ogp_after_assembly2_flags,
                'Electrical before backside bonding':electrical_before_backside_bonding_flags,
                'Backside bonding':Backside_bonding_flags,
                'OGP after backside bonding':ogp_after_backside_bonding_flags,
                'Backside encapsolation':Backside_encapsolation_flags,
                'OGP after backside encapsolation':ogp_after_backside_encapsolation_flags,
                'Pull test':Pull_test_flags,
                'Frontside bonding':Frontside_bonding_flags,
                'OGP after frontside bonding':OGP_after_frontside_bounding_flags,
                'Module encapsolation':Module_encapsolation_flags,
                'OGP after module encapsolation':OGP_after_module_encapsolation_flags,
                'Final electrical test':Final_electrical_test_flags
            }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
                   
        save_flags_to_file(all_checklists_flags, details,"output.csv",username,usergroup,comment)
        find_unfinished_modules()
######################################################################################################
def Ogp_after_backside_bonding(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment):
    Backside_bonding_steps_completed = (all(flag == 'green' for flag in Backside_bonding_flags.values()))
    Backside_Bonding_Flags = 'green' if Backside_bonding_steps_completed else 'red'

    if Backside_Bonding_Flags=='red':
        st.write("Please finish the previous step first")

    if (read_user_group(username)=='OGP' or read_user_group(username)=='All') and Backside_Bonding_Flags=='green':
        for step, flag in ogp_after_backside_bonding_flags.items():
            selected_flag = st.selectbox(f"{step} Flag:", ['green', 'yellow', 'red'], index=['green', 'yellow', 'red'].index(flag), key=f'{step}_selectbox', help=f'Click count: {click_counts_ogp_after_backside_bonding[step]}')
            ogp_after_backside_bonding_flags[step] = selected_flag
            click_counts_ogp_after_backside_bonding[step] += 1

        for step, flag in ogp_after_backside_bonding_flags.items():
            ogp_after_backside_bonding_flags_icon = '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C'
            st.write(f"{step}: {ogp_after_backside_bonding_flags_icon}")

    ogp_after_backside_bonding_steps_completed = (all(flag == 'green' for flag in ogp_after_backside_bonding_flags.values()))
    Ogp_After_Backside_Bonding_Flags = 'green' if ogp_after_backside_bonding_steps_completed else 'red'

    Ogp_After_Backside_Bonding_Flags_Icon = '\u2705' if Ogp_After_Backside_Bonding_Flags == 'green' else '\u274C'
    st.header(f"Ogp After Backside Bonding: {Ogp_After_Backside_Bonding_Flags_Icon}")

    if st.button("Save Flags to File"):
        all_checklists_flags = {
                'OGP before assembly': ogp_before_assembly_flags,
                'Assembly1':assembly1_flags,
                'OGP after assembly1':ogp_after_assembly1_flags,
                'Assembly2':assembly2_flags,
                'OGP after assembly2':ogp_after_assembly2_flags,
                'Electrical before backside bonding':electrical_before_backside_bonding_flags,
                'Backside bonding':Backside_bonding_flags,
                'OGP after backside bonding':ogp_after_backside_bonding_flags,
                'Backside encapsolation':Backside_encapsolation_flags,
                'OGP after backside encapsolation':ogp_after_backside_encapsolation_flags,
                'Pull test':Pull_test_flags,
                'Frontside bonding':Frontside_bonding_flags,
                'OGP after frontside bonding':OGP_after_frontside_bounding_flags,
                'Module encapsolation':Module_encapsolation_flags,
                'OGP after module encapsolation':OGP_after_module_encapsolation_flags,
                'Final electrical test':Final_electrical_test_flags
            }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
                   
        save_flags_to_file(all_checklists_flags, details,"output.csv",username,usergroup,comment)
        find_unfinished_modules()
###########################################################################################################################
def Backside_encapsolation(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment):
    ogp_after_backside_bonding_steps_completed = (all(flag == 'green' for flag in ogp_after_backside_bonding_flags.values()))
    Ogp_After_Backside_Bonding_Flags = 'green' if ogp_after_backside_bonding_steps_completed else 'red'

    if Ogp_After_Backside_Bonding_Flags=='red':
        st.write("Please finish the previous step first")

    if (read_user_group(username)=='Encapsolation' or read_user_group(username)=='All') and Ogp_After_Backside_Bonding_Flags=='green':
        for step, flag in Backside_encapsolation_flags.items():

            selected_flag = st.selectbox(f"{step} Flag:", ['green', 'yellow', 'red'], index=['green', 'yellow', 'red'].index(flag), key=f'{step}_selectbox', help=f'Click count: {click_counts_Backside_encapsolation[step]}')
            Backside_encapsolation_flags[step] = selected_flag
            click_counts_Backside_encapsolation[step] += 1

        for step, flag in Backside_encapsolation_flags.items():
            Backside_encapsolation_flags_icon = '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C'
            st.write(f"{step}: {Backside_encapsolation_flags_icon}")

    Backside_encapsolation_steps_completed = (all(flag == 'green' for flag in Backside_encapsolation_flags.values()))
    Backside_Encapsolation_Flags = 'green' if Backside_encapsolation_steps_completed else 'red'

    Backside_Encapsolation_Flags_Icon = '\u2705' if Backside_Encapsolation_Flags == 'green' else '\u274C'
    st.header(f"Backside Encapsolation: {Backside_Encapsolation_Flags_Icon}")

    if st.button("Save Flags to File"):
        all_checklists_flags = {
                'OGP before assembly': ogp_before_assembly_flags,
                'Assembly1':assembly1_flags,
                'OGP after assembly1':ogp_after_assembly1_flags,
                'Assembly2':assembly2_flags,
                'OGP after assembly2':ogp_after_assembly2_flags,
                'Electrical before backside bonding':electrical_before_backside_bonding_flags,
                'Backside bonding':Backside_bonding_flags,
                'OGP after backside bonding':ogp_after_backside_bonding_flags,
                'Backside encapsolation':Backside_encapsolation_flags,
                'OGP after backside encapsolation':ogp_after_backside_encapsolation_flags,
                'Pull test':Pull_test_flags,
                'Frontside bonding':Frontside_bonding_flags,
                'OGP after frontside bonding':OGP_after_frontside_bounding_flags,
                'Module encapsolation':Module_encapsolation_flags,
                'OGP after module encapsolation':OGP_after_module_encapsolation_flags,
                'Final electrical test':Final_electrical_test_flags
            }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
                   
        save_flags_to_file(all_checklists_flags, details,"output.csv",username,usergroup,comment)
        find_unfinished_modules()
###########################################################################################################################
def Ogp_after_backside_encapsolation(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment):
    Backside_encapsolation_steps_completed = (all(flag == 'green' for flag in Backside_encapsolation_flags.values()))
    Backside_Encapsolation_Flags = 'green' if Backside_encapsolation_steps_completed else 'red'

    if Backside_Encapsolation_Flags=='red':
        st.write("Please finish the previous step first")

    if (read_user_group(username)=='OGP' or read_user_group(username)=='All') and Backside_Encapsolation_Flags=='green':
        for step, flag in ogp_after_backside_encapsolation_flags.items():

            selected_flag = st.selectbox(f"{step} Flag:", ['green', 'yellow', 'red'], index=['green', 'yellow', 'red'].index(flag), key=f'{step}_selectbox', help=f'Click count: {click_counts_ogp_after_backside_encapsolation[step]}')
            ogp_after_backside_encapsolation_flags[step] = selected_flag
            click_counts_ogp_after_backside_encapsolation[step] += 1

        for step, flag in ogp_after_backside_encapsolation_flags.items():
            ogp_after_backside_encapsolation_flags_icon = '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C'
            st.write(f"{step}: {ogp_after_backside_encapsolation_flags_icon}")

    ogp_after_backside_encapsolation_steps_completed = (all(flag == 'green' for flag in ogp_after_backside_encapsolation_flags.values()))
    Ogp_After_Backside_Encapsolation_Flags = 'green' if ogp_after_backside_encapsolation_steps_completed else 'red'

    Ogp_After_Backside_Encapsolation_Flags_Icon = '\u2705' if Ogp_After_Backside_Encapsolation_Flags == 'green' else '\u274C'
    st.header(f"Ogp after backside encapsolation: {Ogp_After_Backside_Encapsolation_Flags_Icon}")

    if st.button("Save Flags to File"):
        all_checklists_flags = {
                'OGP before assembly': ogp_before_assembly_flags,
                'Assembly1':assembly1_flags,
                'OGP after assembly1':ogp_after_assembly1_flags,
                'Assembly2':assembly2_flags,
                'OGP after assembly2':ogp_after_assembly2_flags,
                'Electrical before backside bonding':electrical_before_backside_bonding_flags,
                'Backside bonding':Backside_bonding_flags,
                'OGP after backside bonding':ogp_after_backside_bonding_flags,
                'Backside encapsolation':Backside_encapsolation_flags,
                'OGP after backside encapsolation':ogp_after_backside_encapsolation_flags,
                'Pull test':Pull_test_flags,
                'Frontside bonding':Frontside_bonding_flags,
                'OGP after frontside bonding':OGP_after_frontside_bounding_flags,
                'Module encapsolation':Module_encapsolation_flags,
                'OGP after module encapsolation':OGP_after_module_encapsolation_flags,
                'Final electrical test':Final_electrical_test_flags
            }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
                   
        save_flags_to_file(all_checklists_flags, details,"output.csv",username,usergroup,comment)
        find_unfinished_modules()
###########################################################################################################################
def Pull_test(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment):
    ogp_after_backside_encapsolation_steps_completed = (all(flag == 'green' for flag in ogp_after_backside_encapsolation_flags.values()))
    Ogp_After_Backside_Encapsolation_Flags = 'green' if ogp_after_backside_encapsolation_steps_completed else 'red'

    if Ogp_After_Backside_Encapsolation_Flags=='red':
        st.write("Please finish the previous step first")

    if (read_user_group(username)=='Bonding' or read_user_group(username)=='All') and Ogp_After_Backside_Encapsolation_Flags=='green':
        for step, flag in Pull_test_flags.items():

            selected_flag = st.selectbox(f"{step} Flag:", ['green', 'yellow', 'red'], index=['green', 'yellow', 'red'].index(flag), key=f'{step}_selectbox', help=f'Click count: {click_counts_Pull_test[step]}')
            Pull_test_flags[step] = selected_flag
            click_counts_Pull_test[step] += 1

        for step, flag in Pull_test_flags.items():
            Pull_test_flags_icon = '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C'
            st.write(f"{step}: {Pull_test_flags_icon}")

    Pull_test_steps_completed = (all(flag == 'green' for flag in Pull_test_flags.values()))
    Pull_Test_Flags = 'green' if Pull_test_steps_completed else 'red'

    Pull_Test_Flags_Icon = '\u2705' if Pull_Test_Flags == 'green' else '\u274C'
    st.header(f"Pull Test: {Pull_Test_Flags_Icon}")

    if st.button("Save Flags to File"):
        all_checklists_flags = {
                'OGP before assembly': ogp_before_assembly_flags,
                'Assembly1':assembly1_flags,
                'OGP after assembly1':ogp_after_assembly1_flags,
                'Assembly2':assembly2_flags,
                'OGP after assembly2':ogp_after_assembly2_flags,
                'Electrical before backside bonding':electrical_before_backside_bonding_flags,
                'Backside bonding':Backside_bonding_flags,
                'OGP after backside bonding':ogp_after_backside_bonding_flags,
                'Backside encapsolation':Backside_encapsolation_flags,
                'OGP after backside encapsolation':ogp_after_backside_encapsolation_flags,
                'Pull test':Pull_test_flags,
                'Frontside bonding':Frontside_bonding_flags,
                'OGP after frontside bonding':OGP_after_frontside_bounding_flags,
                'Module encapsolation':Module_encapsolation_flags,
                'OGP after module encapsolation':OGP_after_module_encapsolation_flags,
                'Final electrical test':Final_electrical_test_flags
            }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
                   
        save_flags_to_file(all_checklists_flags, details,"output.csv",username,usergroup,comment)
        find_unfinished_modules()
###########################################################################################################################
def Frontside_bonding(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment):
    Pull_test_steps_completed = (all(flag == 'green' for flag in Pull_test_flags.values()))
    Pull_Test_Flags = 'green' if Pull_test_steps_completed else 'red'

    if Pull_Test_Flags=='red':
        st.write("Please finish the previous step first")

    if (read_user_group(username)=='Bonding' or read_user_group(username)=='All') and Pull_Test_Flags=='green':
        for step, flag in Frontside_bonding_flags.items():
           
            selected_flag = st.selectbox(f"{step} Flag:", ['green', 'yellow', 'red'], index=['green', 'yellow', 'red'].index(flag), key=f'{step}_selectbox', help=f'Click count: {click_counts_Frontside_bonding[step]}')
            Frontside_bonding_flags[step] = selected_flag
            click_counts_Frontside_bonding[step] += 1
           
        for step, flag in Frontside_bonding_flags.items():
            Frontside_bonding_flags_icon = '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C'
            st.write(f"{step}: {Frontside_bonding_flags_icon}")

    Frontside_bonding_steps_completed = (all(flag == 'green' for flag in Frontside_bonding_flags.values()))
    Frontside_Bonding_Flags = 'green' if Frontside_bonding_steps_completed else 'red'

    Frontside_Bonding_Flags_Icon = '\u2705' if Frontside_Bonding_Flags == 'green' else '\u274C'
    st.header(f"Frontside Bonding: {Frontside_Bonding_Flags_Icon}")

    if st.button("Save Flags to File"):
        all_checklists_flags = {
                'OGP before assembly': ogp_before_assembly_flags,
                'Assembly1':assembly1_flags,
                'OGP after assembly1':ogp_after_assembly1_flags,
                'Assembly2':assembly2_flags,
                'OGP after assembly2':ogp_after_assembly2_flags,
                'Electrical before backside bonding':electrical_before_backside_bonding_flags,
                'Backside bonding':Backside_bonding_flags,
                'OGP after backside bonding':ogp_after_backside_bonding_flags,
                'Backside encapsolation':Backside_encapsolation_flags,
                'OGP after backside encapsolation':ogp_after_backside_encapsolation_flags,
                'Pull test':Pull_test_flags,
                'Frontside bonding':Frontside_bonding_flags,
                'OGP after frontside bonding':OGP_after_frontside_bounding_flags,
                'Module encapsolation':Module_encapsolation_flags,
                'OGP after module encapsolation':OGP_after_module_encapsolation_flags,
                'Final electrical test':Final_electrical_test_flags
            }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
                   
        save_flags_to_file(all_checklists_flags, details,"output.csv",username,usergroup,comment)
        find_unfinished_modules()
###########################################################################################################################
def OGP_after_frontside_bounding(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment):
    Frontside_bonding_steps_completed = (all(flag == 'green' for flag in Frontside_bonding_flags.values()))
    Frontside_Bonding_Flags = 'green' if Frontside_bonding_steps_completed else 'red'

    if Frontside_Bonding_Flags=='red':
        st.write("Please finish the previous step first")

    if (read_user_group(username)=='OGP' or read_user_group(username)=='All') and Frontside_Bonding_Flags=='green':
        for step, flag in OGP_after_frontside_bounding_flags.items():

            selected_flag = st.selectbox(f"{step} Flag:", ['green', 'yellow', 'red'], index=['green', 'yellow', 'red'].index(flag), key=f'{step}_selectbox', help=f'Click count: {click_counts_OGP_after_frontside_bounding[step]}')
            OGP_after_frontside_bounding_flags[step] = selected_flag
            click_counts_OGP_after_frontside_bounding[step] += 1

        for step, flag in OGP_after_frontside_bounding_flags.items():
            OGP_after_frontside_bounding_flags_icon = '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C'
            st.write(f"{step}: {OGP_after_frontside_bounding_flags_icon}")

    OGP_after_frontside_bounding_steps_completed = (all(flag == 'green' for flag in OGP_after_frontside_bounding_flags.values()))
    OGP_After_Frontside_Bounding_Flags = 'green' if OGP_after_frontside_bounding_steps_completed else 'red'

    OGP_After_Frontside_Bounding_Flags_Icon = '\u2705' if OGP_After_Frontside_Bounding_Flags == 'green' else '\u274C'
    st.header(f"OGP After Frontside Bounding: {OGP_After_Frontside_Bounding_Flags_Icon}")

    if st.button("Save Flags to File"):
        all_checklists_flags = {
                'OGP before assembly': ogp_before_assembly_flags,
                'Assembly1':assembly1_flags,
                'OGP after assembly1':ogp_after_assembly1_flags,
                'Assembly2':assembly2_flags,
                'OGP after assembly2':ogp_after_assembly2_flags,
                'Electrical before backside bonding':electrical_before_backside_bonding_flags,
                'Backside bonding':Backside_bonding_flags,
                'OGP after backside bonding':ogp_after_backside_bonding_flags,
                'Backside encapsolation':Backside_encapsolation_flags,
                'OGP after backside encapsolation':ogp_after_backside_encapsolation_flags,
                'Pull test':Pull_test_flags,
                'Frontside bonding':Frontside_bonding_flags,
                'OGP after frontside bonding':OGP_after_frontside_bounding_flags,
                'Module encapsolation':Module_encapsolation_flags,
                'OGP after module encapsolation':OGP_after_module_encapsolation_flags,
                'Final electrical test':Final_electrical_test_flags
            }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
                   
        save_flags_to_file(all_checklists_flags, details,"output.csv",username,usergroup,comment)
        find_unfinished_modules()
############################################################################################################################
def Module_encapsolation(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment):
    OGP_after_frontside_bounding_steps_completed = (all(flag == 'green' for flag in OGP_after_frontside_bounding_flags.values()))
    OGP_After_Frontside_Bounding_Flags = 'green' if OGP_after_frontside_bounding_steps_completed else 'red'

    if OGP_After_Frontside_Bounding_Flags=='red':
        st.write("Please finish the previous step first")

    if (read_user_group(username)=='Encapsolation' or read_user_group(username)=='All') and OGP_After_Frontside_Bounding_Flags=='green':
        for step, flag in Module_encapsolation_flags.items():

            selected_flag = st.selectbox(f"{step} Flag:", ['green', 'yellow', 'red'], index=['green', 'yellow', 'red'].index(flag), key=f'{step}_selectbox', help=f'Click count: {click_counts_Module_encapsolation[step]}')
            Module_encapsolation_flags[step] = selected_flag
            click_counts_Module_encapsolation[step] += 1

        for step, flag in Module_encapsolation_flags.items():
            Module_encapsolation_flags_icon = '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C'
            st.write(f"{step}: {Module_encapsolation_flags_icon}")

    Module_encapsolation_steps_completed = (all(flag == 'green' for flag in Module_encapsolation_flags.values()))
    Module_Encapsolation_Flags = 'green' if Module_encapsolation_steps_completed else 'red'

    Module_Encapsolation_Flags_Icon = '\u2705' if Module_Encapsolation_Flags == 'green' else '\u274C'
    st.header(f"Module Encapsolation: {Module_Encapsolation_Flags_Icon}")

    if st.button("Save Flags to File"):
        all_checklists_flags = {
                'OGP before assembly': ogp_before_assembly_flags,
                'Assembly1':assembly1_flags,
                'OGP after assembly1':ogp_after_assembly1_flags,
                'Assembly2':assembly2_flags,
                'OGP after assembly2':ogp_after_assembly2_flags,
                'Electrical before backside bonding':electrical_before_backside_bonding_flags,
                'Backside bonding':Backside_bonding_flags,
                'OGP after backside bonding':ogp_after_backside_bonding_flags,
                'Backside encapsolation':Backside_encapsolation_flags,
                'OGP after backside encapsolation':ogp_after_backside_encapsolation_flags,
                'Pull test':Pull_test_flags,
                'Frontside bonding':Frontside_bonding_flags,
                'OGP after frontside bonding':OGP_after_frontside_bounding_flags,
                'Module encapsolation':Module_encapsolation_flags,
                'OGP after module encapsolation':OGP_after_module_encapsolation_flags,
                'Final electrical test':Final_electrical_test_flags
            }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
                   
        save_flags_to_file(all_checklists_flags, details,"output.csv",username,usergroup,comment)
        find_unfinished_modules()
############################################################################################################################
def OGP_after_module_encapsolation(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment):
    Module_encapsolation_steps_completed = (all(flag == 'green' for flag in Module_encapsolation_flags.values()))
    Module_Encapsolation_Flags = 'green' if Module_encapsolation_steps_completed else 'red'

    if Module_Encapsolation_Flags=='red':
        st.write("Please finish the previous step first")

    if (read_user_group(username)=='OGP' or read_user_group(username)=='All') and Module_Encapsolation_Flags=='green':
        for step, flag in OGP_after_module_encapsolation_flags.items():

            selected_flag = st.selectbox(f"{step} Flag:", ['green', 'yellow', 'red'], index=['green', 'yellow', 'red'].index(flag), key=f'{step}_selectbox', help=f'Click count: {click_counts_OGP_after_module_encapsolation[step]}')
            OGP_after_module_encapsolation_flags[step] = selected_flag
            click_counts_OGP_after_module_encapsolation[step] += 1

        for step, flag in OGP_after_module_encapsolation_flags.items():
            OGP_after_module_encapsolation_flags_icon = '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C'
            st.write(f"{step}: {OGP_after_module_encapsolation_flags_icon}")

    OGP_after_module_encapsolation_steps_completed = (all(flag == 'green' for flag in OGP_after_module_encapsolation_flags.values()))
    OGP_After_Module_Encapsolation_Flags = 'green' if OGP_after_module_encapsolation_steps_completed else 'red'

    OGP_After_Module_Encapsolation_Flags_Icon = '\u2705' if OGP_After_Module_Encapsolation_Flags == 'green' else '\u274C'
    st.header(f"OGP After Module Encapsolation: {OGP_After_Module_Encapsolation_Flags_Icon}")

    if st.button("Save Flags to File"):
        all_checklists_flags = {
                'OGP before assembly': ogp_before_assembly_flags,
                'Assembly1':assembly1_flags,
                'OGP after assembly1':ogp_after_assembly1_flags,
                'Assembly2':assembly2_flags,
                'OGP after assembly2':ogp_after_assembly2_flags,
                'Electrical before backside bonding':electrical_before_backside_bonding_flags,
                'Backside bonding':Backside_bonding_flags,
                'OGP after backside bonding':ogp_after_backside_bonding_flags,
                'Backside encapsolation':Backside_encapsolation_flags,
                'OGP after backside encapsolation':ogp_after_backside_encapsolation_flags,
                'Pull test':Pull_test_flags,
                'Frontside bonding':Frontside_bonding_flags,
                'OGP after frontside bonding':OGP_after_frontside_bounding_flags,
                'Module encapsolation':Module_encapsolation_flags,
                'OGP after module encapsolation':OGP_after_module_encapsolation_flags,
                'Final electrical test':Final_electrical_test_flags
            }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
                   
        save_flags_to_file(all_checklists_flags, details,"output.csv",username,usergroup,comment)
        find_unfinished_modules()
############################################################################################################################
def Final_electrical_test(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment):
    OGP_after_module_encapsolation_steps_completed = (all(flag == 'green' for flag in OGP_after_module_encapsolation_flags.values()))
    OGP_After_Module_Encapsolation_Flags = 'green' if OGP_after_module_encapsolation_steps_completed else 'red'

    if OGP_After_Module_Encapsolation_Flags=='red':
        st.write("Please finish the previous step first")

    if (read_user_group(username)=='Electrical' or read_user_group(username)=='All') and OGP_After_Module_Encapsolation_Flags=='green':
        for step, flag in Final_electrical_test_flags.items():

            selected_flag = st.selectbox(f"{step} Flag:", ['green', 'yellow', 'red'], index=['green', 'yellow', 'red'].index(flag), key=f'{step}_selectbox', help=f'Click count: {click_counts_Final_electrical_test[step]}')
            Final_electrical_test_flags[step] = selected_flag
            click_counts_Final_electrical_test[step] += 1

        for step, flag in Final_electrical_test_flags.items():
            Final_electrical_test_flags_icon = '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C'
            st.write(f"{step}: {Final_electrical_test_flags_icon}")

    Final_electrical_test_steps_completed = (all(flag == 'green' for flag in Final_electrical_test_flags.values()))
    Final_Electrical_Test_Flags = 'green' if Final_electrical_test_steps_completed else 'red'

    Final_Electrical_Test_Flags_Icon = '\u2705' if Final_Electrical_Test_Flags == 'green' else '\u274C'
    st.header(f"Final Electrical Test: {Final_Electrical_Test_Flags_Icon}")

    if st.button("Save Flags to File"):
        all_checklists_flags = {
                'OGP before assembly': ogp_before_assembly_flags,
                'Assembly1':assembly1_flags,
                'OGP after assembly1':ogp_after_assembly1_flags,
                'Assembly2':assembly2_flags,
                'OGP after assembly2':ogp_after_assembly2_flags,
                'Electrical before backside bonding':electrical_before_backside_bonding_flags,
                'Backside bonding':Backside_bonding_flags,
                'OGP after backside bonding':ogp_after_backside_bonding_flags,
                'Backside encapsolation':Backside_encapsolation_flags,
                'OGP after backside encapsolation':ogp_after_backside_encapsolation_flags,
                'Pull test':Pull_test_flags,
                'Frontside bonding':Frontside_bonding_flags,
                'OGP after frontside bonding':OGP_after_frontside_bounding_flags,
                'Module encapsolation':Module_encapsolation_flags,
                'OGP after module encapsolation':OGP_after_module_encapsolation_flags,
                'Final electrical test':Final_electrical_test_flags
            }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
                   
        save_flags_to_file(all_checklists_flags, details,"output.csv",username,usergroup,comment)
        find_unfinished_modules()
############################################################################################################################
def find_unfinished_modules():
    # Read the output.csv file
    df = pd.read_csv("output.csv")

    # Group by the specified criteria and check for unfinished modules
    grouped = df.groupby(['Module Number', 'Sensor ID', 'Hexboard Number', 'Baseplate Number', 'Remeasurement Number'])
    unfinished_modules = []

    for group_name, group_data in grouped:
        # Check if any step in the module has a flag 'red'
        if 'red' in group_data['Flag'].values:
            unfinished_modules.append(group_data)

    # Concatenate the unfinished modules into a single DataFrame
    unfinished_df = pd.concat(unfinished_modules)

    # Save the unfinished modules to a new CSV file
    unfinished_df.to_csv("unfinished_module.csv", index=False)
############################################################################################################################
def show_unfinished_modules(username):
    # Read the unfinished_module.csv file
    unfinished_df = pd.read_csv("unfinished_module.csv")

    # Filter the unfinished modules with red flags
    unfinished_red_flags = unfinished_df[unfinished_df['Flag'] == 'red']

    # Group by the criteria and get the first step with red flag for each unfinished module
    grouped_unfinished = unfinished_red_flags.groupby(['Module Number', 'Sensor ID', 'Hexboard Number', 'Baseplate Number', 'Remeasurement Number'])
    module_info = []
    usergroup=read_user_group(username)
    for group_name, group_data in grouped_unfinished:
        # Find the first step with a red flag for each module
        red_flag_data = group_data[group_data['Flag'] == 'red']
        first_red_flag_step = red_flag_data.iloc[0]['Step'] if not red_flag_data.empty else None
        comment = group_data.iloc[0]['Comment'] if not group_data.empty else None
        # Extract relevant information for display
        module_info.append({
            'Module Number': group_name[0],
            'Sensor ID': group_name[1],
            'Hexboard Number': group_name[2],
            'Baseplate Number': group_name[3],
            'Remeasurement Number': group_name[4],
            'First Red Flag Step': first_red_flag_step,
            'Comment':comment
        })

    if module_info:
        unfinished_table = pd.DataFrame(module_info)
        st.write(unfinished_table)
    else:
        st.write("No unfinished modules with red flags found.")
    
    if st.checkbox("Show Unfinished Modules"):
        for index, module in unfinished_table.iterrows():
            checkbox_label = f"Module Number: {module['Module Number']} - Sensor ID: {module['Sensor ID']} - Hexboard Number:{module['Hexboard Number']} - Baseplate Number:{module['Baseplate Number']} - Remeasurement Number:{module['Remeasurement Number']}"
            if st.checkbox(checkbox_label):
                st.session_state.module_number = module['Module Number']
                st.session_state.sensor_id = module['Sensor ID']
                st.session_state.hexboard_number = module['Hexboard Number']
                st.session_state.baseplate_number = module['Baseplate Number']
                st.session_state.remeasurement_number = module['Remeasurement Number']
                st.session_state.comment = module['Comment']

        if 'module_number' in st.session_state:
            st.text_input("Enter Module Number", value=st.session_state.module_number)
            st.text_input("Enter Sensor ID", value=st.session_state.sensor_id)
            st.text_input("Enter Hexboard Number", value=st.session_state.hexboard_number)
            st.text_input("Enter Baseplate Number", value=st.session_state.baseplate_number)
            st.text_input("Enter Remeasurement Number(0 for the first measurement)", value=str(st.session_state.remeasurement_number))
            st.text_input("Enter Comment(can be empty)", value=str(st.session_state.comment))

        if st.checkbox("Submit"):
            module_number = str(st.session_state.get('module_number'))
            sensor_id = str(st.session_state.get('sensor_id'))
            hexboard_number = str(st.session_state.get('hexboard_number'))
            baseplate_number = str(st.session_state.get('baseplate_number'))
            remeasurement_number = str(st.session_state.get('remeasurement_number'))
            comment = str(st.session_state.get('comment'))
            usergroup = read_user_group(username)

            if all([module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number]):
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                option1=st.selectbox("Select an option", ("Overview","OGP before assembly","Assembly1","OGP after assembly1","Assembly2","OGP after assembly2","Electrical before backside bonding","Backside bonding","OGP after backside bonding","Backside encapsolation","OGP after backside encapsolation","Pull test","Frontside bonding","OGP after frontside bonding","Module encapsolation","OGP after module encapsolation","Final electrical test"),key="option1")
            if option1=='Overview':
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                ogp_before_assembly_completed = all(flag == 'green' for flag in ogp_before_assembly_flags.values())
                Ogp_Before_Assembly_Flag = 'green' if ogp_before_assembly_completed else 'red'
                Ogp_Before_Assembly_Icon = '\u2705' if Ogp_Before_Assembly_Flag == 'green' else '\u274C'
                st.header(f"OGP Before Assembly: {Ogp_Before_Assembly_Icon}")


                assembly1_steps_completed = all(flag == 'green' for flag in assembly1_flags.values())
                Assembly1_Checklist_Flag = 'green' if assembly1_steps_completed else 'red'
                Assembly1_Flag_Icon = '\u2705' if Assembly1_Checklist_Flag == 'green' else '\u274C'
                st.header(f"Assembly1: {Assembly1_Flag_Icon}")

                ogp_after_assembly1_steps_completed = (all(flag == 'green' for flag in ogp_after_assembly1_flags.values()))
                Ogp_After_Assembly1_Checklist_Flag = 'green' if ogp_after_assembly1_steps_completed else 'red'
                Ogp_After_Assembly1_Checklist_Flag_Icon = '\u2705' if Ogp_After_Assembly1_Checklist_Flag == 'green' else '\u274C'
                st.header(f"Ogp After Assembly1: {Ogp_After_Assembly1_Checklist_Flag_Icon}")

                assembly2_steps_completed = (all(flag == 'green' for flag in assembly2_flags.values()))
                Assembly2_Checklist_Flag = 'green' if assembly2_steps_completed else 'red'
                Assembly2_Checklist_Flag_Icon = '\u2705' if Assembly2_Checklist_Flag == 'green' else '\u274C'
                st.header(f"Assembly2: {Assembly2_Checklist_Flag_Icon}")

                ogp_after_assembly2_steps_completed = (all(flag == 'green' for flag in ogp_after_assembly2_flags.values()))
                Ogp_After_Assembly2_Flags = 'green' if ogp_after_assembly2_steps_completed else 'red'
                Ogp_After_Assembly2_Flags_Icon = '\u2705' if Ogp_After_Assembly2_Flags == 'green' else '\u274C'
                st.header(f"Ogp After Assembly2: {Ogp_After_Assembly2_Flags_Icon}")

                electrical_before_backside_bonding_steps_completed = (all(flag == 'green' for flag in ogp_after_assembly2_flags.values()))
                Electrical_Before_Backside_Bonding_Flags = 'green' if electrical_before_backside_bonding_steps_completed else 'red'
                Electrical_Before_Backside_Bonding_Flags_Icon = '\u2705' if Electrical_Before_Backside_Bonding_Flags == 'green' else '\u274C'
                st.header(f"Electrical test Before Backside Bonding: {Electrical_Before_Backside_Bonding_Flags_Icon}")

                Backside_bonding_steps_completed = (all(flag == 'green' for flag in Backside_bonding_flags.values()))
                Backside_Bonding_Flags = 'green' if Backside_bonding_steps_completed else 'red'
                Backside_Bonding_Flags_Icon = '\u2705' if Backside_Bonding_Flags == 'green' else '\u274C'
                st.header(f"Backside_Bonding: {Backside_Bonding_Flags_Icon}")

                ogp_after_backside_bonding_steps_completed = (all(flag == 'green' for flag in ogp_after_backside_bonding_flags.values()))
                Ogp_After_Backside_Bonding_Flags = 'green' if ogp_after_backside_bonding_steps_completed else 'red'
                Ogp_After_Backside_Bonding_Flags_Icon = '\u2705' if Ogp_After_Backside_Bonding_Flags == 'green' else '\u274C'
                st.header(f"Ogp After Backside Bonding: {Ogp_After_Backside_Bonding_Flags_Icon}")

                Backside_encapsolation_steps_completed = (all(flag == 'green' for flag in Backside_encapsolation_flags.values()))
                Backside_Encapsolation_Flags = 'green' if Backside_encapsolation_steps_completed else 'red'
                Backside_Encapsolation_Flags_Icon = '\u2705' if Backside_Encapsolation_Flags == 'green' else '\u274C'
                st.header(f"Backside Encapsolation: {Backside_Encapsolation_Flags_Icon}")

                ogp_after_backside_encapsolation_steps_completed = (all(flag == 'green' for flag in ogp_after_backside_encapsolation_flags.values()))
                Ogp_After_Backside_Encapsolation_Flags = 'green' if ogp_after_backside_encapsolation_steps_completed else 'red'
                Ogp_After_Backside_Encapsolation_Flags_Icon = '\u2705' if Ogp_After_Backside_Encapsolation_Flags == 'green' else '\u274C'
                st.header(f"Ogp after backside encapsolation: {Ogp_After_Backside_Encapsolation_Flags_Icon}")

                Pull_test_steps_completed = (all(flag == 'green' for flag in Pull_test_flags.values()))
                Pull_Test_Flags = 'green' if Pull_test_steps_completed else 'red'
                Pull_Test_Flags_Icon = '\u2705' if Pull_Test_Flags == 'green' else '\u274C'
                st.header(f"Pull Test: {Pull_Test_Flags_Icon}")

                Frontside_bonding_steps_completed = (all(flag == 'green' for flag in Frontside_bonding_flags.values()))
                Frontside_Bonding_Flags = 'green' if Frontside_bonding_steps_completed else 'red'
                Frontside_Bonding_Flags_Icon = '\u2705' if Frontside_Bonding_Flags == 'green' else '\u274C'
                st.header(f"Frontside Bonding: {Frontside_Bonding_Flags_Icon}")

                OGP_after_frontside_bounding_steps_completed = (all(flag == 'green' for flag in OGP_after_frontside_bounding_flags.values()))
                OGP_After_Frontside_Bounding_Flags = 'green' if OGP_after_frontside_bounding_steps_completed else 'red'
                OGP_After_Frontside_Bounding_Flags_Icon = '\u2705' if OGP_After_Frontside_Bounding_Flags == 'green' else '\u274C'
                st.header(f"OGP After Frontside Bounding: {OGP_After_Frontside_Bounding_Flags_Icon}")

                Module_encapsolation_steps_completed = (all(flag == 'green' for flag in Module_encapsolation_flags.values()))
                Module_Encapsolation_Flags = 'green' if Module_encapsolation_steps_completed else 'red'
                Module_Encapsolation_Flags_Icon = '\u2705' if Module_Encapsolation_Flags == 'green' else '\u274C'
                st.header(f"Module Encapsolation: {Module_Encapsolation_Flags_Icon}")

                OGP_after_module_encapsolation_steps_completed = (all(flag == 'green' for flag in OGP_after_module_encapsolation_flags.values()))
                OGP_After_Module_Encapsolation_Flags = 'green' if OGP_after_module_encapsolation_steps_completed else 'red'
                OGP_After_Module_Encapsolation_Flags_Icon = '\u2705' if OGP_After_Module_Encapsolation_Flags == 'green' else '\u274C'
                st.header(f"OGP After Module Encapsolation: {OGP_After_Module_Encapsolation_Flags_Icon}")

                Final_electrical_test_steps_completed = (all(flag == 'green' for flag in Final_electrical_test_flags.values()))
                Final_Electrical_Test_Flags = 'green' if Final_electrical_test_steps_completed else 'red'
                Final_Electrical_Test_Flags_Icon = '\u2705' if Final_Electrical_Test_Flags == 'green' else '\u274C'
                st.header(f"Final Electrical Test: {Final_Electrical_Test_Flags_Icon}")


            if option1=="OGP before assembly":
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                OGP_before_assembly(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment)
            if option1=="Assembly1":
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Assembly1(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment)
            if option1=='OGP after assembly1':
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                OGP_after_assembly1(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment)
            if option1=='Assembly2':
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Assembly2(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment)
            if option1=='OGP after assembly2':
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                OGP_after_assembly2(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment)
            if option1=='Electrical before backside bonding':
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Electrical_before_backside_bonding(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment)
            if option1=='Backside bonding':
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Backside_bonding(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment)
            if option1=='OGP after backside bonding':
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Ogp_after_backside_bonding(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment)
            if option1=='Backside encapsolation':
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Backside_encapsolation(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment)
            if option1=='OGP after backside encapsolation':
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Ogp_after_backside_encapsolation(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment)
            if option1=='Pull test':
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Pull_test(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment)
            if option1=='Frontside bonding':
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Frontside_bonding(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment)
            if option1=='OGP after frontside bonding':
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                OGP_after_frontside_bounding(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment)
            if option1=='Module encapsolation':
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Module_encapsolation(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment)
            if option1=='OGP after module encapsolation':
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                OGP_after_module_encapsolation(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment)
            if option1=='Final electrical test':
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Final_electrical_test(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment)
###################################################################################################################################################################
def plot_selected_module():
    module_number = st.text_input("Enter Module Number")
    sensor_id = st.text_input("Enter Sensor ID")
    hexboard_number = st.text_input("Enter Hexboard Number")
    baseplate_number = st.text_input("Enter Baseplate Number")
    remeasurement_number=st.text_input("Enter Remeasurement Number(0 for the first measurement)")
    if st.checkbox("Submit"):
        if module_number and sensor_id and hexboard_number and baseplate_number and remeasurement_number:
    # Read the output.csv file
            df = pd.read_csv("output.csv", dtype={'Module Number': str, 'Sensor ID': str, 'Hexboard Number': str, 'Baseplate Number': str, 'Remeasurement Number':str})

    # Filter data for the selected module
            module_filter = (
                (df['Module Number'] == module_number) &
                (df['Sensor ID'] == sensor_id) &
                (df['Hexboard Number'] == hexboard_number) &
                (df['Baseplate Number'] == baseplate_number) &
            (df['Remeasurement Number'] == remeasurement_number)
            )

            filtered_df = df[module_filter]
            steps = filtered_df['Step']
            flags = filtered_df['Flag'].apply(lambda x: 1 if x == 'green' else 0)

            plt.figure(figsize=(12, 8))
            plt.bar(steps, flags, color='lightblue')
            plt.title(f"Module: {module_number} - {sensor_id} - {hexboard_number} - {baseplate_number} - {remeasurement_number}")
            plt.xlabel('Steps')
            plt.ylabel('Flag (0 - Red, 1 - Green)')
            plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better visibility

    # Convert plot to HTML image tag
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_tag = f'<img src="data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}" />'
            plt.close()

            return image_tag
###################################################################################################################################################################
def plot_modules():
    # Read the output.csv file
    df = pd.read_csv("output.csv")

    # Filter for only the rows where the flag is 'green'
    finished_modules = df[df['Flag'] == 'green'].groupby(['Step', 'Module Number', 'Sensor ID', 'Hexboard Number', 'Baseplate Number', 'Remeasurement Number']).size().reset_index(name='count')
    finished_modules = finished_modules.groupby('Step')['count'].count()

    # Get the unique steps in the order they appear in the file
    unique_steps_order = df['Step'].unique()

    # Convert 'Step' to a categorical data type with the desired order
    finished_modules.index = pd.Categorical(finished_modules.index, categories=unique_steps_order, ordered=True)

    # Sort the index to reflect the order
    finished_modules = finished_modules.sort_index()

    plt.figure(figsize=(20, 13))
    finished_modules.plot(kind='bar', color='lightgreen')
    plt.title('Number of Modules Finished Each Step')
    plt.xlabel('Steps')
    plt.ylabel('Number of Modules')

    # Adjust font size of x-axis labels
    plt.xticks(rotation=22, ha='right', fontsize=8)

    # Convert plot to HTML image tag
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_tag = f'<img src="data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}" />'
    plt.close()

    return image_tag
#############################################################################################################################################################
def save_flags_to_file(flags_dict, details_dict, filename, username, usergroup, comment):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    usergroup=read_user_group(username)
    if os.path.exists(filename):
        existing_flags_df = pd.read_csv(filename, dtype={'Module Number': str, 'Sensor ID': str, 'Hexboard Number': str, 'Baseplate Number': str, 'Remeasurement Number':str})

        existing_flags_index = existing_flags_df[
            (existing_flags_df['Module Number'] == details_dict['Module Number']) &
            (existing_flags_df['Sensor ID'] == details_dict['Sensor ID']) &
            (existing_flags_df['Hexboard Number'] == details_dict['Hexboard Number']) &
            (existing_flags_df['Baseplate Number'] == details_dict['Baseplate Number']) &
            (existing_flags_df['Remeasurement Number'] == details_dict['Remeasurement Number'])
        ].index

        if not existing_flags_index.empty:
            for index in existing_flags_index:
                for checklist_name, checklist_flags in flags_dict.items():
                    for step, flag in checklist_flags.items():
                        # Update the flag if the step exists for this index
                        if (existing_flags_df.at[index, 'Checklist Name'] == checklist_name and
                                existing_flags_df.at[index, 'Step'] == step):
                            existing_flags_df.at[index, 'Flag'] = flag
                            existing_flags_df.at[index, 'Username'] = username
                            existing_flags_df.at[index, 'UserGroup'] = usergroup
                            existing_flags_df.at[index, 'DateAndTime'] = current_time
                            existing_flags_df.at[index, 'Comment']= comment
            existing_flags_df.to_csv(filename, mode='w', index=False, header=True, sep=',')
            st.success(f"Flags updated in {filename}")

        else:
            all_flags = []
            for checklist_name, checklist_flags in flags_dict.items():
                for step, flag in checklist_flags.items():
                    all_flags.append({
                    'Username': username,
                    'UserGroup': usergroup,
                    'DateAndTime': current_time,
                    'Module Number': details_dict['Module Number'],
                    'Sensor ID': details_dict['Sensor ID'],
                    'Hexboard Number': details_dict['Hexboard Number'],
                    'Baseplate Number': details_dict['Baseplate Number'],
                    'Remeasurement Number': details_dict['Remeasurement Number'],
                    'Checklist Name': checklist_name,
                    'Step': step,
                    'Flag': flag,
                    'Comment': comment
                })
            new_flags_df = pd.DataFrame(all_flags)
            new_flags_df.to_csv(filename, mode='a', index=False, header=False, sep=',')
            st.success(f"Flags appended to {filename}")
    else:
        # Save the flags to a new file if the file doesn't exist
        all_flags = []
        for checklist_name, checklist_flags in flags_dict.items():
            for step, flag in checklist_flags.items():
                all_flags.append({
                    'Username': username,
                    'UserGroup': usergroup,
                    'DateAndTime': current_time,
                    'Module Number': details_dict['Module Number'],
                    'Sensor ID': details_dict['Sensor ID'],
                    'Hexboard Number': details_dict['Hexboard Number'],
                    'Baseplate Number': details_dict['Baseplate Number'],
                    'Remeasurement Number': details_dict['Remeasurement Number'],
                    'Checklist Name': checklist_name,
                    'Step': step,
                    'Flag': flag,
                    'Comment':comment
                })
        flags_df = pd.DataFrame(all_flags)
        flags_df.to_csv(filename, mode='w', index=False, header=True, sep=',')
        st.success(f"Flags saved to {filename}")
################################################################################################################################################
def home_page():
    st.title("Home Page")
    # Add content for the home page
##############################################################################################################################################
def main():
    st.set_page_config(layout="wide", page_title="Your Title", page_icon=":smiley:")
    show_image = True
    logged_in = False

    username = st.sidebar.text_input("Username", key="username_input")  # Unique key for username input
    password_input = st.sidebar.text_input("Password", type="password", key="password_input")  # Unique key for password input
    login_button = st.sidebar.checkbox("Login", key="login_button")  # Unique key for login button
    option = st.sidebar.selectbox("Select an option", ("Home", "Module Assembly Check List", "Unfinished Modules", "Module Status Summary"), key="option_select")  # Unique key for option select

    if login_button:
        if authenticate_user(username, password_input):
            logged_in = True
            show_image = False

            if option == "Home":
                home_page()
            if option == "Module Assembly Check List":
                Module_Assembly_Check_List(username)
            if option == "Unfinished Modules":
                show_unfinished_modules(username)
            if option== "Module Status Summary":
                plot = plot_modules()
                st.markdown(plot, unsafe_allow_html=True)
        else:
            st.error("Please enter the correct username and password")

    if show_image:
        st.title("Login")
        st.image("CMS_detector.jpeg", use_column_width=True)
        st.write("Welcome to the HGCal lab")

        if not login_button and not logged_in:
            st.error("Please log in")
if __name__ == "__main__":
    main()































































