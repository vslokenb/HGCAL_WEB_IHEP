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

STEPS = [
    "Overview", "Apply double-sided tape", "1st Electrical test", "Gantry assembly",
    "OGP of gantry assembly", "Ready for bonding", "Bonding completed",
    "OGP of bonding", "Encapsulation", "Ready for the 2nd Electrical test", "2nd Electrical test"
]



# Function to handle navigation
def navigate(step_change):
    new_index = st.session_state.step_index + step_change
    if 0 <= new_index < len(STEPS):  # Ensure index is within bounds
        st.session_state.step_index = new_index
        st.rerun()

def show_navigation_buttons():
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⬅️ Previous Step", key="prev_step") and st.session_state.step_index > 0:
            navigate(-1)

    with col2:
        if st.button("➡️ Next Step", key="next_step") and st.session_state.step_index < len(STEPS) - 1:
            navigate(1)

Apply_double_sided_tape_flags = {
    'Apply double-sided tape': 'red',
}

First_electrical_test_flags = {
    '1st Electrical test': 'red',
}

Gantry_assembly_flags = {
    'Gantry assembly': 'red',
}

OGP_gantry_assembly_flags = {
    'OGP of gantry assembly': 'red',
}

Ready_for_bonding_flags = {
    'Ready for bonding': 'red',
}

Bonding_completed_flags = {
    'Bonding completed': 'red',
}

OGP_bonding_flags = {
    'OGP of bonding': 'red',
}

Encapsulation_flags = {
    'Encapsulation': 'red',
}

Ready_for_second_electrical_test_flags = {
    'Ready for the 2nd Electrical test': 'red',
}

Second_electrical_test_flags = {
    '2nd Electrical test': 'red',
}

click_counts_Apply_double_sided_tape = {step: 0 for step in Apply_double_sided_tape_flags}
click_counts_First_electrical_test = {step: 0 for step in First_electrical_test_flags}
click_counts_Gantry_assembly = {step: 0 for step in Gantry_assembly_flags}
click_counts_OGP_gantry_assembly = {step: 0 for step in OGP_gantry_assembly_flags}
click_counts_Ready_for_bonding = {step: 0 for step in Ready_for_bonding_flags}
click_counts_Bonding_completed = {step: 0 for step in Bonding_completed_flags}
click_counts_OGP_bonding = {step: 0 for step in OGP_bonding_flags}
click_counts_Encapsulation = {step: 0 for step in Encapsulation_flags}
click_counts_Ready_for_second_electrical_test = {step: 0 for step in Ready_for_second_electrical_test_flags}
click_counts_Second_electrical_test = {step: 0 for step in Second_electrical_test_flags}


###############################################################################################
def read_user_group(username):
    user_info = pd.read_csv("IHEP_MAC_Bookkeeping/user_info.csv")
    user_group = user_info.loc[user_info['username'] == username, 'group'].values
    return user_group[0] if len(user_group) > 0 else None
##################################################################################################

def authenticate_user(username, password):
    user_info = pd.read_csv("IHEP_MAC_Bookkeeping/user_info.csv")   
    user_info['password'] = user_info['password'].astype(str) 
    print(user_info['username'])
    print(user_info['password'])
    if ((user_info['username'] == username) & (user_info['password'] == password)).any():
        return True
    else:
        return False
#################################################################################################

def initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number,remeasurement_number):
    if os.path.exists("IHEP_MAC_Bookkeeping/output.csv"):
        existing_flags_df = pd.read_csv("IHEP_MAC_Bookkeeping/output.csv", dtype={'Module Number': str, 'Sensor ID': str, 'Hexboard Number': str, 'Baseplate Number': str, 'Remeasurement Number':str})

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
                for flags in [
    Apply_double_sided_tape_flags, First_electrical_test_flags, 
    Gantry_assembly_flags,OGP_gantry_assembly_flags,Ready_for_bonding_flags, Bonding_completed_flags,
    OGP_bonding_flags,Encapsulation_flags,Ready_for_second_electrical_test_flags,Second_electrical_test_flags]:
                    if step_ in flags:
                        flags[step_] = flag_
        else:
            # Set default values for all flags if not found in existing data
            for flags in [
    Apply_double_sided_tape_flags, First_electrical_test_flags, 
    Gantry_assembly_flags,OGP_gantry_assembly_flags,Ready_for_bonding_flags, Bonding_completed_flags,
    OGP_bonding_flags,Encapsulation_flags,Ready_for_second_electrical_test_flags,Second_electrical_test_flags]:
                for step_ in flags:
                    flags[step_] = 'red'
#################################################################################################

