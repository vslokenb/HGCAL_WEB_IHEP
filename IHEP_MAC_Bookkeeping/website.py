import streamlit as st
import yaml
import csv
import pandas as pd
import os
from datetime import datetime,date
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import numpy as np
from mail_notification import send_email_notification
import asyncpg
import asyncio
from inventory import *
from summary_maker import *
from plot_weather import *


PACKAGED_CSV = "data/packaged_modules.csv"

# Function to handle navigation
def navigate(step_change):
    new_index = st.session_state.step_index + step_change
    if 0 <= new_index < len(STEPS):  # Ensure index is within bounds
        st.session_state.step_index = new_index
        st.rerun()

def show_navigation_buttons():
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("\u2B05\uFE0F Previous Step", key="prev_step") and st.session_state.step_index > 0:
            navigate(-1)

    with col2:
        if st.button("\u27A1\uFE0F Next Step", key="next_step") and st.session_state.step_index < len(STEPS) - 1:
            navigate(1)

# Initialize flag status as global variables

STEPS = [
"Overview",
"OGP Before Assembly",
"Hexaboard Electronic Test - Untaped",
"Apply Double-sided Tap Beneath Hexaboard",
"Hexaboard Electronic Test - Taped",
"Assemble Sensor",
"OGP After Assemble Sensor",
"Assemble Hexaboard",
"OGP After Assemble Hexaboard",
"Live Module Electronic Test: Assembled",
"Bonding",
"OGP After Backside Bonding",
"Live Module Electronic Test - Fully Bonded",
"Encapsolation",
"OGP After Encapsolation",
"Live Module Electronic Test - Fully Encapsulated"
]

ogp_before_assembly_flags = {
    'Visual inspection for damage and thickness for sensor': 'red',
    'Thickness and inspection for baseplate': 'red',
    'Thickness and inspection for hexboard': 'red',
    'Cleaning of sensor, baseplate and Hexa- board': 'red'
}

hexaboard_electronic_test_untaped_flags={
    "Hexaboard electronic test: Untaped":"red",
    "Pedestal run: Untaped":"red",
}

apply_double_sided_tap_beneath_hexaboard_flags={
    "Apply double-sided tap beneath Hexaboard":"red",
}

hexaboard_electronic_test_taped_flags={
    "Hexaboard electronic test: Taped":"red",
    "Pedestal run: Taped":"red",
}

# Flag for the OGP Check List title
assemble_sensor_flags={
    "Gluing of silicon sensor on base plate":"red",
}


ogp_after_assemble_sensor_flags = {
    'Inspection of glued base plate + sensor': "red",
}

assemble_hexaboard_flags={
    "Gluing of Hexaboard on protomodule":"red",
}

ogp_after_assemble_hexaboard_flags = {
    'Inspection of module': "red",
}

live_module_electronic_test_assembled_flags={
    'Hexaboard electronic test: Assembled':'red',
    'Pedestal run: Assembled':'red',
}

bonding_flags={
    'Wire bonding of the module':'red',
    'Pull test for frontside bonding':'red',
}

ogp_after_backside_bonding_flags={
    'Visual inspection of bonded module before encapsolation':'red'
}

live_module_electronic_test_fully_bonded_flags={
    'Live module electronic test: Fully Bonded':'red',
    'Standard test procedure: Fully Bonded':'red',
}
module_encapsolation_flags={
    'Encapsolation of the module and curing':'red',
}

ogp_after_module_encapsolation_flags={
    'Visual inspection of encapsulated module':'red',
}

live_module_electronic_test_fully_encapsulated_flags={
    'Live module electronic test: Fully Encapsulated (Final Test)':'red',
    'Standard test procedure: Fully Encapsulated':'red',
}
click_counts_ogp_before_assembly = {step: 0 for step in ogp_before_assembly_flags}
click_counts_hexaboard_electronic_test_untaped = {step: 0 for step in hexaboard_electronic_test_untaped_flags}
click_counts_apply_double_sided_tap_beneath_hexaboard = {step: 0 for step in apply_double_sided_tap_beneath_hexaboard_flags}
click_counts_hexaboard_electronic_test_taped = {step: 0 for step in hexaboard_electronic_test_taped_flags}
click_counts_assemble_sensor = {step: 0 for step in assemble_sensor_flags}
click_counts_ogp_after_assemble_sensor = {step: 0 for step in ogp_after_assemble_sensor_flags}
click_counts_assemble_hexaboard = {step: 0 for step in assemble_hexaboard_flags}
click_counts_ogp_after_assemble_hexaboard = {step: 0 for step in ogp_after_assemble_hexaboard_flags}
click_counts_live_module_electronic_test_assembled = {step: 0 for step in live_module_electronic_test_assembled_flags}
click_counts_bonding = {step: 0 for step in bonding_flags}
click_counts_ogp_after_backside_bonding = {step: 0 for step in ogp_after_backside_bonding_flags}
click_counts_live_module_electronic_test_fully_bonded = {step: 0 for step in live_module_electronic_test_fully_bonded_flags}
click_counts_module_encapsolation = {step: 0 for step in module_encapsolation_flags}
click_counts_ogp_after_module_encapsolation = {step: 0 for step in ogp_after_module_encapsolation_flags}
click_counts_live_module_electronic_test_fully_encapsulated = {step: 0 for step in live_module_electronic_test_fully_encapsulated_flags}


###############################################################################################
def read_user_group(username):
    user_info = pd.read_csv("user/user_info.csv")
    user_group = user_info.loc[user_info['username'] == username, 'group'].values
    return user_group[0] if len(user_group) > 0 else None
##################################################################################################

def authenticate_user(username, password):
    user_info = pd.read_csv("user/user_info.csv")   
    user_info['password'] = user_info['password'].astype(str) 
    #print(user_info['username'])
    #print(user_info['password'])
    if ((user_info['username'] == username) & (user_info['password'] == password)).any():
        return True
    else:
        return False
#################################################################################################

def update_password(username, new_password):
    user_info = pd.read_csv("user/user_info.csv")
    user_info.loc[user_info['username'] == username, 'password'] = new_password
    user_info.to_csv("user/user_info.csv", index=False)
#################################################################################################

def initialize_session_state(module_number=None, sensor_id=None, hexboard_number=None, baseplate_number=None, remeasurement_number=None, verbose=False):
    file_path = "data/output.csv"
    
    if os.path.exists(file_path):
        existing_flags_df = pd.read_csv(file_path, dtype={'Module Number': str, 'Sensor ID': str, 'Hexboard Number': str, 'Baseplate Number': str, 'Remeasurement Number': str})

        # Check if all parameters are provided
        all_params_provided = all([module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number])

        # Match existing records
        if all_params_provided:
            existing_flags = existing_flags_df[
                (existing_flags_df['Module Number'] == module_number) &
                (existing_flags_df['Sensor ID'] == sensor_id) &
                (existing_flags_df['Hexboard Number'] == hexboard_number) &
                (existing_flags_df['Baseplate Number'] == baseplate_number) &
                (existing_flags_df['Remeasurement Number'] == remeasurement_number)
            ]
        else:
            # Search using provided parameters
            conditions = []
            if module_number:
                conditions.append(existing_flags_df['Module Number'] == module_number)
            if sensor_id:
                conditions.append(existing_flags_df['Sensor ID'] == sensor_id)
            if hexboard_number:
                conditions.append(existing_flags_df['Hexboard Number'] == hexboard_number)
            if baseplate_number:
                conditions.append(existing_flags_df['Baseplate Number'] == baseplate_number)
            if remeasurement_number:
                conditions.append(existing_flags_df['Remeasurement Number'] == remeasurement_number)

            if conditions:
                existing_flags = existing_flags_df[np.logical_and.reduce(conditions)]
            else:
                existing_flags = pd.DataFrame()  # Empty DataFrame if no conditions provided

        if not existing_flags.empty:
            if verbose:
                st.success("\u2705 Existing module data retrieved from CSV!")

            # Extract unique matched values
            highlighted_df = existing_flags[['Username', 'Module Number', 'Sensor ID', 'Hexboard Number', 'Baseplate Number', 'Remeasurement Number']].drop_duplicates()

            # Display all matched entries in a table
            if verbose:
                st.write("### Matched Entries Found:")
                st.table(highlighted_df.style.set_properties(**{'background-color': '#FFFF99'}))  # Highlight in yellow

            # If multiple matches exist, notify the user
            if len(highlighted_df) > 1:
                if verbose:
                    st.warning("\u26A0\uFE0F Multiple matches found! Using the first one by default.")

            # Select the first matching row
            selected_row = highlighted_df.iloc[0]

            # Assign matched values back to parameters
            module_number = selected_row['Module Number']
            sensor_id = selected_row['Sensor ID']
            hexboard_number = selected_row['Hexboard Number']
            baseplate_number = selected_row['Baseplate Number']
            remeasurement_number = selected_row['Remeasurement Number']
            username = selected_row['Username']

            if verbose:
                st.info(f"\u2139 Using the first matching entry:\n"
                        f"**Module Number:** {module_number}\n"
                        f"**Sensor ID:** {sensor_id}\n"
                        f"**Hexboard Number:** {hexboard_number}\n"
                        f"**Baseplate Number:** {baseplate_number}\n"
                        f"**Remeasurement Number:** {remeasurement_number}\n"
                        f"**Last status change was made by:** {username}")

            # Filter flags based on selected match
            existing_flags = existing_flags_df[
                (existing_flags_df['Module Number'] == module_number) &
                (existing_flags_df['Sensor ID'] == sensor_id) &
                (existing_flags_df['Hexboard Number'] == hexboard_number) &
                (existing_flags_df['Baseplate Number'] == baseplate_number) &
                (existing_flags_df['Remeasurement Number'] == remeasurement_number)
            ]

            # Update flags
            for index, row in existing_flags.iterrows():
                step_ = row['Step']
                flag_ = row['Flag']
                for flags in [ogp_before_assembly_flags, 
                              hexaboard_electronic_test_untaped_flags,
                              apply_double_sided_tap_beneath_hexaboard_flags,
                              hexaboard_electronic_test_taped_flags,
                              assemble_sensor_flags,
                              ogp_after_assemble_sensor_flags,
                              assemble_hexaboard_flags,
                              ogp_after_assemble_hexaboard_flags,
                              live_module_electronic_test_assembled_flags,
                              bonding_flags,
                              ogp_after_backside_bonding_flags,
                              live_module_electronic_test_fully_bonded_flags,
                              module_encapsolation_flags,
                              ogp_after_module_encapsolation_flags,
                              live_module_electronic_test_fully_encapsulated_flags]:
                    if step_ in flags:
                        flags[step_] = flag_

            return True, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, username

        else:
            if not all_params_provided:
                st.error("\u26A0\uFE0F Incomplete input provided. Please enter all required module details before proceeding.")
                return False, None, None, None, None, None, None  # Incomplete input and no matching data found
            
            if verbose:
                st.warning("\u26A0\uFE0F No existing data found. Initializing module with default values (red flags).")

            # Initialize all flags to 'red'
            for flags in [ogp_before_assembly_flags, 
                          hexaboard_electronic_test_untaped_flags,
                          apply_double_sided_tap_beneath_hexaboard_flags,
                          hexaboard_electronic_test_taped_flags,
                          assemble_sensor_flags,
                          ogp_after_assemble_sensor_flags,
                          assemble_hexaboard_flags,
                          ogp_after_assemble_hexaboard_flags,
                          live_module_electronic_test_assembled_flags,
                          bonding_flags,
                          ogp_after_backside_bonding_flags,
                          live_module_electronic_test_fully_bonded_flags,
                          module_encapsolation_flags,
                          ogp_after_module_encapsolation_flags,
                          live_module_electronic_test_fully_encapsulated_flags]:
                for step_ in flags:
                    flags[step_] = 'red'

            return True, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, None  # Default initialization completed

    else:
        st.error("\u26A0\uFE0F CSV file not found! Ensure the file exists before proceeding.")
        return False, None, None, None, None, None, None  # No CSV file means no data retrieval possible

#################################################################################################

def show_module_info_viewer():
    st.title("Module Info Viewer")
    module_names = asyncio.run(list_module_names())
    selected_module = st.selectbox("Select a module", module_names)
    if selected_module:
        with st.spinner(f"Loading data for module {selected_module}..."):
            module_df = asyncio.run(get_full_info(selected_module))

        if not module_df.empty:
            st.subheader(f"Information for `{selected_module}`")
            st.dataframe(module_df)
        else:
            st.warning("No data found for this module.")
def show_proto_info_viewer():
    st.title("Protomodule Info Viewer")
    protomodule_names = asyncio.run(list_proto_names())
    selected_protomodule = st.selectbox("Select a module", protomodule_names)
    if selected_protomodule:
        with st.spinner(f"Loading data for protomodule {selected_protomodule}..."):
            pmodule_df = asyncio.run(get_proto_info(selected_protomodule))

        if not pmodule_df.empty:
            st.subheader(f"Information for `{selected_protomodule}`")
            st.dataframe(pmodule_df)
        else:
            st.warning("No data found for this protomodule.")
