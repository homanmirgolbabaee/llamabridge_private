import streamlit as st
import os

# Hardcoded credentials for demo with first names and university identifiers
DEMO_USERS = {
    "homan.mirgolbabaee@studenti.unipd.it": {
        "password": "password", 
        "first_name": "Homan",
        "university": "unipd"
    },
    "sam@studenti.uniroma1.it": {
        "password": "password", 
        "first_name": "Sam",
        "university": "uniroma1"
    },
    "andrew@studenti.unime.it": {
        "password": "password", 
        "first_name": "Andrew",
        "university": "unime"
    },
    "maria@studenti.unipv.it": {
        "password": "password", 
        "first_name": "Maria",
        "university": "unipv"
    }
}

# University display names for better presentation
UNIVERSITY_NAMES = {
    "unipd": "University of Padua",
    "uniroma1": "Sapienza University of Rome",
    "unime": "University of Messina",
    "unipv": "University of Pavia"
}

def get_logo_path(university_id):
    """Get the path to the university logo"""
    return os.path.join("assets", "logos", f"{university_id}.svg")

def check_password():
    """Returns `True` if the user had correct credentials."""
    
    # Initialize session state variables
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_first_name" not in st.session_state:
        st.session_state.user_first_name = ""
    if "current_user" not in st.session_state:
        st.session_state.current_user = ""
    if "university" not in st.session_state:
        st.session_state.university = ""
    
    def verify_credentials():
        """Checks whether entered credentials are correct."""
        username = st.session_state["username"].strip()
        password = st.session_state["password"].strip()
        
        if username in DEMO_USERS and DEMO_USERS[username]["password"] == password:
            st.session_state.user_first_name = DEMO_USERS[username]["first_name"]
            st.session_state.current_user = username
            st.session_state.university = DEMO_USERS[username]["university"]
            st.session_state.authenticated = True
            return True
        st.error("❌ Invalid username or password")
        return False
        
    if not st.session_state.authenticated:
        # Add custom CSS for centered title and notice
        st.markdown("""
            <style>
                div[data-testid="stTitle"] {
                    text-align: center;
                    padding: 1rem 0;
                    margin-bottom: 2rem;
                }
                div.stButton > button {
                    width: 100%;
                }
                .demo-notice {
                    padding: 1rem;
                    background-color: #f0f2f6;
                    border-radius: 0.5rem;
                    margin: 1rem 0;
                    text-align: center;
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Create empty columns for spacing
        _, center_col, _ = st.columns([1,2,1])        
        # Add demo notice at the top
        st.markdown("""
            <div class='demo-notice'>
                <h3>🚧 Demo Version Notice</h3>
                <p>Currently, the <strong>"How To Obtain Residence Permit"</strong> feature is fully functional as shown in hackathon demo. 
                <p>
                I will make the other features as seemless as soon as possible ! 
                </p>
                </p>
                <p> Thank you for your understanding!</p> 
            </div>
        """, unsafe_allow_html=True)
        
        center_col.title("🔒 Login")



        with center_col:
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            if st.button("Login", type="primary"):
                if verify_credentials():
                    st.rerun()
            
            # Add a demo credentials hint
            with st.expander("Demo Credentials"):
                st.write("Available demo users:")
                for email, details in DEMO_USERS.items():
                    univ_name = UNIVERSITY_NAMES[details["university"]]
                    st.code(f"Username: {email}\nPassword: password\nUniversity: {univ_name}")

    return st.session_state.authenticated