def Module_Assembly_Check_List(username):
    st.title("Welcome to the HGCal module assembly checklist")
    module_number = st.text_input("Enter Module Number")
    sensor_id = st.text_input("Enter Sensor ID")
    hexboard_number = st.text_input("Enter Hexboard Number")
    baseplate_number = st.text_input("Enter Baseplate Number")
    remeasurement_number=st.text_input("Enter Remeasurement Number(0 for the first measurement)")
    comment = st.text_input("Comment*(Optional)")
    usergroup=read_user_group(username)
        # Checkbox to submit the details
    if st.checkbox("Display status"):
        if module_number and sensor_id and hexboard_number and baseplate_number and remeasurement_number:
            #steps = [
            #"Overview", "Apply double-sided tape", "1st Electrical test", "Gantry assembly",
            #"OGP of gantry assembly", "Ready for bonding", "Bonding completed",
            #"OGP of bonding", "Encapsulation", "Ready for the 2nd Electrical test", "2nd Electrical test"]
            #if "step_index" not in st.session_state:
            #    st.session_state.step_index = 0
            option1 = st.selectbox("Select a step", STEPS, index=st.session_state.step_index, key="option1")
            st.session_state.step_index = STEPS.index(option1)
            #option1=st.selectbox("Select a step", ("Overview", "Apply double-sided tape", "1st Electrical test" , "Gantry assembly",   "OGP of gantry assembly", "Ready for bonding", "Bonding completed",  "OGP of bonding", "Encapsulation", "Ready for the 2nd Electrical test", "2nd Electrical test"),key="option1")
            if option1=='Overview':
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)


                apply_double_sided_tape_completed = all(flag == 'green' for flag in Apply_double_sided_tape_flags.values())
                Apply_Double_Sided_Tape_Flag = 'green' if apply_double_sided_tape_completed else 'red'
                Apply_double_sided_tape_Icon = '\u2705' if Apply_Double_Sided_Tape_Flag == 'green' else '\u274C'

                first_electrical_test_completed = all(flag == 'green' for flag in First_electrical_test_flags.values())
                First_Electrical_Test_Flag = 'green' if first_electrical_test_completed else 'red'
                First_Electrical_Test_Icon = '\u2705' if First_Electrical_Test_Flag == 'green' else '\u274C'

                gantry_assembly_completed = all(flag == 'green' for flag in Gantry_assembly_flags.values())
                Gantry_Assembly_Flag = 'green' if gantry_assembly_completed else 'red'
                Gantry_Assembly_Icon = '\u2705' if Gantry_Assembly_Flag == 'green' else '\u274C'

                ogp_gantry_assembly_completed = all(flag == 'green' for flag in OGP_gantry_assembly_flags.values())
                OGP_Gantry_Assembly_Flag = 'green' if ogp_gantry_assembly_completed else 'red'
                OGP_Gantry_Assembly_Icon = '\u2705' if OGP_Gantry_Assembly_Flag == 'green' else '\u274C'

                ready_for_bonding_completed = all(flag == 'green' for flag in Ready_for_bonding_flags.values())
                Ready_for_Bonding_Flag = 'green' if ready_for_bonding_completed else 'red'
                Ready_for_Bonding_Icon = '\u2705' if Ready_for_Bonding_Flag == 'green' else '\u274C'

                bonding_completed = all(flag == 'green' for flag in Bonding_completed_flags.values())
                Bonding_Completed_Flag = 'green' if bonding_completed else 'red'
                Bonding_Completed_Icon = '\u2705' if Bonding_Completed_Flag == 'green' else '\u274C'

                ogp_bonding_completed = all(flag == 'green' for flag in OGP_bonding_flags.values())
                OGP_Bonding_Flag = 'green' if ogp_bonding_completed else 'red'
                OGP_Bonding_Icon = '\u2705' if OGP_Bonding_Flag == 'green' else '\u274C'

                encapsulation_completed = all(flag == 'green' for flag in Encapsulation_flags.values())
                Encapsulation_Flag = 'green' if encapsulation_completed else 'red'
                Encapsulation_Icon = '\u2705' if Encapsulation_Flag == 'green' else '\u274C'

                ready_for_second_electrical_test_completed = all(flag == 'green' for flag in Ready_for_second_electrical_test_flags.values())
                Ready_for_Second_Electrical_Test_Flag = 'green' if ready_for_second_electrical_test_completed else 'red'
                Ready_for_Second_Electrical_Test_Icon = '\u2705' if Ready_for_Second_Electrical_Test_Flag == 'green' else '\u274C'

                second_electrical_test_completed = all(flag == 'green' for flag in Second_electrical_test_flags.values())
                Second_Electrical_Test_Flag = 'green' if second_electrical_test_completed else 'red'
                Second_Electrical_Test_Icon = '\u2705' if Second_Electrical_Test_Flag == 'green' else '\u274C'


                # Create a DataFrame for a cleaner display
                checklist_df = pd.DataFrame({
                    "Step": [                        
                        "Apply double-sided tape", 
                        "1st Electrical test", 
                        "Gantry assembly",   
                        "OGP of gantry assembly", 
                        "Ready for bonding", 
                        "Bonding completed",  
                        "OGP of bonding", 
                        "Encapsulation", 
                        "Ready for the 2nd Electrical test", 
                        "2nd Electrical test"

                    ],
                    "Status": [
                        Apply_double_sided_tape_Icon,
                        First_Electrical_Test_Icon,
                        Gantry_Assembly_Icon,
                        OGP_Gantry_Assembly_Icon,
                        Ready_for_Bonding_Icon,
                        Bonding_Completed_Icon,
                        OGP_Bonding_Icon,
                        Encapsulation_Icon,
                        Ready_for_Second_Electrical_Test_Icon,
                        Second_Electrical_Test_Icon,
                    ]
                })

                # Display as a table
                st.table(checklist_df)
                col1, col2 = st.columns(2)

                with col2:
                     if st.button("➡️ Next Step") and st.session_state.step_index < len(STEPS) - 1:
                        navigate(1)

            if option1 == "Apply double-sided tape":
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Apply_Double_Sided_Tape(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment)

            if option1 == "1st Electrical test":
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                First_Electrical_Test(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment)

            if option1 == "Gantry assembly":
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Gantry_Assembly(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment)

            if option1 == "OGP of gantry assembly":
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                OGP_Gantry_Assembly(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment)

            if option1 == "Ready for bonding":
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Ready_for_Bonding(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment)

            if option1 == "Bonding completed":
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Bonding_Completed(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment)

            if option1 == "OGP of bonding":
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                OGP_Bonding(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment)

            if option1 == "Encapsulation":
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Encapsulation(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment)

            if option1 == "Ready for the 2nd Electrical test":
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Ready_for_Second_Electrical_Test(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment)

            if option1 == "2nd Electrical test":
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Second_Electrical_Test(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment)
            