def Module_Assembly_Check_List(username):
    st.title("Welcome to the HGCal module assembly checklist")

    if st.checkbox("Show list of Unfinished Modules"):
        show_unfinished_modules(username)
    if st.checkbox("Show list of Finished Modules"):
        show_finished_modules(username)

    module_number = st.text_input("Enter Module Number")
    sensor_id = st.text_input("Enter Sensor ID")
    hexboard_number = st.text_input("Enter Hexboard Number")
    baseplate_number = st.text_input("Enter Baseplate Number")
    remeasurement_number=st.text_input("Enter Remeasurement Number(0 for the first measurement)")
    comment = st.text_input("Comment*(Optional)")
    usergroup=read_user_group(username)

    success, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, last_user = initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, verbose=True)

    if st.checkbox("Display status"):

        if not success:
            st.error("Cannot proceed further due to incomplete input or missing data.")
            st.stop()  # Prevents the app from executing further steps

        if module_number or sensor_id or hexboard_number or baseplate_number or remeasurement_number:
            if "step_index" not in st.session_state:
                st.session_state.step_index = 0
            option1 = st.selectbox("Select a step", STEPS, index=st.session_state.step_index, key="option1")
            st.session_state.step_index = STEPS.index(option1)
            if option1=='Overview':
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, verbose=False)
                ogp_before_assembly_completed = all(flag == 'green' for flag in ogp_before_assembly_flags.values())
                Ogp_Before_Assembly_Flag = 'green' if ogp_before_assembly_completed else 'red'
                Ogp_Before_Assembly_Icon = '\u2705' if Ogp_Before_Assembly_Flag == 'green' else '\u274C'

                hexaboard_electronic_test_untaped_completed = all(flag == 'green' for flag in hexaboard_electronic_test_untaped_flags.values())
                Hexaboard_Electronic_Test_Untaped_Flag = 'green' if hexaboard_electronic_test_untaped_completed else 'red'
                Hexaboard_Electronic_Test_Untaped_Icon = '\u2705' if Hexaboard_Electronic_Test_Untaped_Flag == 'green' else '\u274C'

                apply_double_sided_tap_beneath_hexaboard_completed = all(flag == 'green' for flag in apply_double_sided_tap_beneath_hexaboard_flags.values())
                Apply_Double_Sided_Tap_Beneath_Hexaboard_Flag = 'green' if apply_double_sided_tap_beneath_hexaboard_completed else 'red'
                Apply_Double_Sided_Tap_Beneath_Hexaboard_Icon = '\u2705' if Apply_Double_Sided_Tap_Beneath_Hexaboard_Flag == 'green' else '\u274C'

                hexaboard_electronic_test_taped_completed = all(flag == 'green' for flag in hexaboard_electronic_test_taped_flags.values())
                Hexaboard_Electronic_Test_Taped_Flag = 'green' if hexaboard_electronic_test_taped_completed else 'red'
                Hexaboard_Electronic_Test_Taped_Icon = '\u2705' if Hexaboard_Electronic_Test_Taped_Flag == 'green' else '\u274C'

                assemble_sensor_completed = all(flag == 'green' for flag in assemble_sensor_flags.values())
                Assemble_Sensor_Flag = 'green' if assemble_sensor_completed else 'red'
                Assemble_Sensor_Icon = '\u2705' if Assemble_Sensor_Flag == 'green' else '\u274C'

                ogp_after_assemble_sensor_completed = all(flag == 'green' for flag in ogp_after_assemble_sensor_flags.values())
                Ogp_After_Assemble_Sensor_Flag = 'green' if ogp_after_assemble_sensor_completed else 'red'
                Ogp_After_Assemble_Sensor_Icon = '\u2705' if Ogp_After_Assemble_Sensor_Flag == 'green' else '\u274C'

                assemble_hexaboard_completed = all(flag == 'green' for flag in assemble_hexaboard_flags.values())
                Assemble_Hexaboard_Flag = 'green' if assemble_hexaboard_completed else 'red'
                Assemble_Hexaboard_Icon = '\u2705' if Assemble_Hexaboard_Flag == 'green' else '\u274C'

                ogp_after_assemble_hexaboard_completed = all(flag == 'green' for flag in ogp_after_assemble_hexaboard_flags.values())
                Ogp_After_Assemble_Hexaboard_Flag = 'green' if ogp_after_assemble_hexaboard_completed else 'red'
                Ogp_After_Assemble_Hexaboard_Icon = '\u2705' if Ogp_After_Assemble_Hexaboard_Flag == 'green' else '\u274C'

                live_module_electronic_test_assembled_completed = all(flag == 'green' for flag in live_module_electronic_test_assembled_flags.values())
                Live_Module_Electronic_Test_Assembled_Flag = 'green' if live_module_electronic_test_assembled_completed else 'red'
                Live_Module_Electronic_Test_Assembled_Icon = '\u2705' if Live_Module_Electronic_Test_Assembled_Flag == 'green' else '\u274C'

                bonding_completed = all(flag == 'green' for flag in bonding_flags.values())
                Bonding_Flag = 'green' if bonding_completed else 'red'
                Bonding_Icon = '\u2705' if Bonding_Flag == 'green' else '\u274C'

                ogp_after_backside_bonding_completed = all(flag == 'green' for flag in ogp_after_backside_bonding_flags.values())
                Ogp_After_Backside_Bonding_Flag = 'green' if ogp_after_backside_bonding_completed else 'red'
                Ogp_After_Backside_Bonding_Icon = '\u2705' if Ogp_After_Backside_Bonding_Flag == 'green' else '\u274C'

                live_module_electronic_test_fully_bonded_completed = all(flag == 'green' for flag in live_module_electronic_test_fully_bonded_flags.values())
                Live_Module_Electronic_Test_Fully_Bonded_Flag = 'green' if live_module_electronic_test_fully_bonded_completed else 'red'
                Live_Module_Electronic_Test_Fully_Bonded_Icon = '\u2705' if Live_Module_Electronic_Test_Fully_Bonded_Flag == 'green' else '\u274C'

                module_encapsolation_completed = all(flag == 'green' for flag in module_encapsolation_flags.values())
                Module_Encapsolation_Flag = 'green' if module_encapsolation_completed else 'red'
                Module_Encapsolation_Icon = '\u2705' if Module_Encapsolation_Flag == 'green' else '\u274C'

                ogp_after_module_encapsolation_completed = all(flag == 'green' for flag in ogp_after_module_encapsolation_flags.values())
                Ogp_After_Module_Encapsolation_Flag = 'green' if ogp_after_module_encapsolation_completed else 'red'
                Ogp_After_Module_Encapsolation_Icon = '\u2705' if Ogp_After_Module_Encapsolation_Flag == 'green' else '\u274C'

                live_module_electronic_test_fully_encapsulated_completed = all(flag == 'green' for flag in live_module_electronic_test_fully_encapsulated_flags.values())
                Live_Module_Electronic_Test_Fully_Encapsulated_Flag = 'green' if live_module_electronic_test_fully_encapsulated_completed else 'red'
                Live_Module_Electronic_Test_Fully_Encapsulated_Icon = '\u2705' if Live_Module_Electronic_Test_Fully_Encapsulated_Flag == 'green' else '\u274C'
 

                col1, col2 = st.columns(2)

                with col2:
                     if st.button("\u27A1\uFE0F Next Step") and st.session_state.step_index < len(STEPS) - 1:
                        navigate(1)

                # Create a DataFrame for a cleaner display
                checklist_df = pd.DataFrame({
                    "Step": [                        
                        "OGP Before Assembly",
                        "Hexaboard Electronic Test - Untaped",
                        "Apply Double-sided Tap Beneath Hexaboard",
                        "Hexaboard Electronic Test - Taped",
                        "Assemble Sensor",
                        "OGP After Assemble Sensor",
                        "Assemble Hexaboard",
                        "OGP After Assemble Hexaboard",
                        "Live Module Electronic Test: Assembled",
                        "Bonding",
                        "OGP After Bonding",
                        "Live Module Electronic Test - Fully Bonded",
                        "Encapsolation",
                        "OGP After Encapsolation",
                        "Live Module Electronic Test - Fully Encapsulated"
                    ],
                    "Status": [
                        Ogp_Before_Assembly_Icon,
                        Hexaboard_Electronic_Test_Untaped_Icon,
                        Apply_Double_Sided_Tap_Beneath_Hexaboard_Icon,
                        Hexaboard_Electronic_Test_Taped_Icon,
                        Assemble_Sensor_Icon,
                        Ogp_After_Assemble_Sensor_Icon,
                        Assemble_Hexaboard_Icon,
                        Ogp_After_Assemble_Hexaboard_Icon,
                        Live_Module_Electronic_Test_Assembled_Icon,
                        Bonding_Icon,
                        Ogp_After_Backside_Bonding_Icon,
                        Live_Module_Electronic_Test_Fully_Bonded_Icon,
                        Module_Encapsolation_Icon,
                        Ogp_After_Module_Encapsolation_Icon,
                        Live_Module_Electronic_Test_Fully_Encapsulated_Icon
                    ]
                })

                # Display as a table
                st.table(checklist_df)
                st.write(f"Last status change was made by: {last_user}")


            if option1 == "OGP Before Assembly":
                success, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, last_user = initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                OGP_before_assembly(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment, last_user)

            elif option1 == "Hexaboard Electronic Test - Untaped":
                success, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, last_user =initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Hexaboard_Electronic_Test_Untaped(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment , last_user)

            elif option1 == "Apply Double-sided Tap Beneath Hexaboard":
                success, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, last_user = initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Apply_Double_Sided_Tap_Beneath_Hexaboard(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment, last_user)

            elif option1 == "Hexaboard Electronic Test - Taped":
                success, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, last_user = initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Hexaboard_Electronic_Test_Taped(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment, last_user)

            elif option1 == "Assemble Sensor":
                success, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, last_user = initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Assemble_Sensor(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment, last_user)

            elif option1 == "OGP After Assemble Sensor":
                success, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, last_user = initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                OGP_After_Assemble_Sensor(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment, last_user)

            elif option1 == "Assemble Hexaboard":
                success, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, last_user = initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Assemble_Hexaboard(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment, last_user)

            elif option1 == "OGP After Assemble Hexaboard":
                success, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, last_user = initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                OGP_After_Assemble_Hexaboard(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment, last_user)

            elif option1 == "Live Module Electronic Test: Assembled":
                success, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, last_user = initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Live_Module_Electronic_Test_Assembled(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment, last_user)

            elif option1 == "Bonding":
                success, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, last_user = initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Bonding(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment, last_user)

            elif option1 == "OGP After Backside Bonding":
                success, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, last_user = initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                OGP_After_Backside_Bonding(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment, last_user)

            elif option1 == "Live Module Electronic Test - Fully Bonded":
                success, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, last_user = initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Live_Module_Electronic_Test_Fully_Bonded(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment, last_user)

            elif option1 == "Encapsolation":
                success, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, last_user = initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, last_user)
                Module_Encapsolation(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment, last_user)

            elif option1 == "OGP After Encapsolation":
                success, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, last_user = initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                OGP_After_Module_Encapsolation(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment, last_user)

            elif option1 == "Live Module Electronic Test - Fully Encapsulated":
                success, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, last_user = initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Live_Module_Electronic_Test_Fully_Encapsulated(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment, last_user)



############################################################################################################################
def OGP_before_assembly(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment, last_user):
    show_navigation_buttons()
    if(read_user_group(username) == 'OGP' or read_user_group(username) == 'All'):
        status_options = {
            '\u2705 Green': 'green',
            '\u26A0\uFE0F Yellow': 'yellow',
            '\u274C Red': 'red'
        }
        for step, flag in ogp_before_assembly_flags.items():
            selected_label = st.radio(
                f"{step} Flag:",
                list(status_options.keys()),  # Show all options as radio buttons
                index=list(status_options.values()).index(flag),
                key=f'{step}_radio',
                help=f'Click count: {click_counts_ogp_before_assembly[step]}'
            )

            # Update flag and click count based on selected option
            ogp_before_assembly_flags[step] = status_options[selected_label]
            click_counts_ogp_before_assembly[step] += 1
        table_data = [[step, '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C', last_user] for step, flag in ogp_before_assembly_flags.items()]
        df_steps = pd.DataFrame(table_data, columns=["Step", "Status", "Status Changed by"])

        # Display step-wise table
        st.write("### OGP Before Assembly Steps Overview")
        st.table(df_steps)

    # Determine overall checklist status
    ogp_before_assembly_completed = all(flag == 'green' for flag in ogp_before_assembly_flags.values())
    Ogp_Before_Assembly_Flag = 'green' if ogp_before_assembly_completed else 'red'
    Ogp_Before_Assembly_Icon = '\u2705' if Ogp_Before_Assembly_Flag == 'green' else '\u274C'
    st.header(f"OGP Before Assembly Check List: {Ogp_Before_Assembly_Icon}")

    if st.button("Save Flags to File"):
        all_checklists_flags = {
            "OGP Before Assembly": ogp_before_assembly_flags,
            "Hexaboard Electronic Test - Untaped": hexaboard_electronic_test_untaped_flags,
            "Apply Double-sided Tap Beneath Hexaboard": apply_double_sided_tap_beneath_hexaboard_flags,
            "Hexaboard Electronic Test - Taped": hexaboard_electronic_test_taped_flags,
            "Assemble Sensor": assemble_sensor_flags,
            "OGP After Assemble Sensor": ogp_after_assemble_sensor_flags,
            "Assemble Hexaboard": assemble_hexaboard_flags,
            "OGP After Assemble Hexaboard": ogp_after_assemble_hexaboard_flags,
            "Live Module Electronic Test - Assembled": live_module_electronic_test_assembled_flags,
            "Bonding": bonding_flags,
            "OGP After Bonding": ogp_after_backside_bonding_flags,
            "Live Module Electronic Test - Fully Bonded": live_module_electronic_test_fully_bonded_flags,
            "Encapsolation": module_encapsolation_flags,
            "OGP After Encapsolation": ogp_after_module_encapsolation_flags,
            "Live Module Electronic Test - Fully Encapsulated": live_module_electronic_test_fully_encapsulated_flags

            }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
                   
        save_flags_to_file(all_checklists_flags, details,"data/output.csv",username,usergroup,comment)
        find_unfinished_modules()

            # Construct email content with detailed info
        subject = "MAC Production Status Change Notification: OGP Before Assembly Check"
        message = f"""Dear OGP Team,

            Please be informed that the status of the step: OGP Before Assembly Check has changed.

            Status: {Ogp_Before_Assembly_Icon}
            Changed by: {username}
            Module Number: {module_number}
            Sensor ID: {sensor_id}
            Hexboard Number: {hexboard_number}
            Baseplate Number: {baseplate_number}
            Remeasurement Number: {remeasurement_number}
            Comment: {comment}

            Best regards,  
            IHEP MAC Checklist Website"""

        send_email_notification(
            group_name="OGP",
            subject=subject,
            message=message,
            sender_email="hgcalcn@cern.ch",
            sender_password="dummyPW"
        )
#####################################################################################################################################
def Hexaboard_Electronic_Test_Untaped(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment, last_user):
    show_navigation_buttons()
    ogp_before_assembly_completed = all(flag == 'green' for flag in ogp_before_assembly_flags.values())
    Ogp_Before_Assembly_Flag = 'green' if ogp_before_assembly_completed else 'red'

    if Ogp_Before_Assembly_Flag=='red':
        st.write("Please finish the previous step first")

    if (read_user_group(username)=='OGP' or read_user_group(username)=='All') and Ogp_Before_Assembly_Flag=='green':
        status_options = {
            '\u2705 Green': 'green',
            '\u26A0\uFE0F Yellow': 'yellow',
            '\u274C Red': 'red'
        }

        for step, flag in hexaboard_electronic_test_untaped_flags.items():
            selected_label = st.radio(
                f"{step} Flag:",
                list(status_options.keys()),  # Show all options as radio buttons
                index=list(status_options.values()).index(flag),
                key=f'{step}_radio',
                help=f'Click count: {click_counts_hexaboard_electronic_test_untaped[step]}'
            )
            hexaboard_electronic_test_untaped_flags[step] = status_options[selected_label]
            click_counts_hexaboard_electronic_test_untaped[step] += 1

        table_data = [[step, '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C', last_user] for step, flag in hexaboard_electronic_test_untaped_flags.items()]
        df_steps = pd.DataFrame(table_data, columns=["Step", "Status", "Status Changed by"])

        st.write("### Hexaboard Electronic Test - Untaped Steps Overview")
        st.table(df_steps)


    hexaboard_electronic_test_untaped_completed = (all(flag == 'green' for flag in hexaboard_electronic_test_untaped_flags.values()))
    Hexaboard_Electronic_Test_Untaped_Flag = 'green' if hexaboard_electronic_test_untaped_completed else 'red'
    Hexaboard_Electronic_Test_Untaped_Icon = '\u2705' if Hexaboard_Electronic_Test_Untaped_Flag == 'green' else '\u274C'
    st.header(f"Hexaboard Electronic Test Check List: {Hexaboard_Electronic_Test_Untaped_Icon}")
    if st.button("Save Flags to File"):
        all_checklists_flags = {
            "OGP Before Assembly": ogp_before_assembly_flags,
            "Hexaboard Electronic Test - Untaped": hexaboard_electronic_test_untaped_flags,
            "Apply Double-sided Tap Beneath Hexaboard": apply_double_sided_tap_beneath_hexaboard_flags,
            "Hexaboard Electronic Test - Taped": hexaboard_electronic_test_taped_flags,
            "Assemble Sensor": assemble_sensor_flags,
            "OGP After Assemble Sensor": ogp_after_assemble_sensor_flags,
            "Assemble Hexaboard": assemble_hexaboard_flags,
            "OGP After Assemble Hexaboard": ogp_after_assemble_hexaboard_flags,
            "Live Module Electronic Test - Assembled": live_module_electronic_test_assembled_flags,
            "Bonding": bonding_flags,
            "OGP After Bonding": ogp_after_backside_bonding_flags,
            "Live Module Electronic Test - Fully Bonded": live_module_electronic_test_fully_bonded_flags,
            "Encapsolation": module_encapsolation_flags,
            "OGP After Encapsolation": ogp_after_module_encapsolation_flags,
            "Live Module Electronic Test - Fully Encapsulated": live_module_electronic_test_fully_encapsulated_flags

            }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
                   
        save_flags_to_file(all_checklists_flags, details,"data/output.csv",username,usergroup,comment)
        find_unfinished_modules()

        subject = " MAC Production Status Change Notification: Hexaboard Electronic Test - Untaped"
        message = f"""Dear OGP Team,

            Please be informed that the status of the step: Hexaboard Electronic Test - Untaped has changed.

            Status: {Hexaboard_Electronic_Test_Untaped_Icon}
            Changed by: {username}
            Module Number: {module_number}
            Sensor ID: {sensor_id}
            Hexboard Number: {hexboard_number}
            Baseplate Number: {baseplate_number}
            Remeasurement Number: {remeasurement_number}
            Comment: {comment}

            Best regards,  
            IHEP MAC Checklist Website"""

        send_email_notification(
            group_name="OGP",
            subject=subject,
            message=message,
            sender_email="hgcalcn@cern.ch",
            sender_password="dummyPW"
        )
######################################################################################################################################

def Apply_Double_Sided_Tap_Beneath_Hexaboard(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment, last_user):
    show_navigation_buttons()
    previous_step_completed = all(flag == 'green' for flag in hexaboard_electronic_test_untaped_flags.values())
    previous_step_flag = 'green' if previous_step_completed else 'red'

    if previous_step_flag == 'red':
        st.write("Please finish the previous step first")

    if (read_user_group(username) in ['OGP', 'All']) and previous_step_flag == 'green':
        status_options = {'\u2705 Green': 'green', '\u26A0\uFE0F Yellow': 'yellow', '\u274C Red': 'red'}

        for step, flag in apply_double_sided_tap_beneath_hexaboard_flags.items():
            selected_label = st.radio(f"{step} Flag:", list(status_options.keys()), index=list(status_options.values()).index(flag),
                                      key=f'{step}_radio', help=f'Click count: {click_counts_apply_double_sided_tap_beneath_hexaboard[step]}')
            apply_double_sided_tap_beneath_hexaboard_flags[step] = status_options[selected_label]
            click_counts_apply_double_sided_tap_beneath_hexaboard[step] += 1

        table_data = [[step, '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C', last_user]
                      for step, flag in apply_double_sided_tap_beneath_hexaboard_flags.items()]
        df_steps = pd.DataFrame(table_data, columns=["Step", "Status", "Status Changed by"])

        st.write("### Apply Double-sided Tap Beneath Hexaboard Steps Overview")
        st.table(df_steps)

    apply_double_sided_tap_beneath_hexaboard_completed = all(flag == 'green' for flag in apply_double_sided_tap_beneath_hexaboard_flags.values())
    Apply_Double_Sided_Tap_Beneath_Hexaboard_Flag = 'green' if apply_double_sided_tap_beneath_hexaboard_completed else 'red'
    Apply_Double_Sided_Tap_Beneath_Hexaboard_Icon = '\u2705' if Apply_Double_Sided_Tap_Beneath_Hexaboard_Flag == 'green' else '\u274C'
    st.header(f"Apply Double-sided Tap Beneath Hexaboard Check List: {Apply_Double_Sided_Tap_Beneath_Hexaboard_Icon}")



    if st.button("Save Flags to File"):
        all_checklists_flags = {
            "OGP Before Assembly": ogp_before_assembly_flags,
            "Hexaboard Electronic Test - Untaped": hexaboard_electronic_test_untaped_flags,
            "Apply Double-sided Tap Beneath Hexaboard": apply_double_sided_tap_beneath_hexaboard_flags,
            "Hexaboard Electronic Test - Taped": hexaboard_electronic_test_taped_flags,
            "Assemble Sensor": assemble_sensor_flags,
            "OGP After Assemble Sensor": ogp_after_assemble_sensor_flags,
            "Assemble Hexaboard": assemble_hexaboard_flags,
            "OGP After Assemble Hexaboard": ogp_after_assemble_hexaboard_flags,
            "Live Module Electronic Test - Assembled": live_module_electronic_test_assembled_flags,
            "Bonding": bonding_flags,
            "OGP After Bonding": ogp_after_backside_bonding_flags,
            "Live Module Electronic Test - Fully Bonded": live_module_electronic_test_fully_bonded_flags,
            "Encapsolation": module_encapsolation_flags,
            "OGP After Encapsolation": ogp_after_module_encapsolation_flags,
            "Live Module Electronic Test - Fully Encapsulated": live_module_electronic_test_fully_encapsulated_flags

            }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
        save_flags_to_file(all_checklists_flags, details,"data/output.csv",username,usergroup,comment)
        find_unfinished_modules()

        subject = "MAC Production Status Change Notification: Apply Double-sided Tap Beneath Hexaboard"
        message = f"""Dear OGP Team,

            Please be informed that the status of the step: Apply Double-sided Tap Beneath Hexaboard has changed.

            Status: {Apply_Double_Sided_Tap_Beneath_Hexaboard_Icon}
            Changed by: {username}
            Module Number: {module_number}
            Sensor ID: {sensor_id}
            Hexboard Number: {hexboard_number}
            Baseplate Number: {baseplate_number}
            Remeasurement Number: {remeasurement_number}
            Comment: {comment}

            Best regards,  
            IHEP MAC Checklist Website"""

        send_email_notification(
            group_name="OGP",
            subject=subject,
            message=message,
            sender_email="hgcalcn@cern.ch",
            sender_password="dummyPW"
        )

######################################################################################################################################

def Hexaboard_Electronic_Test_Taped(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment, last_user):
    show_navigation_buttons()
    previous_step_completed = all(flag == 'green' for flag in apply_double_sided_tap_beneath_hexaboard_flags.values())
    previous_step_flag = 'green' if previous_step_completed else 'red'

    if previous_step_flag == 'red':
        st.write("Please finish the previous step first")

    if (read_user_group(username) in ['Electrical', 'All']) and previous_step_flag == 'green':
        status_options = {'\u2705 Green': 'green', '\u26A0\uFE0F Yellow': 'yellow', '\u274C Red': 'red'}

        for step, flag in hexaboard_electronic_test_taped_flags.items():
            selected_label = st.radio(f"{step} Flag:", list(status_options.keys()), index=list(status_options.values()).index(flag),
                                      key=f'{step}_radio', help=f'Click count: {click_counts_hexaboard_electronic_test_taped[step]}')
            hexaboard_electronic_test_taped_flags[step] = status_options[selected_label]
            click_counts_hexaboard_electronic_test_taped[step] += 1

        table_data = [[step, '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C', last_user]
                      for step, flag in hexaboard_electronic_test_taped_flags.items()]
        df_steps = pd.DataFrame(table_data, columns=["Step", "Status", "Status Changed by"])

        st.write("### Hexaboard Electronic Test - Taped Steps Overview")
        st.table(df_steps)

    hexaboard_electronic_test_taped_completed = all(flag == 'green' for flag in hexaboard_electronic_test_taped_flags.values())
    Hexaboard_Electronic_Test_Taped_Flag = 'green' if hexaboard_electronic_test_taped_completed else 'red'
    Hexaboard_Electronic_Test_Taped_Icon = '\u2705' if Hexaboard_Electronic_Test_Taped_Flag == 'green' else '\u274C'
    st.header(f"Hexaboard Electronic Test - Taped Check List: {Hexaboard_Electronic_Test_Taped_Icon}")

    if st.button("Save Flags to File"):
        all_checklists_flags = {
            "OGP Before Assembly": ogp_before_assembly_flags,
            "Hexaboard Electronic Test - Untaped": hexaboard_electronic_test_untaped_flags,
            "Apply Double-sided Tap Beneath Hexaboard": apply_double_sided_tap_beneath_hexaboard_flags,
            "Hexaboard Electronic Test - Taped": hexaboard_electronic_test_taped_flags,
            "Assemble Sensor": assemble_sensor_flags,
            "OGP After Assemble Sensor": ogp_after_assemble_sensor_flags,
            "Assemble Hexaboard": assemble_hexaboard_flags,
            "OGP After Assemble Hexaboard": ogp_after_assemble_hexaboard_flags,
            "Live Module Electronic Test - Assembled": live_module_electronic_test_assembled_flags,
            "Bonding": bonding_flags,
            "OGP After Bonding": ogp_after_backside_bonding_flags,
            "Live Module Electronic Test - Fully Bonded": live_module_electronic_test_fully_bonded_flags,
            "Encapsolation": module_encapsolation_flags,
            "OGP After Encapsolation": ogp_after_module_encapsolation_flags,
            "Live Module Electronic Test - Fully Encapsulated": live_module_electronic_test_fully_encapsulated_flags

            }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
    
        save_flags_to_file(all_checklists_flags, {'Module Number': module_number, 'Sensor ID': sensor_id, 'Hexboard Number': hexboard_number,
                                                  'Baseplate Number': baseplate_number, 'Remeasurement Number': remeasurement_number},
                           "data/output.csv", username, usergroup, comment)
        find_unfinished_modules()

        subject = "MAC Production Status Change Notification: Hexaboard Electronic Test - Taped"
        message = f"""Dear OGP and Gantry Teams,

            Please be informed that the status of the step: Hexaboard Electronic Test - Taped has changed.

            Status: {Hexaboard_Electronic_Test_Taped_Icon}
            Changed by: {username}
            Module Number: {module_number}
            Sensor ID: {sensor_id}
            Hexboard Number: {hexboard_number}
            Baseplate Number: {baseplate_number}
            Remeasurement Number: {remeasurement_number}
            Comment: {comment}

            Best regards,  
            IHEP MAC Checklist Website"""

        send_email_notification(
            group_name="OGP",
            subject=subject,
            message=message,
            sender_email="hgcalcn@cern.ch",
            sender_password="dummyPW"
        )
        send_email_notification(
            group_name="Gantry",
            subject=subject,
            message=message,
            sender_email="hgcalcn@cern.ch",
            sender_password="dummyPW"
        )