############################################################################################################################
def Apply_Double_Sided_Tape(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment):
    
    show_navigation_buttons()

    if(read_user_group(username) == 'OGP' or read_user_group(username) == 'All'):
        status_options = {
            '\u2705 Green': 'green',
            '\u26A0\uFE0F Yellow': 'yellow',
            '\u274C Red': 'red'
        }
        for step, flag in Apply_double_sided_tape_flags.items():
            selected_label = st.radio(
                f"{step} Flag:",
                list(status_options.keys()),  # Show all options as radio buttons
                index=list(status_options.values()).index(flag),
                key=f'{step}_radio',
                help=f'Click count: {click_counts_Apply_double_sided_tape[step]}'
            )

            # Update flag and click count based on selected option
            Apply_double_sided_tape_flags[step] = status_options[selected_label]
            click_counts_Apply_double_sided_tape[step] += 1

        table_data = [[step, '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C', username] for step, flag in Apply_double_sided_tape_flags.items()]
        df_steps = pd.DataFrame(table_data, columns=["Step", "Status", "User"])

        # Display step-wise table
        st.write("### Apply Double Sided Tape Overview")
        st.table(df_steps)

    # Determine overall checklist status
    apply_double_sided_tape_completed = all(flag == 'green' for flag in Apply_double_sided_tape_flags.values())
    Apply_Double_Sided_Tape_Flag = 'green' if apply_double_sided_tape_completed else 'red'
    Apply_double_sided_tape_Icon = '\u2705' if Apply_Double_Sided_Tape_Flag == 'green' else '\u274C'
    st.header(f" Apply Double Sided Tape Check List: {Apply_double_sided_tape_Icon}")

    if st.button("Save Flags to File"):
        all_checklists_flags = {
                'Apply double-sided tape':Apply_double_sided_tape_flags, 
                '1st Electrical test"':First_electrical_test_flags, 
                'Gantry assembly': Gantry_assembly_flags,
                'OGP of gantry assembly':OGP_gantry_assembly_flags,
                'Ready for bonding':Ready_for_bonding_flags, 
                'Bonding completed':Bonding_completed_flags,
                'OGP of bonding':OGP_bonding_flags,
                'Encapsulation':Encapsulation_flags,
                'Ready for the 2nd Electrical test':Ready_for_second_electrical_test_flags,
                '2nd Electrical test':Second_electrical_test_flags,

            }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
                   
        save_flags_to_file(all_checklists_flags, details,"IHEP_MAC_Bookkeeping/output.csv",username,usergroup,comment)
        find_unfinished_modules()
############################################################################################################################
def First_Electrical_Test(username,module_number,sensor_id,hexboard_number,baseplate_number,remeasurement_number,usergroup,comment):
    show_navigation_buttons()
    apply_double_sided_tape_completed = all(flag == 'green' for flag in Apply_double_sided_tape_flags.values())
    Apply_Double_Sided_Tape_Flag = 'green' if apply_double_sided_tape_completed else 'red'

    if Apply_Double_Sided_Tape_Flag=='red':
        st.write("Please finish the previous step first")

    if (read_user_group(username)=='All') and Apply_Double_Sided_Tape_Flag=='green':
        status_options = {
            '\u2705 Green': 'green',
            '\u26A0\uFE0F Yellow': 'yellow',
            '\u274C Red': 'red'
        }

        for step, flag in First_electrical_test_flags.items():
            selected_label = st.radio(
                f"{step} Flag:",
                list(status_options.keys()),  # Show all options as radio buttons
                index=list(status_options.values()).index(flag),
                key=f'{step}_radio',
                help=f'Click count: {click_counts_First_electrical_test[step]}'
            )
            First_electrical_test_flags[step] = status_options[selected_label]
            click_counts_First_electrical_test[step] += 1

        table_data = [[step, '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C', username] for step, flag in First_electrical_test_flags.items()]
        df_steps = pd.DataFrame(table_data, columns=["Step", "Status", "User"])

        st.write("### First Electrical Test Steps Overview")
        st.table(df_steps)


    first_electrical_test_completed = (all(flag == 'green' for flag in First_electrical_test_flags.values()))
    First_Electrical_Test_Flag = 'green' if first_electrical_test_completed else 'red'
    First_Electrical_Test_Icon = '\u2705' if First_Electrical_Test_Flag == 'green' else '\u274C'
    st.header(f"First Electrical Test Check List: {First_Electrical_Test_Icon}")
    if st.button("Save Flags to File"):
        all_checklists_flags = {
                'Apply double-sided tape':Apply_double_sided_tape_flags, 
                '1st Electrical test"':First_electrical_test_flags, 
                'Gantry assembly': Gantry_assembly_flags,
                'OGP of gantry assembly':OGP_gantry_assembly_flags,
                'Ready for bonding':Ready_for_bonding_flags, 
                'Bonding completed':Bonding_completed_flags,
                'OGP of bonding':OGP_bonding_flags,
                'Encapsulation':Encapsulation_flags,
                'Ready for the 2nd Electrical test':Ready_for_second_electrical_test_flags,
                '2nd Electrical test':Second_electrical_test_flags,
            }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
                   
        save_flags_to_file(all_checklists_flags, details,"IHEP_MAC_Bookkeeping/output.csv",username,usergroup,comment)
        find_unfinished_modules()
############################################################################################################################
def Gantry_Assembly(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment):
    show_navigation_buttons()
    first_electrical_test_completed = all(flag == 'green' for flag in First_electrical_test_flags.values())
    First_Electrical_Test_Flag = 'green' if first_electrical_test_completed else 'red'

    if First_Electrical_Test_Flag == 'red':
        st.write("Please finish the previous step first")

    if (read_user_group(username) == 'All') and First_Electrical_Test_Flag == 'green':
        status_options = {
            '\u2705 Green': 'green',
            '\u26A0\uFE0F Yellow': 'yellow',
            '\u274C Red': 'red'
        }

        for step, flag in Gantry_assembly_flags.items():
            selected_label = st.radio(
                f"{step} Flag:",
                list(status_options.keys()),
                index=list(status_options.values()).index(flag),
                key=f'{step}_radio',
                help=f'Click count: {click_counts_Gantry_assembly[step]}'
            )
            Gantry_assembly_flags[step] = status_options[selected_label]
            click_counts_Gantry_assembly[step] += 1

        table_data = [[step, '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C', username] for step, flag in Gantry_assembly_flags.items()]
        df_steps = pd.DataFrame(table_data, columns=["Step", "Status", "User"])

        st.write("### Gantry Assembly Steps Overview")
        st.table(df_steps)

    gantry_assembly_completed = (all(flag == 'green' for flag in Gantry_assembly_flags.values()))
    Gantry_Assembly_Flag = 'green' if gantry_assembly_completed else 'red'
    Gantry_Assembly_Icon = '\u2705' if Gantry_Assembly_Flag == 'green' else '\u274C'
    st.header(f"Gantry Assembly Check List: {Gantry_Assembly_Icon}")
    if st.button("Save Flags to File"):
        all_checklists_flags = {
            'Apply double-sided tape': Apply_double_sided_tape_flags,
            'Gantry assembly': Gantry_assembly_flags,
            'OGP of gantry assembly': OGP_gantry_assembly_flags,
            'Ready for bonding': Ready_for_bonding_flags,
            'Bonding completed': Bonding_completed_flags,
            'OGP of bonding': OGP_bonding_flags,
            'Encapsulation': Encapsulation_flags,
            'Ready for the 2nd Electrical test': Ready_for_second_electrical_test_flags,
            '2nd Electrical test': Second_electrical_test_flags,
        }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
        save_flags_to_file(all_checklists_flags, details, "IHEP_MAC_Bookkeeping/output.csv", username, usergroup, comment)
        find_unfinished_modules()
############################################################################################################################
def OGP_Gantry_Assembly(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment):
    show_navigation_buttons()
    gantry_assembly_completed = all(flag == 'green' for flag in Gantry_assembly_flags.values())
    Gantry_Assembly_Flag = 'green' if gantry_assembly_completed else 'red'

    if Gantry_Assembly_Flag == 'red':
        st.write("Please finish the previous step first")

    if (read_user_group(username) == 'All') and Gantry_Assembly_Flag == 'green':
        status_options = {
            '\u2705 Green': 'green',
            '\u26A0\uFE0F Yellow': 'yellow',
            '\u274C Red': 'red'
        }

        for step, flag in OGP_gantry_assembly_flags.items():
            selected_label = st.radio(
                f"{step} Flag:",
                list(status_options.keys()),
                index=list(status_options.values()).index(flag),
                key=f'{step}_radio',
                help=f'Click count: {click_counts_OGP_gantry_assembly[step]}'
            )
            OGP_gantry_assembly_flags[step] = status_options[selected_label]
            click_counts_OGP_gantry_assembly[step] += 1

        table_data = [[step, '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C', username] for step, flag in OGP_gantry_assembly_flags.items()]
        df_steps = pd.DataFrame(table_data, columns=["Step", "Status", "User"])

        st.write("### OGP of Gantry Assembly Steps Overview")
        st.table(df_steps)

    ogp_gantry_assembly_completed = (all(flag == 'green' for flag in OGP_gantry_assembly_flags.values()))
    OGP_Gantry_Assembly_Flag = 'green' if ogp_gantry_assembly_completed else 'red'
    OGP_Gantry_Assembly_Icon = '\u2705' if OGP_Gantry_Assembly_Flag == 'green' else '\u274C'
    st.header(f"OGP of Gantry Assembly Check List: {OGP_Gantry_Assembly_Icon}")
    if st.button("Save Flags to File"):
        all_checklists_flags = {
            'Apply double-sided tape': Apply_double_sided_tape_flags,
            'Gantry assembly': Gantry_assembly_flags,
            'OGP of gantry assembly': OGP_gantry_assembly_flags,
            'Ready for bonding': Ready_for_bonding_flags,
            'Bonding completed': Bonding_completed_flags,
            'OGP of bonding': OGP_bonding_flags,
            'Encapsulation': Encapsulation_flags,
            'Ready for the 2nd Electrical test': Ready_for_second_electrical_test_flags,
            '2nd Electrical test': Second_electrical_test_flags,
        }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
        save_flags_to_file(all_checklists_flags, details, "IHEP_MAC_Bookkeeping/output.csv", username, usergroup, comment)
        find_unfinished_modules()
############################################################################################################################