######################################################################################################################################

def Assemble_Sensor(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment, last_user):
    show_navigation_buttons()
    previous_step_completed = all(flag == 'green' for flag in hexaboard_electronic_test_taped_flags.values())
    previous_step_flag = 'green' if previous_step_completed else 'red'

    if previous_step_flag == 'red':
        st.write("Please finish the previous step first")

    if (read_user_group(username) in ['Gantry', 'All']) and previous_step_flag == 'green':
        status_options = {'\u2705 Green': 'green', '\u26A0\uFE0F Yellow': 'yellow', '\u274C Red': 'red'}

        for step, flag in assemble_sensor_flags.items():
            selected_label = st.radio(f"{step} Flag:", list(status_options.keys()), 
                                      index=list(status_options.values()).index(flag), 
                                      key=f'{step}_radio', 
                                      help=f'Click count: {click_counts_assemble_sensor[step]}')
            assemble_sensor_flags[step] = status_options[selected_label]
            click_counts_assemble_sensor[step] += 1

        table_data = [[step, '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C', last_user] 
                      for step, flag in assemble_sensor_flags.items()]
        df_steps = pd.DataFrame(table_data, columns=["Step", "Status", "Status Changed by"])

        st.write("### Assemble Sensor Steps Overview")
        st.table(df_steps)

    assemble_sensor_completed = all(flag == 'green' for flag in assemble_sensor_flags.values())
    Assemble_Sensor_Flag = 'green' if assemble_sensor_completed else 'red'
    Assemble_Sensor_Icon = '\u2705' if Assemble_Sensor_Flag == 'green' else '\u274C'
    st.header(f"Assemble Sensor Check List: {Assemble_Sensor_Icon}")

    if st.button("Save Flags to File"):
        all_checklists_flags = {
            "OGP Before Assembly": ogp_before_assembly_flags,
            "Hexaboard Electronic Test - Untaped": hexaboard_electronic_test_untaped_flags,
            "Apply Double-sided Tap Beneath Hexaboard": apply_double_sided_tap_beneath_hexaboard_flags,
            "Hexaboard Electronic Test - Taped": hexaboard_electronic_test_taped_flags,
            "Assemble Sensor": assemble_sensor_flags,
            "OGP After Assemble Sensor": ogp_after_assemble_sensor_flags,
            "Assemble Hexaboard": assemble_hexaboard_flags,
            "OGP After Assemble Hexaboard": ogp_after_assemble_hexaboard_flags,
            "Live Module Electronic Test - Assembled": live_module_electronic_test_assembled_flags,
            "Bonding": bonding_flags,
            "OGP After Bonding": ogp_after_backside_bonding_flags,
            "Live Module Electronic Test - Fully Bonded": live_module_electronic_test_fully_bonded_flags,
            "Encapsolation": module_encapsolation_flags,
            "OGP After Encapsolation": ogp_after_module_encapsolation_flags,
            "Live Module Electronic Test - Fully Encapsulated": live_module_electronic_test_fully_encapsulated_flags

            }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
    
        save_flags_to_file(all_checklists_flags, {'Module Number': module_number, 'Sensor ID': sensor_id, 'Hexboard Number': hexboard_number,
                                                  'Baseplate Number': baseplate_number, 'Remeasurement Number': remeasurement_number},
                           "data/output.csv", username, usergroup, comment)
        find_unfinished_modules()

        subject = "MAC Production Status Change Notification: Assemble Sensor"
        message = f"""Dear OGP and Gantry Teams,

            Please be informed that the status of the step: Assemble Sensor has changed.

            Status: {Assemble_Sensor_Icon}
            Changed by: {username}
            Module Number: {module_number}
            Sensor ID: {sensor_id}
            Hexboard Number: {hexboard_number}
            Baseplate Number: {baseplate_number}
            Remeasurement Number: {remeasurement_number}
            Comment: {comment}

            Best regards,  
            IHEP MAC Checklist Website"""

        send_email_notification(
            group_name="Gantry",
            subject=subject,
            message=message,
            sender_email="hgcalcn@cern.ch",
            sender_password="dummyPW"
        )
        send_email_notification(
            group_name="OGP",
            subject=subject,
            message=message,
            sender_email="hgcalcn@cern.ch",
            sender_password="dummyPW"
        )
######################################################################################################################################


def OGP_After_Assemble_Sensor(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment, last_user):
    show_navigation_buttons()
    previous_step_completed = all(flag == 'green' for flag in assemble_sensor_flags.values())
    previous_step_flag = 'green' if previous_step_completed else 'red'

    if previous_step_flag == 'red':
        st.write("Please finish the previous step first")

    if (read_user_group(username) in ['OGP', 'All']) and previous_step_flag == 'green':
        status_options = {'\u2705 Green': 'green', '\u26A0\uFE0F Yellow': 'yellow', '\u274C Red': 'red'}

        for step, flag in ogp_after_assemble_sensor_flags.items():
            selected_label = st.radio(f"{step} Flag:", list(status_options.keys()), 
                                      index=list(status_options.values()).index(flag), 
                                      key=f'{step}_radio', 
                                      help=f'Click count: {click_counts_ogp_after_assemble_sensor[step]}')
            ogp_after_assemble_sensor_flags[step] = status_options[selected_label]
            click_counts_ogp_after_assemble_sensor[step] += 1

        table_data = [[step, '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C', last_user] 
                      for step, flag in ogp_after_assemble_sensor_flags.items()]
        df_steps = pd.DataFrame(table_data, columns=["Step", "Status", "Status Changed by"])

        st.write("### OGP After Assemble Sensor Steps Overview")
        st.table(df_steps)

    ogp_after_assemble_sensor_completed = all(flag == 'green' for flag in ogp_after_assemble_sensor_flags.values())
    OGP_After_Assemble_Sensor_Flag = 'green' if ogp_after_assemble_sensor_completed else 'red'
    OGP_After_Assemble_Sensor_Icon = '\u2705' if OGP_After_Assemble_Sensor_Flag == 'green' else '\u274C'
    st.header(f"OGP After Assemble Sensor Check List: {OGP_After_Assemble_Sensor_Icon}")

    if st.button("Save Flags to File"):
        all_checklists_flags = {
            "OGP Before Assembly": ogp_before_assembly_flags,
            "Hexaboard Electronic Test - Untaped": hexaboard_electronic_test_untaped_flags,
            "Apply Double-sided Tap Beneath Hexaboard": apply_double_sided_tap_beneath_hexaboard_flags,
            "Hexaboard Electronic Test - Taped": hexaboard_electronic_test_taped_flags,
            "Assemble Sensor": assemble_sensor_flags,
            "OGP After Assemble Sensor": ogp_after_assemble_sensor_flags,
            "Assemble Hexaboard": assemble_hexaboard_flags,
            "OGP After Assemble Hexaboard": ogp_after_assemble_hexaboard_flags,
            "Live Module Electronic Test - Assembled": live_module_electronic_test_assembled_flags,
            "Bonding": bonding_flags,
            "OGP After Bonding": ogp_after_backside_bonding_flags,
            "Live Module Electronic Test - Fully Bonded": live_module_electronic_test_fully_bonded_flags,
            "Encapsolation": module_encapsolation_flags,
            "OGP After Encapsolation": ogp_after_module_encapsolation_flags,
            "Live Module Electronic Test - Fully Encapsulated": live_module_electronic_test_fully_encapsulated_flags

            }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
                   
        save_flags_to_file(all_checklists_flags, details,"data/output.csv",username,usergroup,comment)
        find_unfinished_modules()

        subject = "MAC Production Status Change Notification: OGP After Assemble Sensor"
        message = f"""Dear OGP and Gantry Teams,

            Please be informed that the status of the step: OGP After Assemble Sensor has changed.

            Status: {OGP_After_Assemble_Sensor_Icon}
            Changed by: {username}
            Module Number: {module_number}
            Sensor ID: {sensor_id}
            Hexboard Number: {hexboard_number}
            Baseplate Number: {baseplate_number}
            Remeasurement Number: {remeasurement_number}
            Comment: {comment}

            Best regards,  
            IHEP MAC Checklist Website"""

        send_email_notification(
            group_name="OGP",
            subject=subject,
            message=message,
            sender_email="hgcalcn@cern.ch",
            sender_password="dummyPW"
        )
        send_email_notification(
            group_name="Gantry",
            subject=subject,
            message=message,
            sender_email="hgcalcn@cern.ch",
            sender_password="dummyPW"
        )

######################################################################################################################################

def Assemble_Hexaboard(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment, last_user):
    show_navigation_buttons()
    previous_step_completed = all(flag == 'green' for flag in ogp_after_assemble_sensor_flags.values())
    previous_step_flag = 'green' if previous_step_completed else 'red'

    if previous_step_flag == 'red':
        st.write("Please finish the previous step first")

    if (read_user_group(username) in ['Gantry', 'All']) and previous_step_flag == 'green':
        status_options = {'\u2705 Green': 'green', '\u26A0\uFE0F Yellow': 'yellow', '\u274C Red': 'red'}

        for step, flag in assemble_hexaboard_flags.items():
            selected_label = st.radio(f"{step} Flag:", list(status_options.keys()), 
                                      index=list(status_options.values()).index(flag), 
                                      key=f'{step}_radio', 
                                      help=f'Click count: {click_counts_assemble_hexaboard[step]}')
            assemble_hexaboard_flags[step] = status_options[selected_label]
            click_counts_assemble_hexaboard[step] += 1

        table_data = [[step, '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C', last_user] 
                      for step, flag in assemble_hexaboard_flags.items()]
        df_steps = pd.DataFrame(table_data, columns=["Step", "Status", "Status Changed by"])

        st.write("### Assemble Hexaboard Steps Overview")
        st.table(df_steps)

    assemble_hexaboard_completed = all(flag == 'green' for flag in assemble_hexaboard_flags.values())
    Assemble_Hexaboard_Flag = 'green' if assemble_hexaboard_completed else 'red'
    Assemble_Hexaboard_Icon = '\u2705' if Assemble_Hexaboard_Flag == 'green' else '\u274C'
    st.header(f"Assemble Hexaboard Check List: {Assemble_Hexaboard_Icon}")

    if st.button("Save Flags to File"):
        all_checklists_flags = {
            "OGP Before Assembly": ogp_before_assembly_flags,
            "Hexaboard Electronic Test - Untaped": hexaboard_electronic_test_untaped_flags,
            "Apply Double-sided Tap Beneath Hexaboard": apply_double_sided_tap_beneath_hexaboard_flags,
            "Hexaboard Electronic Test - Taped": hexaboard_electronic_test_taped_flags,
            "Assemble Sensor": assemble_sensor_flags,
            "OGP After Assemble Sensor": ogp_after_assemble_sensor_flags,
            "Assemble Hexaboard": assemble_hexaboard_flags,
            "OGP After Assemble Hexaboard": ogp_after_assemble_hexaboard_flags,
            "Live Module Electronic Test - Assembled": live_module_electronic_test_assembled_flags,
            "Bonding": bonding_flags,
            "OGP After Bonding": ogp_after_backside_bonding_flags,
            "Live Module Electronic Test - Fully Bonded": live_module_electronic_test_fully_bonded_flags,
            "Encapsolation": module_encapsolation_flags,
            "OGP After Encapsolation": ogp_after_module_encapsolation_flags,
            "Live Module Electronic Test - Fully Encapsulated": live_module_electronic_test_fully_encapsulated_flags

            }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
                   
        save_flags_to_file(all_checklists_flags, details,"data/output.csv",username,usergroup,comment)
        find_unfinished_modules()

        subject = "MAC Production Status Change Notification: Assemble Hexaboard"
        message = f"""Dear Gantry and OGP Teams,

            Please be informed that the status of the step: Assemble Hexaboard has changed.

            Status: {Assemble_Hexaboard_Icon}
            Changed by: {username}
            Module Number: {module_number}
            Sensor ID: {sensor_id}
            Hexboard Number: {hexboard_number}
            Baseplate Number: {baseplate_number}
            Remeasurement Number: {remeasurement_number}
            Comment: {comment}

            Best regards,  
            IHEP MAC Checklist Website"""

        send_email_notification(
            group_name="Gantry",
            subject=subject,
            message=message,
            sender_email="hgcalcn@cern.ch",
            sender_password="dummyPW"
        )
        send_email_notification(
            group_name="OGP",
            subject=subject,
            message=message,
            sender_email="hgcalcn@cern.ch",
            sender_password="dummyPW"
        )

######################################################################################################################################


def OGP_After_Assemble_Hexaboard(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment, last_user):
    show_navigation_buttons()
    previous_step_completed = all(flag == 'green' for flag in assemble_hexaboard_flags.values())
    previous_step_flag = 'green' if previous_step_completed else 'red'

    if previous_step_flag == 'red':
        st.write("Please finish the previous step first")

    if (read_user_group(username) in ['OGP', 'All']) and previous_step_flag == 'green':
        status_options = {'\u2705 Green': 'green', '\u26A0\uFE0F Yellow': 'yellow', '\u274C Red': 'red'}

        for step, flag in ogp_after_assemble_hexaboard_flags.items():
            selected_label = st.radio(f"{step} Flag:", list(status_options.keys()), 
                                      index=list(status_options.values()).index(flag), 
                                      key=f'{step}_radio', 
                                      help=f'Click count: {click_counts_ogp_after_assemble_hexaboard[step]}')
            ogp_after_assemble_hexaboard_flags[step] = status_options[selected_label]
            click_counts_ogp_after_assemble_hexaboard[step] += 1

        table_data = [[step, '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C', last_user] 
                      for step, flag in ogp_after_assemble_hexaboard_flags.items()]
        df_steps = pd.DataFrame(table_data, columns=["Step", "Status", "Status Changed by"])

        st.write("### OGP After Assemble Hexaboard Steps Overview")
        st.table(df_steps)

    ogp_after_assemble_hexaboard_completed = all(flag == 'green' for flag in ogp_after_assemble_hexaboard_flags.values())
    OGP_After_Assemble_Hexaboard_Flag = 'green' if ogp_after_assemble_hexaboard_completed else 'red'
    OGP_After_Assemble_Hexaboard_Icon = '\u2705' if OGP_After_Assemble_Hexaboard_Flag == 'green' else '\u274C'
    st.header(f"OGP After Assemble Hexaboard Check List: {OGP_After_Assemble_Hexaboard_Icon}")

    if st.button("Save Flags to File"):
        all_checklists_flags = {
            "OGP Before Assembly": ogp_before_assembly_flags,
            "Hexaboard Electronic Test - Untaped": hexaboard_electronic_test_untaped_flags,
            "Apply Double-sided Tap Beneath Hexaboard": apply_double_sided_tap_beneath_hexaboard_flags,
            "Hexaboard Electronic Test - Taped": hexaboard_electronic_test_taped_flags,
            "Assemble Sensor": assemble_sensor_flags,
            "OGP After Assemble Sensor": ogp_after_assemble_sensor_flags,
            "Assemble Hexaboard": assemble_hexaboard_flags,
            "OGP After Assemble Hexaboard": ogp_after_assemble_hexaboard_flags,
            "Live Module Electronic Test - Assembled": live_module_electronic_test_assembled_flags,
            "Bonding": bonding_flags,
            "OGP After Bonding": ogp_after_backside_bonding_flags,
            "Live Module Electronic Test - Fully Bonded": live_module_electronic_test_fully_bonded_flags,
            "Encapsolation": module_encapsolation_flags,
            "OGP After Encapsolation": ogp_after_module_encapsolation_flags,
            "Live Module Electronic Test - Fully Encapsulated": live_module_electronic_test_fully_encapsulated_flags

            }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
                   
        save_flags_to_file(all_checklists_flags, details,"data/output.csv",username,usergroup,comment)
        find_unfinished_modules()

        subject = "MAC Production Status Change Notification: OGP After Assemble Hexaboard"
        message = f"""Dear Electrical Test and OGP Teams,

            Please be informed that the status of the step: OGP After Assemble Hexaboard has changed.

            Status: {OGP_After_Assemble_Hexaboard_Icon}
            Changed by: {username}
            Module Number: {module_number}
            Sensor ID: {sensor_id}
            Hexboard Number: {hexboard_number}
            Baseplate Number: {baseplate_number}
            Remeasurement Number: {remeasurement_number}
            Comment: {comment}

            Best regards,  
            IHEP MAC Checklist Website"""

        send_email_notification(
            group_name="OGP",
            subject=subject,
            message=message,
            sender_email="hgcalcn@cern.ch",
            sender_password="dummyPW"
        )
        send_email_notification(
            group_name="Electrical",
            subject=subject,
            message=message,
            sender_email="hgcalcn@cern.ch",
            sender_password="dummyPW"
        )

######################################################################################################################################

def Live_Module_Electronic_Test_Assembled(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment, last_user):
    show_navigation_buttons()
    previous_step_completed = all(flag == 'green' for flag in ogp_after_assemble_hexaboard_flags.values())
    previous_step_flag = 'green' if previous_step_completed else 'red'

    if previous_step_flag == 'red':
        st.write("Please finish the previous step first")

    if (read_user_group(username) in ['Electrical', 'All']) and previous_step_flag == 'green':
        status_options = {'\u2705 Green': 'green', '\u26A0\uFE0F Yellow': 'yellow', '\u274C Red': 'red'}

        for step, flag in live_module_electronic_test_assembled_flags.items():
            selected_label = st.radio(f"{step} Flag:", list(status_options.keys()), 
                                      index=list(status_options.values()).index(flag), 
                                      key=f'{step}_radio', 
                                      help=f'Click count: {click_counts_live_module_electronic_test_assembled[step]}')
            live_module_electronic_test_assembled_flags[step] = status_options[selected_label]
            click_counts_live_module_electronic_test_assembled[step] += 1

        table_data = [[step, '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C', last_user] 
                      for step, flag in live_module_electronic_test_assembled_flags.items()]
        df_steps = pd.DataFrame(table_data, columns=["Step", "Status", "Status Changed by"])

        st.write("### Live Module Electronic Test: Assembled Steps Overview")
        st.table(df_steps)

    live_module_electronic_test_assembled_completed = all(flag == 'green' for flag in live_module_electronic_test_assembled_flags.values())
    Live_Module_Electronic_Test_Assembled_Flag = 'green' if live_module_electronic_test_assembled_completed else 'red'
    Live_Module_Electronic_Test_Assembled_Icon = '\u2705' if Live_Module_Electronic_Test_Assembled_Flag == 'green' else '\u274C'
    st.header(f"Live Module Electronic Test: Assembled Check List: {Live_Module_Electronic_Test_Assembled_Icon}")

    if st.button("Save Flags to File"):
        all_checklists_flags = {
            "OGP Before Assembly": ogp_before_assembly_flags,
            "Hexaboard Electronic Test - Untaped": hexaboard_electronic_test_untaped_flags,
            "Apply Double-sided Tap Beneath Hexaboard": apply_double_sided_tap_beneath_hexaboard_flags,
            "Hexaboard Electronic Test - Taped": hexaboard_electronic_test_taped_flags,
            "Assemble Sensor": assemble_sensor_flags,
            "OGP After Assemble Sensor": ogp_after_assemble_sensor_flags,
            "Assemble Hexaboard": assemble_hexaboard_flags,
            "OGP After Assemble Hexaboard": ogp_after_assemble_hexaboard_flags,
            "Live Module Electronic Test - Assembled": live_module_electronic_test_assembled_flags,
            "Bonding": bonding_flags,
            "OGP After Bonding": ogp_after_backside_bonding_flags,
            "Live Module Electronic Test - Fully Bonded": live_module_electronic_test_fully_bonded_flags,
            "Encapsolation": module_encapsolation_flags,
            "OGP After Encapsolation": ogp_after_module_encapsolation_flags,
            "Live Module Electronic Test - Fully Encapsulated": live_module_electronic_test_fully_encapsulated_flags

            }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
                   
        save_flags_to_file(all_checklists_flags, details,"data/output.csv",username,usergroup,comment)
        find_unfinished_modules()

        subject = "MAC Production Status Change Notification: Live Module Electronic Test: Assembled"
        message = f"""Dear Bonding and Electrical Test Teams,

            Please be informed that the status of the step: Live Module Electronic Test: Assembled has changed.

            Status: {Live_Module_Electronic_Test_Assembled_Icon}
            Changed by: {username}
            Module Number: {module_number}
            Sensor ID: {sensor_id}
            Hexboard Number: {hexboard_number}
            Baseplate Number: {baseplate_number}
            Remeasurement Number: {remeasurement_number}
            Comment: {comment}

            Best regards,  
            IHEP MAC Checklist Website"""

        send_email_notification(
            group_name="Electrical",
            subject=subject,
            message=message,
            sender_email="hgcalcn@cern.ch",
            sender_password="dummyPW"
        )
        send_email_notification(
            group_name="Bonding",
            subject=subject,
            message=message,
            sender_email="hgcalcn@cern.ch",
            sender_password="dummyPW"
        )


######################################################################################################################################

def Bonding(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment, last_user):
    show_navigation_buttons()
    previous_step_completed = all(flag == 'green' for flag in live_module_electronic_test_assembled_flags.values())
    previous_step_flag = 'green' if previous_step_completed else 'red'

    if previous_step_flag == 'red':
        st.write("Please finish the previous step first")

    if (read_user_group(username) in ['Bonding', 'All']) and previous_step_flag == 'green':
        status_options = {'\u2705 Green': 'green', '\u26A0\uFE0F Yellow': 'yellow', '\u274C Red': 'red'}

        for step, flag in bonding_flags.items():
            selected_label = st.radio(f"{step} Flag:", list(status_options.keys()), 
                                      index=list(status_options.values()).index(flag), 
                                      key=f'{step}_radio', 
                                      help=f'Click count: {click_counts_bonding[step]}')
            bonding_flags[step] = status_options[selected_label]
            click_counts_bonding[step] += 1

        table_data = [[step, '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C', last_user] 
                      for step, flag in bonding_flags.items()]
        df_steps = pd.DataFrame(table_data, columns=["Step", "Status", "Status Changed by"])

        st.write("### Bonding Steps Overview")
        st.table(df_steps)

    bonding_completed = all(flag == 'green' for flag in bonding_flags.values())
    Bonding_Flag = 'green' if bonding_completed else 'red'
    Bonding_Icon = '\u2705' if Bonding_Flag == 'green' else '\u274C'
    st.header(f"Bonding Check List: {Bonding_Icon}")

    if st.button("Save Flags to File"):
        all_checklists_flags = {
            "OGP Before Assembly": ogp_before_assembly_flags,
            "Hexaboard Electronic Test - Untaped": hexaboard_electronic_test_untaped_flags,
            "Apply Double-sided Tap Beneath Hexaboard": apply_double_sided_tap_beneath_hexaboard_flags,
            "Hexaboard Electronic Test - Taped": hexaboard_electronic_test_taped_flags,
            "Assemble Sensor": assemble_sensor_flags,
            "OGP After Assemble Sensor": ogp_after_assemble_sensor_flags,
            "Assemble Hexaboard": assemble_hexaboard_flags,
            "OGP After Assemble Hexaboard": ogp_after_assemble_hexaboard_flags,
            "Live Module Electronic Test - Assembled": live_module_electronic_test_assembled_flags,
            "Bonding": bonding_flags,
            "OGP After Bonding": ogp_after_backside_bonding_flags,
            "Live Module Electronic Test - Fully Bonded": live_module_electronic_test_fully_bonded_flags,
            "Encapsolation": module_encapsolation_flags,
            "OGP After Encapsolation": ogp_after_module_encapsolation_flags,
            "Live Module Electronic Test - Fully Encapsulated": live_module_electronic_test_fully_encapsulated_flags

            }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
                   
        save_flags_to_file(all_checklists_flags, details,"data/output.csv",username,usergroup,comment)
        find_unfinished_modules()


        subject = "MAC Production Status Change Notification: Bonding"
        message = f"""Dear Bonding and OGP Teams,

            Please be informed that the status of the step: Bonding has changed.

            Status: {Bonding_Icon}
            Changed by: {username}
            Module Number: {module_number}
            Sensor ID: {sensor_id}
            Hexboard Number: {hexboard_number}
            Baseplate Number: {baseplate_number}
            Remeasurement Number: {remeasurement_number}
            Comment: {comment}

            Best regards,  
            IHEP MAC Checklist Website"""

        send_email_notification(
            group_name="Bonding",
            subject=subject,
            message=message,
            sender_email="hgcalcn@cern.ch",
            sender_password="dummyPW"
        )
        send_email_notification(
            group_name="OGP",
            subject=subject,
            message=message,
            sender_email="hgcalcn@cern.ch",
            sender_password="dummyPW"
        )

######################################################################################################################################