def Ready_for_Bonding(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment):
    show_navigation_buttons()
    ogp_gantry_assembly_completed = all(flag == 'green' for flag in OGP_gantry_assembly_flags.values())
    OGP_Gantry_Assembly_Flag = 'green' if ogp_gantry_assembly_completed else 'red'

    if OGP_Gantry_Assembly_Flag == 'red':
        st.write("Please finish the previous step first")

    if (read_user_group(username) == 'All') and OGP_Gantry_Assembly_Flag == 'green':
        status_options = {
            '\u2705 Green': 'green',
            '\u26A0\uFE0F Yellow': 'yellow',
            '\u274C Red': 'red'
        }

        for step, flag in Ready_for_bonding_flags.items():
            selected_label = st.radio(
                f"{step} Flag:",
                list(status_options.keys()),
                index=list(status_options.values()).index(flag),
                key=f'{step}_radio',
                help=f'Click count: {click_counts_Ready_for_bonding[step]}'
            )
            Ready_for_bonding_flags[step] = status_options[selected_label]
            click_counts_Ready_for_bonding[step] += 1

        table_data = [[step, '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C', username] for step, flag in Ready_for_bonding_flags.items()]
        df_steps = pd.DataFrame(table_data, columns=["Step", "Status", "User"])

        st.write("### Ready for Bonding Steps Overview")
        st.table(df_steps)

    ready_for_bonding_completed = (all(flag == 'green' for flag in Ready_for_bonding_flags.values()))
    Ready_for_Bonding_Flag = 'green' if ready_for_bonding_completed else 'red'
    Ready_for_Bonding_Icon = '\u2705' if Ready_for_Bonding_Flag == 'green' else '\u274C'
    st.header(f"Ready for Bonding Check List: {Ready_for_Bonding_Icon}")
    if st.button("Save Flags to File"):
        all_checklists_flags = {
            'Apply double-sided tape': Apply_double_sided_tape_flags,
            'Gantry assembly': Gantry_assembly_flags,
            'OGP of gantry assembly': OGP_gantry_assembly_flags,
            'Ready for bonding': Ready_for_bonding_flags,
            'Bonding completed': Bonding_completed_flags,
            'OGP of bonding': OGP_bonding_flags,
            'Encapsulation': Encapsulation_flags,
            'Ready for the 2nd Electrical test': Ready_for_second_electrical_test_flags,
            '2nd Electrical test': Second_electrical_test_flags,
        }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
        save_flags_to_file(all_checklists_flags, details, "IHEP_MAC_Bookkeeping/output.csv", username, usergroup, comment)
        find_unfinished_modules()
############################################################################################################################
def Bonding_Completed(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment):
    show_navigation_buttons()
    ready_for_bonding_completed = all(flag == 'green' for flag in Ready_for_bonding_flags.values())
    Ready_for_Bonding_Flag = 'green' if ready_for_bonding_completed else 'red'

    if Ready_for_Bonding_Flag == 'red':
        st.write("Please finish the previous step first")

    if (read_user_group(username) == 'All') and Ready_for_Bonding_Flag == 'green':
        status_options = {
            '\u2705 Green': 'green',
            '\u26A0\uFE0F Yellow': 'yellow',
            '\u274C Red': 'red'
        }

        for step, flag in Bonding_completed_flags.items():
            selected_label = st.radio(
                f"{step} Flag:",
                list(status_options.keys()),
                index=list(status_options.values()).index(flag),
                key=f'{step}_radio',
                help=f'Click count: {click_counts_Bonding_completed[step]}'
            )
            Bonding_completed_flags[step] = status_options[selected_label]
            click_counts_Bonding_completed[step] += 1

        table_data = [[step, '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C', username] for step, flag in Bonding_completed_flags.items()]
        df_steps = pd.DataFrame(table_data, columns=["Step", "Status", "User"])

        st.write("### Bonding Completed Steps Overview")
        st.table(df_steps)

    bonding_completed = (all(flag == 'green' for flag in Bonding_completed_flags.values()))
    Bonding_Completed_Flag = 'green' if bonding_completed else 'red'
    Bonding_Completed_Icon = '\u2705' if Bonding_Completed_Flag == 'green' else '\u274C'
    st.header(f"Bonding Completed Check List: {Bonding_Completed_Icon}")
    if st.button("Save Flags to File"):
        all_checklists_flags = {
            'Apply double-sided tape': Apply_double_sided_tape_flags,
            'Gantry assembly': Gantry_assembly_flags,
            'OGP of gantry assembly': OGP_gantry_assembly_flags,
            'Ready for bonding': Ready_for_bonding_flags,
            'Bonding completed': Bonding_completed_flags,
            'OGP of bonding': OGP_bonding_flags,
            'Encapsulation': Encapsulation_flags,
            'Ready for the 2nd Electrical test': Ready_for_second_electrical_test_flags,
            '2nd Electrical test': Second_electrical_test_flags,
        }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
        save_flags_to_file(all_checklists_flags, details, "IHEP_MAC_Bookkeeping/output.csv", username, usergroup, comment)
        find_unfinished_modules()

############################################################################################################################
def OGP_Bonding(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment):
    show_navigation_buttons()
    bonding_completed = all(flag == 'green' for flag in Bonding_completed_flags.values())
    Bonding_Completed_Flag = 'green' if bonding_completed else 'red'

    if Bonding_Completed_Flag == 'red':
        st.write("Please finish the previous step first")

    if (read_user_group(username) == 'All') and Bonding_Completed_Flag == 'green':
        status_options = {
            '\u2705 Green': 'green',
            '\u26A0\uFE0F Yellow': 'yellow',
            '\u274C Red': 'red'
        }

        for step, flag in OGP_bonding_flags.items():
            selected_label = st.radio(
                f"{step} Flag:",
                list(status_options.keys()),
                index=list(status_options.values()).index(flag),
                key=f'{step}_radio',
                help=f'Click count: {click_counts_OGP_bonding[step]}'
            )
            OGP_bonding_flags[step] = status_options[selected_label]
            click_counts_OGP_bonding[step] += 1

        table_data = [[step, '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C', username] for step, flag in OGP_bonding_flags.items()]
        df_steps = pd.DataFrame(table_data, columns=["Step", "Status", "User"])

        st.write("### OGP of Bonding Steps Overview")
        st.table(df_steps)

    ogp_bonding_completed = (all(flag == 'green' for flag in OGP_bonding_flags.values()))
    OGP_Bonding_Flag = 'green' if ogp_bonding_completed else 'red'
    OGP_Bonding_Icon = '\u2705' if OGP_Bonding_Flag == 'green' else '\u274C'
    st.header(f"OGP of Bonding Check List: {OGP_Bonding_Icon}")
    if st.button("Save Flags to File"):
        all_checklists_flags = {
            'Apply double-sided tape': Apply_double_sided_tape_flags,
            'Gantry assembly': Gantry_assembly_flags,
            'OGP of gantry assembly': OGP_gantry_assembly_flags,
            'Ready for bonding': Ready_for_bonding_flags,
            'Bonding completed': Bonding_completed_flags,
            'OGP of bonding': OGP_bonding_flags,
            'Encapsulation': Encapsulation_flags,
            'Ready for the 2nd Electrical test': Ready_for_second_electrical_test_flags,
            '2nd Electrical test': Second_electrical_test_flags,
        }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
        save_flags_to_file(all_checklists_flags, details, "IHEP_MAC_Bookkeeping/output.csv", username, usergroup, comment)
        find_unfinished_modules()