def OGP_After_Backside_Bonding(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment, last_user):
    show_navigation_buttons()
    previous_step_completed = all(flag == 'green' for flag in bonding_flags.values())
    previous_step_flag = 'green' if previous_step_completed else 'red'

    if previous_step_flag == 'red':
        st.write("Please finish the previous step first")
    
    if (read_user_group(username) in ['OGP', 'All']) and previous_step_flag == 'green':
        status_options = {'\u2705 Green': 'green', '\u26A0\uFE0F Yellow': 'yellow', '\u274C Red': 'red'}

        for step, flag in ogp_after_backside_bonding_flags.items():
            selected_label = st.radio(f"{step} Flag:", list(status_options.keys()), 
                                      index=list(status_options.values()).index(flag), 
                                      key=f'{step}_radio', 
                                      help=f'Click count: {click_counts_ogp_after_backside_bonding[step]}')
            ogp_after_backside_bonding_flags[step] = status_options[selected_label]
            click_counts_ogp_after_backside_bonding[step] += 1

        table_data = [[step, '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C', last_user] 
                      for step, flag in ogp_after_backside_bonding_flags.items()]
        df_steps = pd.DataFrame(table_data, columns=["Step", "Status", "Status Changed by"])

        st.write("### OGP After Bonding Steps Overview")
        st.table(df_steps)

    ogp_after_backside_bonding_completed = all(flag == 'green' for flag in ogp_after_backside_bonding_flags.values())
    Ogp_After_Backside_Bonding_Flag = 'green' if ogp_after_backside_bonding_completed else 'red'
    Ogp_After_Backside_Bonding_Icon = '\u2705' if Ogp_After_Backside_Bonding_Flag == 'green' else '\u274C'
    st.header(f"OGP After Bonding Check List: {Ogp_After_Backside_Bonding_Icon}")

    if st.button("Save Flags to File"):
        all_checklists_flags = {
            "OGP Before Assembly": ogp_before_assembly_flags,
            "Hexaboard Electronic Test - Untaped": hexaboard_electronic_test_untaped_flags,
            "Apply Double-sided Tap Beneath Hexaboard": apply_double_sided_tap_beneath_hexaboard_flags,
            "Hexaboard Electronic Test - Taped": hexaboard_electronic_test_taped_flags,
            "Assemble Sensor": assemble_sensor_flags,
            "OGP After Assemble Sensor": ogp_after_assemble_sensor_flags,
            "Assemble Hexaboard": assemble_hexaboard_flags,
            "OGP After Assemble Hexaboard": ogp_after_assemble_hexaboard_flags,
            "Live Module Electronic Test - Assembled": live_module_electronic_test_assembled_flags,
            "Bonding": bonding_flags,
            "OGP After Bonding": ogp_after_backside_bonding_flags,
            "Live Module Electronic Test - Fully Bonded": live_module_electronic_test_fully_bonded_flags,
            "Encapsolation": module_encapsolation_flags,
            "OGP After Encapsolation": ogp_after_module_encapsolation_flags,
            "Live Module Electronic Test - Fully Encapsulated": live_module_electronic_test_fully_encapsulated_flags

            }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
                   
        save_flags_to_file(all_checklists_flags, details,"data/output.csv",username,usergroup,comment)
        find_unfinished_modules()

        subject = "MAC Production Status Change Notification: OGP After Bonding"
        message = f"""Dear OGP and Electrical Test Teams,

            Please be informed that the status of the step: OGP After Bonding has changed.

            Status: {Ogp_After_Backside_Bonding_Icon}
            Changed by: {username}
            Module Number: {module_number}
            Sensor ID: {sensor_id}
            Hexboard Number: {hexboard_number}
            Baseplate Number: {baseplate_number}
            Remeasurement Number: {remeasurement_number}
            Comment: {comment}

            Best regards,  
            IHEP MAC Checklist Website"""

        send_email_notification(
            group_name="OGP",
            subject=subject,
            message=message,
            sender_email="hgcalcn@cern.ch",
            sender_password="dummyPW"
        )

        send_email_notification(
            group_name="Electrical",
            subject=subject,
            message=message,
            sender_email="hgcalcn@cern.ch",
            sender_password="dummyPW"
        )

######################################################################################################################################
def Live_Module_Electronic_Test_Fully_Bonded(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment, last_user):
    show_navigation_buttons()
    previous_step_completed = all(flag == 'green' for flag in ogp_after_backside_bonding_flags.values())
    previous_step_flag = 'green' if previous_step_completed else 'red'

    if previous_step_flag == 'red':
        st.write("Please finish the previous step first")

    if (read_user_group(username) in ['Electrical', 'All']) and previous_step_flag == 'green':
        status_options = {'\u2705 Green': 'green', '\u26A0\uFE0F Yellow': 'yellow', '\u274C Red': 'red'}

        for step, flag in live_module_electronic_test_fully_bonded_flags.items():
            selected_label = st.radio(f"{step} Flag:", list(status_options.keys()), 
                                      index=list(status_options.values()).index(flag), 
                                      key=f'{step}_radio', 
                                      help=f'Click count: {click_counts_live_module_electronic_test_fully_bonded[step]}')
            live_module_electronic_test_fully_bonded_flags[step] = status_options[selected_label]
            click_counts_live_module_electronic_test_fully_bonded[step] += 1

        table_data = [[step, '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C', last_user] 
                      for step, flag in live_module_electronic_test_fully_bonded_flags.items()]
        df_steps = pd.DataFrame(table_data, columns=["Step", "Status", "Status Changed by"])

        st.write("### Live Module Electronic Test - Fully Bonded Steps Overview")
        st.table(df_steps)

    live_module_electronic_test_fully_bonded_completed = all(flag == 'green' for flag in live_module_electronic_test_fully_bonded_flags.values())
    Live_Module_Electronic_Test_Fully_Bonded_Flag = 'green' if live_module_electronic_test_fully_bonded_completed else 'red'
    Live_Module_Electronic_Test_Fully_Bonded_Icon = '\u2705' if Live_Module_Electronic_Test_Fully_Bonded_Flag == 'green' else '\u274C'
    st.header(f"Live Module Electronic Test - Fully Bonded Check List: {Live_Module_Electronic_Test_Fully_Bonded_Icon}")

    if st.button("Save Flags to File"):
        all_checklists_flags = {
            "OGP Before Assembly": ogp_before_assembly_flags,
            "Hexaboard Electronic Test - Untaped": hexaboard_electronic_test_untaped_flags,
            "Apply Double-sided Tap Beneath Hexaboard": apply_double_sided_tap_beneath_hexaboard_flags,
            "Hexaboard Electronic Test - Taped": hexaboard_electronic_test_taped_flags,
            "Assemble Sensor": assemble_sensor_flags,
            "OGP After Assemble Sensor": ogp_after_assemble_sensor_flags,
            "Assemble Hexaboard": assemble_hexaboard_flags,
            "OGP After Assemble Hexaboard": ogp_after_assemble_hexaboard_flags,
            "Live Module Electronic Test - Assembled": live_module_electronic_test_assembled_flags,
            "Bonding": bonding_flags,
            "OGP After Bonding": ogp_after_backside_bonding_flags,
            "Live Module Electronic Test - Fully Bonded": live_module_electronic_test_fully_bonded_flags,
            "Encapsolation": module_encapsolation_flags,
            "OGP After Encapsolation": ogp_after_module_encapsolation_flags,
            "Live Module Electronic Test - Fully Encapsulated": live_module_electronic_test_fully_encapsulated_flags

            }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
                   
        save_flags_to_file(all_checklists_flags, details,"data/output.csv",username,usergroup,comment)
        find_unfinished_modules()

        subject = "MAC Production Status Change Notification: Live Module Electronic Test - Fully Bonded"
        message = f"""Dear Electrical Test and Encapsolation Teams,

            Please be informed that the status of the step: Live Module Electronic Test - Fully Bonded has changed.

            Status: {Live_Module_Electronic_Test_Fully_Bonded_Icon}
            Changed by: {username}
            Module Number: {module_number}
            Sensor ID: {sensor_id}
            Hexboard Number: {hexboard_number}
            Baseplate Number: {baseplate_number}
            Remeasurement Number: {remeasurement_number}
            Comment: {comment}

            Best regards,  
            IHEP MAC Checklist Website"""

        send_email_notification(
            group_name="Electrical",
            subject=subject,
            message=message,
            sender_email="hgcalcn@cern.ch",
            sender_password="dummyPW"
        )

        send_email_notification(
            group_name="Encapsolation",
            subject=subject,
            message=message,
            sender_email="hgcalcn@cern.ch",
            sender_password="dummyPW"
        )
        

######################################################################################################################################
def Module_Encapsolation(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment, last_user):
    show_navigation_buttons()
    previous_step_completed = all(flag == 'green' for flag in live_module_electronic_test_fully_bonded_flags.values())
    previous_step_flag = 'green' if previous_step_completed else 'red'

    if previous_step_flag == 'red':
        st.write("Please finish the previous step first")

    if (read_user_group(username) in ['Encapsolation', 'All']) and previous_step_flag == 'green':
        status_options = {'\u2705 Green': 'green', '\u26A0\uFE0F Yellow': 'yellow', '\u274C Red': 'red'}

        for step, flag in module_encapsolation_flags.items():
            selected_label = st.radio(f"{step} Flag:", list(status_options.keys()), 
                                      index=list(status_options.values()).index(flag), 
                                      key=f'{step}_radio', 
                                      help=f'Click count: {click_counts_module_encapsolation[step]}')
            module_encapsolation_flags[step] = status_options[selected_label]
            click_counts_module_encapsolation[step] += 1

        table_data = [[step, '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C', last_user] 
                      for step, flag in module_encapsolation_flags.items()]
        df_steps = pd.DataFrame(table_data, columns=["Step", "Status", "Status Changed by"])

        st.write("### Encapsolation Steps Overview")
        st.table(df_steps)

    module_encapsolation_completed = all(flag == 'green' for flag in module_encapsolation_flags.values())
    Encapsolation_Flag = 'green' if module_encapsolation_completed else 'red'
    Encapsolation_Icon = '\u2705' if Encapsolation_Flag == 'green' else '\u274C'
    st.header(f"Encapsolation Check List: {Encapsolation_Icon}")

    if st.button("Save Flags to File"):
        all_checklists_flags = {
            "OGP Before Assembly": ogp_before_assembly_flags,
            "Hexaboard Electronic Test - Untaped": hexaboard_electronic_test_untaped_flags,
            "Apply Double-sided Tap Beneath Hexaboard": apply_double_sided_tap_beneath_hexaboard_flags,
            "Hexaboard Electronic Test - Taped": hexaboard_electronic_test_taped_flags,
            "Assemble Sensor": assemble_sensor_flags,
            "OGP After Assemble Sensor": ogp_after_assemble_sensor_flags,
            "Assemble Hexaboard": assemble_hexaboard_flags,
            "OGP After Assemble Hexaboard": ogp_after_assemble_hexaboard_flags,
            "Live Module Electronic Test - Assembled": live_module_electronic_test_assembled_flags,
            "Bonding": bonding_flags,
            "OGP After Bonding": ogp_after_backside_bonding_flags,
            "Live Module Electronic Test - Fully Bonded": live_module_electronic_test_fully_bonded_flags,
            "Encapsolation": module_encapsolation_flags,
            "OGP After Encapsolation": ogp_after_module_encapsolation_flags,
            "Live Module Electronic Test - Fully Encapsulated": live_module_electronic_test_fully_encapsulated_flags

            }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
                   
        save_flags_to_file(all_checklists_flags, details,"data/output.csv",username,usergroup,comment)
        find_unfinished_modules()

        subject = "MAC Production Status Change Notification: Encapsolation"
        message = f"""Dear Encapsolation and OGP Teams,

            Please be informed that the status of the step: Encapsolation has changed.

            Status: {Encapsolation_Icon}
            Changed by: {username}
            Module Number: {module_number}
            Sensor ID: {sensor_id}
            Hexboard Number: {hexboard_number}
            Baseplate Number: {baseplate_number}
            Remeasurement Number: {remeasurement_number}
            Comment: {comment}

            Best regards,  
            IHEP MAC Checklist Website"""

        send_email_notification(
            group_name="Encapsolation",
            subject=subject,
            message=message,
            sender_email="hgcalcn@cern.ch",
            sender_password="dummyPW"
        )

        send_email_notification(
            group_name="OGP",
            subject=subject,
            message=message,
            sender_email="hgcalcn@cern.ch",
            sender_password="dummyPW"
        )

######################################################################################################################################
def OGP_After_Module_Encapsolation(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment, last_user):
    show_navigation_buttons()
    previous_step_completed = all(flag == 'green' for flag in module_encapsolation_flags.values())
    previous_step_flag = 'green' if previous_step_completed else 'red'

    if previous_step_flag == 'red':
        st.write("Please finish the previous step first")

    if (read_user_group(username) in ['OGP', 'All']) and previous_step_flag == 'green':
        status_options = {'\u2705 Green': 'green', '\u26A0\uFE0F Yellow': 'yellow', '\u274C Red': 'red'}

        for step, flag in ogp_after_module_encapsolation_flags.items():
            selected_label = st.radio(f"{step} Flag:", list(status_options.keys()), 
                                      index=list(status_options.values()).index(flag), 
                                      key=f'{step}_radio', 
                                      help=f'Click count: {click_counts_ogp_after_module_encapsolation[step]}')
            ogp_after_module_encapsolation_flags[step] = status_options[selected_label]
            click_counts_ogp_after_module_encapsolation[step] += 1

        table_data = [[step, '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C', last_user] 
                      for step, flag in ogp_after_module_encapsolation_flags.items()]
        df_steps = pd.DataFrame(table_data, columns=["Step", "Status", "Status Changed by"])

        st.write("### OGP After Encapsolation Steps Overview")
        st.table(df_steps)

    ogp_after_module_encapsolation_completed = all(flag == 'green' for flag in ogp_after_module_encapsolation_flags.values())
    OGP_After_Encapsolation_Flag = 'green' if ogp_after_module_encapsolation_completed else 'red'
    OGP_After_Encapsolation_Icon = '\u2705' if OGP_After_Encapsolation_Flag == 'green' else '\u274C'
    st.header(f"OGP After Encapsolation Check List: {OGP_After_Encapsolation_Icon}")

    if st.button("Save Flags to File"):
        all_checklists_flags = {
            "OGP Before Assembly": ogp_before_assembly_flags,
            "Hexaboard Electronic Test - Untaped": hexaboard_electronic_test_untaped_flags,
            "Apply Double-sided Tap Beneath Hexaboard": apply_double_sided_tap_beneath_hexaboard_flags,
            "Hexaboard Electronic Test - Taped": hexaboard_electronic_test_taped_flags,
            "Assemble Sensor": assemble_sensor_flags,
            "OGP After Assemble Sensor": ogp_after_assemble_sensor_flags,
            "Assemble Hexaboard": assemble_hexaboard_flags,
            "OGP After Assemble Hexaboard": ogp_after_assemble_hexaboard_flags,
            "Live Module Electronic Test - Assembled": live_module_electronic_test_assembled_flags,
            "Bonding": bonding_flags,
            "OGP After Bonding": ogp_after_backside_bonding_flags,
            "Live Module Electronic Test - Fully Bonded": live_module_electronic_test_fully_bonded_flags,
            "Encapsolation": module_encapsolation_flags,
            "OGP After Encapsolation": ogp_after_module_encapsolation_flags,
            "Live Module Electronic Test - Fully Encapsulated": live_module_electronic_test_fully_encapsulated_flags

            }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
                   
        save_flags_to_file(all_checklists_flags, details,"data/output.csv",username,usergroup,comment)
        find_unfinished_modules()

        subject = "MAC Production Status Change Notification: OGP After Encapsolation"
        message = f"""Dear OGP and Electrical Test Teams,

            Please be informed that the status of the step: OGP After Encapsolation has changed.

            Status: {OGP_After_Encapsolation_Icon}
            Changed by: {username}
            Module Number: {module_number}
            Sensor ID: {sensor_id}
            Hexboard Number: {hexboard_number}
            Baseplate Number: {baseplate_number}
            Remeasurement Number: {remeasurement_number}
            Comment: {comment}

            Best regards,  
            IHEP MAC Checklist Website"""

        send_email_notification(
            group_name="OGP",
            subject=subject,
            message=message,
            sender_email="hgcalcn@cern.ch",
            sender_password="dummyPW"
        )

        send_email_notification(
            group_name="Electrical",
            subject=subject,
            message=message,
            sender_email="hgcalcn@cern.ch",
            sender_password="dummyPW"
        )