############################################################################################################################
def Encapsulation(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment):
    show_navigation_buttons()
    ogp_bonding_completed = all(flag == 'green' for flag in OGP_bonding_flags.values())
    OGP_Bonding_Flag = 'green' if ogp_bonding_completed else 'red'

    if OGP_Bonding_Flag == 'red':
        st.write("Please finish the previous step first")

    if (read_user_group(username) == 'All') and OGP_Bonding_Flag == 'green':
        status_options = {
            '\u2705 Green': 'green',
            '\u26A0\uFE0F Yellow': 'yellow',
            '\u274C Red': 'red'
        }

        for step, flag in Encapsulation_flags.items():
            selected_label = st.radio(
                f"{step} Flag:",
                list(status_options.keys()),
                index=list(status_options.values()).index(flag),
                key=f'{step}_radio',
                help=f'Click count: {click_counts_Encapsulation[step]}'
            )
            Encapsulation_flags[step] = status_options[selected_label]
            click_counts_Encapsulation[step] += 1

        table_data = [[step, '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C', username] for step, flag in Encapsulation_flags.items()]
        df_steps = pd.DataFrame(table_data, columns=["Step", "Status", "User"])

        st.write("### Encapsulation Steps Overview")
        st.table(df_steps)

    encapsulation_completed = (all(flag == 'green' for flag in Encapsulation_flags.values()))
    Encapsulation_Flag = 'green' if encapsulation_completed else 'red'
    Encapsulation_Icon = '\u2705' if Encapsulation_Flag == 'green' else '\u274C'
    st.header(f"Encapsulation Check List: {Encapsulation_Icon}")
    if st.button("Save Flags to File"):
        all_checklists_flags = {
            'Apply double-sided tape': Apply_double_sided_tape_flags,
            'Gantry assembly': Gantry_assembly_flags,
            'OGP of gantry assembly': OGP_gantry_assembly_flags,
            'Ready for bonding': Ready_for_bonding_flags,
            'Bonding completed': Bonding_completed_flags,
            'OGP of bonding': OGP_bonding_flags,
            'Encapsulation': Encapsulation_flags,
            'Ready for the 2nd Electrical test': Ready_for_second_electrical_test_flags,
            '2nd Electrical test': Second_electrical_test_flags,
        }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
        save_flags_to_file(all_checklists_flags, details, "IHEP_MAC_Bookkeeping/output.csv", username, usergroup, comment)
        find_unfinished_modules()

############################################################################################################################
def Ready_for_Second_Electrical_Test(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment):
    show_navigation_buttons()
    encapsulation_completed = all(flag == 'green' for flag in Encapsulation_flags.values())
    Encapsulation_Flag = 'green' if encapsulation_completed else 'red'

    if Encapsulation_Flag == 'red':
        st.write("Please finish the previous step first")

    if (read_user_group(username) == 'All') and Encapsulation_Flag == 'green':
        status_options = {
            '\u2705 Green': 'green',
            '\u26A0\uFE0F Yellow': 'yellow',
            '\u274C Red': 'red'
        }

        for step, flag in Ready_for_second_electrical_test_flags.items():
            selected_label = st.radio(
                f"{step} Flag:",
                list(status_options.keys()),
                index=list(status_options.values()).index(flag),
                key=f'{step}_radio',
                help=f'Click count: {click_counts_Ready_for_second_electrical_test[step]}'
            )
            Ready_for_second_electrical_test_flags[step] = status_options[selected_label]
            click_counts_Ready_for_second_electrical_test[step] += 1

        table_data = [[step, '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C', username] for step, flag in Ready_for_second_electrical_test_flags.items()]
        df_steps = pd.DataFrame(table_data, columns=["Step", "Status", "User"])

        st.write("### Ready for the 2nd Electrical Test Steps Overview")
        st.table(df_steps)

    ready_for_second_electrical_test_completed = (all(flag == 'green' for flag in Ready_for_second_electrical_test_flags.values()))
    Ready_for_Second_Electrical_Test_Flag = 'green' if ready_for_second_electrical_test_completed else 'red'
    Ready_for_Second_Electrical_Test_Icon = '\u2705' if Ready_for_Second_Electrical_Test_Flag == 'green' else '\u274C'
    st.header(f"Ready for the 2nd Electrical Test Check List: {Ready_for_Second_Electrical_Test_Icon}")
    if st.button("Save Flags to File"):
        all_checklists_flags = {
            'Apply double-sided tape': Apply_double_sided_tape_flags,
            'Gantry assembly': Gantry_assembly_flags,
            'OGP of gantry assembly': OGP_gantry_assembly_flags,
            'Ready for bonding': Ready_for_bonding_flags,
            'Bonding completed': Bonding_completed_flags,
            'OGP of bonding': OGP_bonding_flags,
            'Encapsulation': Encapsulation_flags,
            'Ready for the 2nd Electrical test': Ready_for_second_electrical_test_flags,
            '2nd Electrical test': Second_electrical_test_flags,
        }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
        save_flags_to_file(all_checklists_flags, details, "IHEP_MAC_Bookkeeping/output.csv", username, usergroup, comment)
        find_unfinished_modules()