######################################################################################################################################
def Live_Module_Electronic_Test_Fully_Encapsulated(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment, last_user):
    col1, col2 = st.columns(2)    
    with col1:
        if st.button("\u2B05\uFE0FPrevious Step", key="prev_step") and st.session_state.step_index > 0:
            navigate(-1)
    previous_step_completed = all(flag == 'green' for flag in ogp_after_module_encapsolation_flags.values())
    previous_step_flag = 'green' if previous_step_completed else 'red'

    if previous_step_flag == 'red':
        st.write("Please finish the previous step first")

    if (read_user_group(username) in ['Electrical', 'All']) and previous_step_flag == 'green':
        status_options = {'\u2705 Green': 'green', '\u26A0\uFE0F Yellow': 'yellow', '\u274C Red': 'red'}

        for step, flag in live_module_electronic_test_fully_encapsulated_flags.items():
            selected_label = st.radio(f"{step} Flag:", list(status_options.keys()), 
                                      index=list(status_options.values()).index(flag), 
                                      key=f'{step}_radio', 
                                      help=f'Click count: {click_counts_live_module_electronic_test_fully_encapsulated[step]}')
            live_module_electronic_test_fully_encapsulated_flags[step] = status_options[selected_label]
            click_counts_live_module_electronic_test_fully_encapsulated[step] += 1

        table_data = [[step, '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C', last_user] 
                      for step, flag in live_module_electronic_test_fully_encapsulated_flags.items()]
        df_steps = pd.DataFrame(table_data, columns=["Step", "Status", "Status Changed by"])

        st.write("### Live Module Electronic Test - Fully Encapsulated Steps Overview")
        st.table(df_steps)

    live_module_electronic_test_fully_encapsulated_completed = all(flag == 'green' for flag in live_module_electronic_test_fully_encapsulated_flags.values())
    Live_Module_Electronic_Test_Fully_Encapsulated_Flag = 'green' if live_module_electronic_test_fully_encapsulated_completed else 'red'
    Live_Module_Electronic_Test_Fully_Encapsulated_Icon = '\u2705' if Live_Module_Electronic_Test_Fully_Encapsulated_Flag == 'green' else '\u274C'
    st.header(f"Live Module Electronic Test - Fully Encapsulated Check List: {Live_Module_Electronic_Test_Fully_Encapsulated_Icon}")

    if st.button("Save Flags to File"):
        all_checklists_flags = {
            "OGP Before Assembly": ogp_before_assembly_flags,
            "Hexaboard Electronic Test - Untaped": hexaboard_electronic_test_untaped_flags,
            "Apply Double-sided Tap Beneath Hexaboard": apply_double_sided_tap_beneath_hexaboard_flags,
            "Hexaboard Electronic Test - Taped": hexaboard_electronic_test_taped_flags,
            "Assemble Sensor": assemble_sensor_flags,
            "OGP After Assemble Sensor": ogp_after_assemble_sensor_flags,
            "Assemble Hexaboard": assemble_hexaboard_flags,
            "OGP After Assemble Hexaboard": ogp_after_assemble_hexaboard_flags,
            "Live Module Electronic Test - Assembled": live_module_electronic_test_assembled_flags,
            "Bonding": bonding_flags,
            "OGP After Bonding": ogp_after_backside_bonding_flags,
            "Live Module Electronic Test - Fully Bonded": live_module_electronic_test_fully_bonded_flags,
            "Encapsolation": module_encapsolation_flags,
            "OGP After Encapsolation": ogp_after_module_encapsolation_flags,
            "Live Module Electronic Test - Fully Encapsulated": live_module_electronic_test_fully_encapsulated_flags

            }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
                   
        save_flags_to_file(all_checklists_flags, details,"data/output.csv",username,usergroup,comment)
        find_unfinished_modules()

        subject = "MAC Production Status Change Notification: Live Module Electronic Test - Fully Encapsulated"
        message = f"""Dear Electrical Test Team,

            Please be informed that the status of the step: Live Module Electronic Test - Fully Encapsulated has changed.

            Status: {Live_Module_Electronic_Test_Fully_Encapsulated_Icon}
            Changed by: {username}
            Module Number: {module_number}
            Sensor ID: {sensor_id}
            Hexboard Number: {hexboard_number}
            Baseplate Number: {baseplate_number}
            Remeasurement Number: {remeasurement_number}
            Comment: {comment}

            Best regards,  
            IHEP MAC Checklist Website"""

        send_email_notification(
            group_name="Electrical",
            subject=subject,
            message=message,
            sender_email="hgcalcn@cern.ch",
            sender_password="dummyPW"
        )

######################################################################################################################################


def find_unfinished_modules():
    # Read the data/output.csv file
    outputfile_path = "data/output.csv"
    if not os.path.exists(outputfile_path):
        print(f"File '{outputfile_path}' not found. Creating an empty CSV.")
        columns = ["Username", "UserGroup", "DateAndTime", "Module Number", 
               "Sensor ID", "Hexboard Number", "Baseplate Number", 
               "Remeasurement Number", "Checklist Name", "Step", "Flag", "Comment"]
        pd.DataFrame(columns=columns).to_csv(outputfile_path, index=False)
    
    df = pd.read_csv(outputfile_path)

    # Group by the specified criteria and check for unfinished modules
    grouped = df.groupby(['Module Number', 'Sensor ID', 'Hexboard Number', 'Baseplate Number', 'Remeasurement Number'])
    unfinished_modules = []

    for group_name, group_data in grouped:
        # Check if any step in the module has a flag 'red'
        if 'red' in group_data['Flag'].values:
            unfinished_modules.append(group_data)

    # Concatenate the unfinished modules into a single DataFrame
    if unfinished_modules:  # Check if the list is not empty
        unfinished_df = pd.concat(unfinished_modules, ignore_index=True)
    else:
        unfinished_df = pd.DataFrame() 

    # Save the unfinished modules to a new CSV file
    unfinished_df.to_csv("data/unfinished_module.csv", index=False)

############################################################################################################################
def show_unfinished_modules(username):
    try:
        unfinished_df = pd.read_csv("data/output.csv")
        if unfinished_df.empty:
            st.header("Congratulations, no unfinished module found.")
        else:
            # Filter the unfinished modules with red flags
            unfinished_red_flags = unfinished_df[unfinished_df['Flag'].isin(['red', 'yellow'])]

            # Group by the criteria and get the first step with red flag for each unfinished module
            grouped_unfinished = unfinished_red_flags.groupby(['Module Number', 'Sensor ID', 'Hexboard Number', 'Baseplate Number', 'Remeasurement Number'])
            module_info = []
            usergroup=read_user_group(username)
            for group_name, group_data in grouped_unfinished:
                # Find the first step with a red flag for each module
                red_flag_data = group_data[group_data['Flag'].isin(['red', 'yellow'])]
                first_red_flag_step = red_flag_data.iloc[0]['Step'] if not red_flag_data.empty else None
                comment = group_data.iloc[0]['Comment'] if not group_data.empty else None
                # Extract relevant information for display
                module_info.append({
                    'Module Number': group_name[0],
                    'Sensor ID': group_name[1],
                    'Hexboard Number': group_name[2],
                    'Baseplate Number': group_name[3],
                    'Next Step': first_red_flag_step,
                    'Remeasurement Number': group_name[4],
                    'Comment':comment
                })

            if module_info:
                unfinished_table = pd.DataFrame(module_info)
                unfinished_table.index = range(1, len(unfinished_table) + 1)
                st.write(unfinished_table)
                st.warning("\u26A0\uFE0F Please finish those modules in the Module Assembly Check List.")
            else:
                st.info("No unfinished modules with red flags found.")
         
    except pd.errors.EmptyDataError:
        st.header("Congratulations, no unfinished module found.")
    except FileNotFoundError:
        st.error("unfinished_module.csv was not found. Please check the file path.")            



###################################################################################################################################################################

def show_inventory(assemb_date: str):
    st.header("Live inventory")
    info=asyncio.run(inventory_tracker(assemb_date))
    baseplate_stat = asyncio.run(baseplate_stats())
    hxb_stat = asyncio.run(hxb_stats())
    df = pd.DataFrame(info)
    df.index=range(1, len(info) + 1)
    st.write(df)
    with st.expander("Baseplate Usage Summary"):
        st.metric("CuW Used", f"{baseplate_stat['CuW used']} / {baseplate_stat['CuW total']}")
        st.metric("Ti Used", f"{baseplate_stat['Ti used']} / {baseplate_stat['Ti total']}")
    with st.expander("Hexaboard Usage Summary"):
        st.metric("V3B Used", f"{hxb_stat['v3b used']} / {hxb_stat['v3b total']}")
        st.metric("V3C Used", f"{hxb_stat['v3c used']} / {hxb_stat['v3c total']}")
def list_all_module():
    info=asyncio.run(list_complete_module())
    df=pd.DataFrame(info)
    df.index+=1
    st.write("Table of assembled modules")
    st.write(df)
def list_completed_modules():
    st.header("Completed modules")
    info=asyncio.run(status_complete())
    df=pd.DataFrame(info)
    df.index+=1
    st.write("Table of finished modules")
    st.write(df)
def list_new_assemble_modules():
    info=asyncio.run(status_no_wb())
    df=pd.DataFrame(info)
    df.index+=1
    st.write("Table of modules at stage: not yet wirebonded")
    st.write(df)
def list_wb_back_modules():
    info=asyncio.run(status_wb_back())
    df=pd.DataFrame(info)
    df.index+=1
    st.write("Table of modules at stage: wb back")
    st.write(df)

def list_wb_front_modules():
    info=asyncio.run(status_wb_front())
    df=pd.DataFrame(info)
    df.index+=1
    st.write("Table of modules at stage: wb front")
    st.write(df)

def list_encap_back_modules():
    info=asyncio.run(status_encap_back())
    df=pd.DataFrame(info)
    df.index+=1
    st.write("Table of modules at stage: encap back")
    st.write(df)

def list_protomodules():
    info=asyncio.run(status_proto())
    df=pd.DataFrame(info)
    df.index+=1
    st.write("Table of modules at stage: protomodule")
    st.write(df)


def load_packaged_modules():
    """Load packaged modules from CSV if exists, otherwise return an empty set."""
    if os.path.exists(PACKAGED_CSV):
        try:
            df = pd.read_csv(PACKAGED_CSV)
            return set(df["Module Number"].tolist())
        except pd.errors.EmptyDataError:
            return set()
    return set()

def save_packaged_modules(packaged_modules):
    """Save packaged modules to CSV."""
    df = pd.DataFrame({"Module Number": list(packaged_modules)})
    df.to_csv(PACKAGED_CSV, index=False)

def show_finished_modules(username): 
    try:
        finished_df = pd.read_csv("data/output.csv")

        if finished_df.empty:
            st.header("No finished module found.")
            return


        # Load already packaged modules
        packaged_modules = load_packaged_modules()
        
        # Display packaged modules
        packaged_df = pd.DataFrame({"Module Number": list(packaged_modules)})
        packaged_df.index = range(1, len(packaged_df) + 1)
        if not packaged_df.empty:
            st.write("## Packaged Modules")
            st.write(packaged_df)
            st.success("Those modules are already packaged.")

        # Group by module-related fields and check if all steps have 'green' flags
        grouped = finished_df.groupby(['Module Number', 'Sensor ID', 'Hexboard Number', 'Baseplate Number', 'Remeasurement Number'])
        finished_modules = []

        for group_name, group_data in grouped:
            module_number = group_name[0]
            if module_number in packaged_modules:
                continue  # Skip already packaged modules
            
            if all(group_data['Flag'] == 'green'):  # Check if all steps have green flags
                comment = group_data.iloc[0]['Comment'] if not group_data.empty else None
                finished_modules.append({
                    'Module Number': module_number,
                    'Sensor ID': group_name[1],
                    'Hexboard Number': group_name[2],
                    'Baseplate Number': group_name[3],
                    'Remeasurement Number': group_name[4],
                    'Comment': comment
                })

        if not finished_modules:
            st.info("No finished modules found.")
            return

        # Convert to DataFrame
        finished_table = pd.DataFrame(finished_modules)#finished_modules)
        finished_table.index = range(1, len(finished_modules)+1)#len(finished_table) + 1)

        # Display finished modules
        st.write("## Finished Modules (Ready for Packaging)")
        st.write(finished_table)
        st.success("Those modules have all steps finished. Ready for packaging. Please switch to 'Packaging Modules' tab when there are more than 20 modules finished" )

    except pd.errors.EmptyDataError:
        st.header("No finished modules found.")
    except FileNotFoundError:
        st.error("output.csv was not found. Please check the file path.")