############################################################################################################################
def Second_Electrical_Test(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment):
    show_navigation_buttons()
    ready_for_second_electrical_test_completed = all(flag == 'green' for flag in Ready_for_second_electrical_test_flags.values())
    Ready_for_Second_Electrical_Test_Flag = 'green' if ready_for_second_electrical_test_completed else 'red'

    if Ready_for_Second_Electrical_Test_Flag == 'red':
        st.write("Please finish the previous step first")

    if (read_user_group(username) == 'All') and Ready_for_Second_Electrical_Test_Flag == 'green':
        status_options = {
            '\u2705 Green': 'green',
            '\u26A0\uFE0F Yellow': 'yellow',
            '\u274C Red': 'red'
        }

        for step, flag in Second_electrical_test_flags.items():
            selected_label = st.radio(
                f"{step} Flag:",
                list(status_options.keys()),
                index=list(status_options.values()).index(flag),
                key=f'{step}_radio',
                help=f'Click count: {click_counts_Second_electrical_test[step]}'
            )
            Second_electrical_test_flags[step] = status_options[selected_label]
            click_counts_Second_electrical_test[step] += 1

        table_data = [[step, '\u2705' if flag == 'green' else '\u26A0\uFE0F' if flag == 'yellow' else '\u274C', username] for step, flag in Second_electrical_test_flags.items()]
        df_steps = pd.DataFrame(table_data, columns=["Step", "Status", "User"])

        st.write("### Second Electrical Test Steps Overview")
        st.table(df_steps)

    second_electrical_test_completed = (all(flag == 'green' for flag in Second_electrical_test_flags.values()))
    Second_Electrical_Test_Flag = 'green' if second_electrical_test_completed else 'red'
    Second_Electrical_Test_Icon = '\u2705' if Second_Electrical_Test_Flag == 'green' else '\u274C'
    st.header(f"Second Electrical Test Check List: {Second_Electrical_Test_Icon}")
    if st.button("Save Flags to File"):
        all_checklists_flags = {
            'Apply double-sided tape': Apply_double_sided_tape_flags,
            'Gantry assembly': Gantry_assembly_flags,
            'OGP of gantry assembly': OGP_gantry_assembly_flags,
            'Ready for bonding': Ready_for_bonding_flags,
            'Bonding completed': Bonding_completed_flags,
            'OGP of bonding': OGP_bonding_flags,
            'Encapsulation': Encapsulation_flags,
            'Ready for the 2nd Electrical test': Ready_for_second_electrical_test_flags,
            '2nd Electrical test': Second_electrical_test_flags,
        }
        details = {
            'Module Number': module_number,
            'Sensor ID': sensor_id,
            'Hexboard Number': hexboard_number,
            'Baseplate Number': baseplate_number,
            'Remeasurement Number': remeasurement_number,
        }
        save_flags_to_file(all_checklists_flags, details, "IHEP_MAC_Bookkeeping/output.csv", username, usergroup, comment)
        find_unfinished_modules()

############################################################################################################################

def find_unfinished_modules():
    # Read the IHEP_MAC_Bookkeeping/output.csv file
    df = pd.read_csv("IHEP_MAC_Bookkeeping/output.csv")

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
    unfinished_df.to_csv("IHEP_MAC_Bookkeeping/unfinished_module.csv", index=False)
############################################################################################################################
def show_unfinished_modules(username):
    # Read the unfinished_module.csv file
    unfinished_df = pd.read_csv("IHEP_MAC_Bookkeeping/unfinished_module.csv")

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
                option1=st.selectbox("Select an option", ("Overview", "Apply double-sided tape", "1st Electrical test" , "Gantry assembly",   "OGP of gantry assembly", "Ready for bonding", "Bonding completed",  "OGP of bonding", "Encapsulation", "Ready for the 2nd Electrical test", "2nd Electrical test"),key="option1")
            if option1=='Overview':
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                
                apply_double_sided_tape_completed = all(flag == 'green' for flag in Apply_double_sided_tape_flags.values())
                Apply_Double_Sided_Tape_Flag = 'green' if apply_double_sided_tape_completed else 'red'
                Apply_double_sided_tape_Icon = '\u2705' if Apply_Double_Sided_Tape_Flag == 'green' else '\u274C'

                first_electrical_test_completed = all(flag == 'green' for flag in First_electrical_test_flags.values())
                First_Electrical_Test_Flag = 'green' if first_electrical_test_completed else 'red'
                First_Electrical_Test_Icon = '\u2705' if First_Electrical_Test_Flag == 'green' else '\u274C'

                gantry_assembly_completed = all(flag == 'green' for flag in Gantry_assembly_flags.values())
                Gantry_Assembly_Flag = 'green' if gantry_assembly_completed else 'red'
                Gantry_Assembly_Icon = '\u2705' if Gantry_Assembly_Flag == 'green' else '\u274C'

                ogp_gantry_assembly_completed = all(flag == 'green' for flag in OGP_gantry_assembly_flags.values())
                OGP_Gantry_Assembly_Flag = 'green' if ogp_gantry_assembly_completed else 'red'
                OGP_Gantry_Assembly_Icon = '\u2705' if OGP_Gantry_Assembly_Flag == 'green' else '\u274C'

                ready_for_bonding_completed = all(flag == 'green' for flag in Ready_for_bonding_flags.values())
                Ready_for_Bonding_Flag = 'green' if ready_for_bonding_completed else 'red'
                Ready_for_Bonding_Icon = '\u2705' if Ready_for_Bonding_Flag == 'green' else '\u274C'

                bonding_completed = all(flag == 'green' for flag in Bonding_completed_flags.values())
                Bonding_Completed_Flag = 'green' if bonding_completed else 'red'
                Bonding_Completed_Icon = '\u2705' if Bonding_Completed_Flag == 'green' else '\u274C'

                ogp_bonding_completed = all(flag == 'green' for flag in OGP_bonding_flags.values())
                OGP_Bonding_Flag = 'green' if ogp_bonding_completed else 'red'
                OGP_Bonding_Icon = '\u2705' if OGP_Bonding_Flag == 'green' else '\u274C'

                encapsulation_completed = all(flag == 'green' for flag in Encapsulation_flags.values())
                Encapsulation_Flag = 'green' if encapsulation_completed else 'red'
                Encapsulation_Icon = '\u2705' if Encapsulation_Flag == 'green' else '\u274C'

                ready_for_second_electrical_test_completed = all(flag == 'green' for flag in Ready_for_second_electrical_test_flags.values())
                Ready_for_Second_Electrical_Test_Flag = 'green' if ready_for_second_electrical_test_completed else 'red'
                Ready_for_Second_Electrical_Test_Icon = '\u2705' if Ready_for_Second_Electrical_Test_Flag == 'green' else '\u274C'

                second_electrical_test_completed = all(flag == 'green' for flag in Second_electrical_test_flags.values())
                Second_Electrical_Test_Flag = 'green' if second_electrical_test_completed else 'red'
                Second_Electrical_Test_Icon = '\u2705' if Second_Electrical_Test_Flag == 'green' else '\u274C'

            if option1 == "Apply double-sided tape":
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Apply_Double_Sided_Tape(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment)

            if option1 == "1st Electrical test":
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                First_Electrical_Test(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment)

            if option1 == "Gantry assembly":
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Gantry_Assembly(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment)

            if option1 == "OGP of gantry assembly":
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                OGP_Gantry_Assembly(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment)

            if option1 == "Ready for bonding":
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Ready_for_Bonding(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment)

            if option1 == "Bonding completed":
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Bonding_Completed(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment)

            if option1 == "OGP of bonding":
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                OGP_Bonding(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment)

            if option1 == "Encapsulation":
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Encapsulation(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment)

            if option1 == "Ready for the 2nd Electrical test":
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Ready_for_Second_Electrical_Test(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment)

            if option1 == "2nd Electrical test":
                initialize_session_state(module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number)
                Second_Electrical_Test(username, module_number, sensor_id, hexboard_number, baseplate_number, remeasurement_number, usergroup, comment)
            