###################################################################################################################################################################
def packaging_modules(username):
    try:
        finished_df = pd.read_csv("data/output.csv")

        if finished_df.empty:
            st.header("No finished module found.")
            return


        # Load already packaged modules
        packaged_modules = load_packaged_modules()
        
        # Display packaged modules
        packaged_df = pd.DataFrame({"Module Number": list(packaged_modules)})
        packaged_df.index = range(1, len(packaged_df) + 1)
        if not packaged_df.empty:
            st.write("## Packaged Modules")
            st.write(packaged_df)
            st.success("Those modules are already packaged.")

        # Group by module-related fields and check if all steps have 'green' flags
        grouped = finished_df.groupby(['Module Number', 'Sensor ID', 'Hexboard Number', 'Baseplate Number', 'Remeasurement Number'])
        finished_modules = []

        for group_name, group_data in grouped:
            module_number = group_name[0]
            if module_number in packaged_modules:
                continue  # Skip already packaged modules
            
            if all(group_data['Flag'] == 'green'):  # Check if all steps have green flags
                comment = group_data.iloc[0]['Comment'] if not group_data.empty else None
                finished_modules.append({
                    'Module Number': module_number,
                    'Sensor ID': group_name[1],
                    'Hexboard Number': group_name[2],
                    'Baseplate Number': group_name[3],
                    'Remeasurement Number': group_name[4],
                    'Comment': comment
                })

        if not finished_modules:
            st.info("No finished modules found.")
            return

        # Convert to DataFrame
        finished_table = pd.DataFrame(finished_modules)
        finished_table.index = range(1, len(finished_table) + 1)

        # Display finished modules
        st.write("## Finished Modules (Ready for Packaging)")
        st.write(finished_table)
        st.info("Those modules have all steps finished. When there are more than 20 finished modules, please click the button below to notify the packaging team")


        subject = "MAC Production Status Change Notification: 20 modules are ready for packaging"
        message = f"""Dear Packaging Teams,

            Please be informed that there are 20 modules ready for packaging. Please proceed on the website system.

            Best regards,  
            IHEP MAC Checklist Website"""


        if len(finished_modules) >= 20:
            if st.button("Notify Packaging Team"):
                send_email_notification(
                    group_name="Packaging",
                    subject=subject,
                    message=message,
                    sender_email="hgcalcn@cern.ch",
                    sender_password="dummyPW"
                )
            #Checkbox selection
            selected_modules = st.multiselect("Select modules for packaging:", finished_table["Module Number"].tolist())

            # Packaging button
            if st.button("Packaging"):
                if selected_modules:
                    packaged_modules.update(selected_modules)  # Add new selections
                    save_packaged_modules(packaged_modules)
                    st.success(f"Packaged {len(selected_modules)} modules successfully!")



    except pd.errors.EmptyDataError:
        st.header("No finished modules found.")
    except FileNotFoundError:
        st.error("output.csv was not found. Please check the file path.")

###################################################################################################################################################################

def plot_selected_module():
    module_number = st.text_input("Enter Module Number")
    sensor_id = st.text_input("Enter Sensor ID")
    hexboard_number = st.text_input("Enter Hexboard Number")
    baseplate_number = st.text_input("Enter Baseplate Number")
    remeasurement_number=st.text_input("Enter Remeasurement Number(0 for the first measurement)")
    if st.checkbox("Submit"):
        if module_number and sensor_id and hexboard_number and baseplate_number and remeasurement_number:
    # Read the data/output.csv file
            df = pd.read_csv("data/output.csv", dtype={'Module Number': str, 'Sensor ID': str, 'Hexboard Number': str, 'Baseplate Number': str, 'Remeasurement Number':str})

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
    # Read the data/output.csv file
    outputfile_path = "data/output.csv"
    if not os.path.exists(outputfile_path) or os.stat(outputfile_path).st_size == 0:
        st.error(f"File '{outputfile_path}' is missing or empty. No data available.")
        st.stop()  # Stop execution
    # Date selection for filtering
    df = pd.read_csv(outputfile_path)
    if df.empty:
        st.warning("The data file is empty. No data available to display.")
        st.stop()

    # Convert 'DateAndTime' to datetime
    df["DateAndTime"] = pd.to_datetime(df["DateAndTime"])

    min_date = df["DateAndTime"].min()
    max_date = df["DateAndTime"].max()
    start_date = st.date_input("Select Start Date", min_value=min_date, max_value=max_date, value=min_date)
    end_date = st.date_input("Select End Date", min_value=min_date, max_value=max_date, value=max_date)
    # Convert selected dates to datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    if start_date:
        df = df[df["DateAndTime"] >= start_date]
    if end_date:
        end_date = end_date.replace(hour=23, minute=59, second=59) # extend to the end of the day
        df = df[df["DateAndTime"] <= end_date]
    if df.shape[0] < 1:
        print("Not enough data points to generate a plot.")
        return "<p>Not enough data to generate a plot. Please select a larger date range or wait for more data collection.</p>"


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
    # Adjust padding to prevent overlap
    plt.subplots_adjust(bottom=0.3) 

    # Convert plot to HTML image tag
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)




    image_tag = f'<img src="data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}" />'
    plt.close()

    return image_tag

#############################################################################################################################################################
def plot_steps():
    # Read the data/output.csv file
    outputfile_path = "data/output.csv"

    if not os.path.exists(outputfile_path) or os.stat(outputfile_path).st_size == 0:
        st.error(f"File '{outputfile_path}' is missing or empty. No data available.")
        st.stop()  # Stop execution
    
    # Date selection for filtering
    df = pd.read_csv(outputfile_path)
    if df.empty:
        st.warning("The data file is empty. No data available to display.")
        st.stop()


    # Convert 'DateAndTime' to datetime
    df["DateAndTime"] = pd.to_datetime(df["DateAndTime"])

     # Get unique steps for selection
    unique_steps = df["Step"].unique()
    
    # Step selection
    selected_step = st.selectbox("Select a Step:", unique_steps)

    # Filter data for the selected step and only 'green' flagged rows
    filtered_df = df[(df["Step"] == selected_step) & (df["Flag"] == "green")]

    mode = st.radio("Select mode:", ["Accumulated numbers", "Numbers per day"])

    # Count finished modules per day
    finished_per_day = filtered_df.groupby(filtered_df["DateAndTime"].dt.date).size()

    if mode == "Accumulated numbers":
        finished_per_day = finished_per_day.cumsum()  # Convert to cumulative sum

    # Plot the number of finished modules over time
    plt.figure(figsize=(12, 6))
    plt.bar(finished_per_day.index, finished_per_day.values, color="lightgreen")
    plt.title(f"Number of Finished Modules Over Time ({selected_step}) - {mode}")
    plt.xlabel("Date")
    plt.ylabel("Number of Finished Modules")
    plt.xticks(rotation=45)
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    # Convert plot to an image for embedding
    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)
    image_tag = f'<img src="data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}" />'
    plt.close()

    return image_tag    
########################################################################################

def plot_summary(selected_date): #,module_names_array,v_info,i_info,adc_stdd,adc_mean):
    plot1,plot2,plot3=asyncio.run(plot_workflow(selected_date))
    return plot1,plot2,plot3               

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
    st.title("CMS HGCal IHEP/TTU MAC: Module Assembly and Status Bookkeeping System")
    st.image("IHEP_MAC_Bookkeeping/ReeseLabs_hexagon.jpg", use_container_width=True)

    # Add content for the home page
##############################################################################################################################################
def main():
    st.set_page_config(layout="wide", page_title="HGCAL IHEP/TTU MAC", page_icon="IHEP_MAC_Bookkeeping/hex_ver_1.png")




    show_image = True
    logged_in = False

    #username = None  # Initialize the username variable
    #password_input = None  # Initialize the password variable


    # Session state to track login status
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = None  # Store username persistently


    if not st.session_state.authenticated:
        username = st.sidebar.text_input("Username", key="username_input")  # Unique key for username input
        password_input = st.sidebar.text_input("Password", type="password", key="password_input")  # Unique key for password input
        login_button = st.sidebar.button("Login", key="login_button")  # Unique key for login button

        if login_button:
            if authenticate_user(username, password_input):
                st.session_state.authenticated = True  # Mark as logged in
                st.session_state.username = username  # Store username
                st.sidebar.success("Login successful!")
                logged_in = True
                show_image = False


            else:
                st.sidebar.error("Invalid username or password")

    if st.session_state.authenticated:

    
        show_image = False
        username = st.session_state.username  # Retrieve username
        with st.sidebar:
            st.markdown("### ")

        # Top row: two logos side-by-side
            top1, top2 = st.columns(2)
            with top1:
                st.image("IHEP_MAC_Bookkeeping/CMS.png", width=200)
            with top2:
                st.image("IHEP_MAC_Bookkeeping/ttu.png", width=200)

        # Bottom row: centered third logo
            bottom_spacer1, bottom_center, bottom_spacer2 = st.columns([1, 2, 1])
            with bottom_center:
                st.image("IHEP_MAC_Bookkeeping/ihep.png", width=200)

            st.markdown("---")
            st.sidebar.write("### Select an Option")



            option = st.sidebar.selectbox("", ("Home", "Module Assembly Check List", "Unfinished Modules", "Finished Modules", "Packaging Modules", "Module Status Summary"), key="option_select")  # Unique key for option select
        
        if option == "Home":
            home_page()
        if option == "Module Assembly Check List":
            show_module_info_viewer()
            show_proto_info_viewer()
            Module_Assembly_Check_List(username)
        if option == "Unfinished Modules":
            show_unfinished_modules(username)
            list_protomodules()
            list_new_assemble_modules()
            list_wb_back_modules()
            list_encap_back_modules()
            list_wb_front_modules()
        if option == "Finished Modules":
            list_completed_modules()
        if option == "Packaging Modules":
            packaging_modules(username)    
        if option== "Module Status Summary":
            show_inventory('2025-03-04')
            list_all_module()
            plot_choice = st.sidebar.radio("Select Plot Type:", ["Modules Summary", "Steps Over Time","Electrical QC Summary"])
            if plot_choice == "Steps Over Time":
                plot = plot_steps() 
                st.markdown(plot, unsafe_allow_html=True)
            elif plot_choice == "Modules Summary":
                plot = plot_modules() 
                st.markdown(plot, unsafe_allow_html=True)
            elif plot_choice == "Electrical QC Summary":
                selected_date0 = st.date_input("Select modules assembled since: ", value=date(2025, 3, 4))
                selected_date = selected_date0.strftime('%Y-%m-%d')
                st.title("Electrical QC summary")
                if st.button("🔁 Regenerate plot with newest module info"):

                    
                    plot1,plot2,plot3 =plot_summary(selected_date)
                    #plot1 = plot_summary('/home/daq2-admin/HGCAL_WEB_IHEP/data/summary_since_'+selected_date+'.root',module_names_array,selected_date)
                    #plot2 = mean_summary('/home/daq2-admin/HGCAL_WEB_IHEP/data/summary_since_'+selected_date+'.root',module_names_array,selected_date)
                    #plot3 = std_summary('/home/daq2-admin/HGCAL_WEB_IHEP/data/summary_since_'+selected_date+'.root',module_names_array,selected_date)
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.pyplot(plot1)
                        st.caption("IV Summary")

                    with col2:
                        st.pyplot(plot3)
                        st.caption("Mean ADC Summary")

                    with col3:
                        st.pyplot(plot2)
                        st.caption("ADC noise Summary")
       # --- Password Change Section ---
        st.sidebar.write("---")

        st.sidebar.button("Logout", on_click=lambda: st.session_state.update(authenticated=False))  # Logout Button
        change_password_button = st.sidebar.checkbox("Change Password")

        if change_password_button:
            old_password = st.sidebar.text_input("Old Password", type="password")
            new_password = st.sidebar.text_input("New Password", type="password")
            confirm_password = st.sidebar.text_input("Confirm New Password", type="password")

            if st.sidebar.button("Confirm Password Change"):
                # Authenticate with the old password
                if authenticate_user(username, old_password):
                    if new_password == confirm_password:
                        update_password(username, new_password)
                        st.sidebar.success("Password changed successfully!")
                    else:
                        st.sidebar.error("New passwords do not match.")
                else:
                    st.sidebar.error("Incorrect old password.")


    if show_image:
        st.title("Welcome to the HGCal IHEP/TTU MAC Bookkeeping Site")

        st.image("IHEP_MAC_Bookkeeping/CMS_detector.jpeg", use_container_width=True)
        #st.write("Welcome to the CMS HGCal IHEP MAC Bookkeeping System")
        col1, col2, col3 = st.columns([3, 2, 1])  # Equal width for both columns
        with col1:
            st.image("IHEP_MAC_Bookkeeping/APDLABLOGO.jpg", width=150)
        with col2:
            st.image("IHEP_MAC_Bookkeeping/ihep.png",  width=300)
        with col3:
            st.image("IHEP_MAC_Bookkeeping/CMS.png",  width=150)

        show_weather = st.sidebar.checkbox("Tell me the weather!", value=False)
        if show_weather:
            refresh_weather = st.sidebar.button("🔄 Refresh Weather Data")
            weatherstation=whats_the_weather()
            st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            st.write(f"Loaded {len(weatherstation)} plots.")
            for i in weatherstation:
                st.pyplot(i)
            if refresh_weather:
                weatherstation=whats_the_weather()
                for i in weatherstation:
                    st.pyplot(i)

 
        if not login_button and not logged_in and not show_weather:
            st.error("Please log in")


if __name__ == "__main__":
    main()