###################################################################################################################################################################
def plot_selected_module():
    module_number = st.text_input("Enter Module Number")
    sensor_id = st.text_input("Enter Sensor ID")
    hexboard_number = st.text_input("Enter Hexboard Number")
    baseplate_number = st.text_input("Enter Baseplate Number")
    remeasurement_number=st.text_input("Enter Remeasurement Number(0 for the first measurement)")
    if st.checkbox("Submit"):
        if module_number and sensor_id and hexboard_number and baseplate_number and remeasurement_number:
    # Read the IHEP_MAC_Bookkeeping/output.csv file
            df = pd.read_csv("IHEP_MAC_Bookkeeping/output.csv", dtype={'Module Number': str, 'Sensor ID': str, 'Hexboard Number': str, 'Baseplate Number': str, 'Remeasurement Number':str})

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

def plot_modules(start_date=None, end_date=None):
    # Read the IHEP_MAC_Bookkeeping/output.csv file
    df = pd.read_csv("IHEP_MAC_Bookkeeping/output.csv")

    # Convert 'DateAndTime' to datetime
    df["DateAndTime"] = pd.to_datetime(df["DateAndTime"])

    if start_date:
        df = df[df["DateAndTime"] >= start_date]
    if end_date:
        df = df[df["DateAndTime"] <= end_date]

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
    st.title("CMS HGCal IHEP MAC: Module Assembly and Status Bookkeeping System")
    st.image("IHEP_MAC_Bookkeeping/ReeseLabs_hexagon.jpg", use_container_width=True)
    # Add content for the home page
##############################################################################################################################################
def main():
    st.set_page_config(layout="wide", page_title="HGCAL IHEP MAC", page_icon="IHEP_MAC_Bookkeeping/hex_ver_1.png")


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
        st.sidebar.write("### Select an Option")


        option = st.sidebar.selectbox("Select an option", ("Home", "Module Assembly Check List", "Unfinished Modules", "Module Status Summary"), key="option_select")  # Unique key for option select
        
        if option == "Home":
            home_page()
        if option == "Module Assembly Check List":
            Module_Assembly_Check_List(username)
        if option == "Unfinished Modules":
            show_unfinished_modules(username)
        if option== "Module Status Summary":
            # Date selection for filtering
            df = pd.read_csv("IHEP_MAC_Bookkeeping/output.csv")
            df["DateAndTime"] = pd.to_datetime(df["DateAndTime"])
            min_date = df["DateAndTime"].min()
            max_date = df["DateAndTime"].max()
            start_date = st.date_input("Select Start Date", min_value=min_date, max_value=max_date, value=min_date)
            end_date = st.date_input("Select End Date", min_value=min_date, max_value=max_date, value=max_date)
            # Convert selected dates to datetime
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            plot = plot_modules(start_date, end_date)

            st.markdown(plot, unsafe_allow_html=True)
        
        st.sidebar.button("Logout", on_click=lambda: st.session_state.update(authenticated=False))  # Logout Button

    if show_image:
        st.title("Welcome to the HGCal IHEP MAC Bookkeeping Site")

        st.image("IHEP_MAC_Bookkeeping/CMS_detector.jpeg", use_container_width=True)
        #st.write("Welcome to the CMS HGCal IHEP MAC Bookkeeping System")
        col1, col2, col3 = st.columns([3, 2, 1])  # Equal width for both columns
        with col2:
            st.image("IHEP_MAC_Bookkeeping/ihep.png",  width=300)
        with col3:
            st.image("IHEP_MAC_Bookkeeping/CMS.png",  width=150)

        if not login_button and not logged_in:
            st.error("Please log in")
if __name__ == "__main__":
    main()

