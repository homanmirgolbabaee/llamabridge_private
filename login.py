import streamlit as st

# Hardcoded credentials for demo with first names
DEMO_USERS = {
    "homan.mirgolbabaee@studenti.unipd.it": {"password": "password", "first_name": "Homan"},
    "sam@studenti.uniroma1.it": {"password": "password", "first_name": "Sam"},
    "andrew@studenti.unime.it": {"password": "password", "first_name": "Andrew"},
    "maria@studenti.unipv.it": {"password": "password", "first_name": "Maria"}
}

def check_password():
    """Returns `True` if the user had correct credentials."""
    
    # Initialize session state variables
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_first_name" not in st.session_state:
        st.session_state.user_first_name = ""
    if "current_user" not in st.session_state:
        st.session_state.current_user = ""
    
    def verify_credentials():
        """Checks whether entered credentials are correct."""
        username = st.session_state["username"].strip()
        password = st.session_state["password"].strip()
        
        if username in DEMO_USERS and DEMO_USERS[username]["password"] == password:
            st.session_state.user_first_name = DEMO_USERS[username]["first_name"]
            st.session_state.current_user = username
            st.session_state.authenticated = True
            return True
        st.error("❌ Invalid username or password")
        return False
        
    if not st.session_state.authenticated:
        st.title("🔒 Login")
        
        # Center the login form using columns
        col1, col2, col3 = st.columns([1,2,1])
        
        with col2:
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            if st.button("Login", type="primary"):
                if verify_credentials():
                    st.rerun()  # Using st.rerun() instead of experimental_rerun()
            
            # Add a demo credentials hint
            with st.expander("Demo Credentials"):
                st.write("Available demo users:")
                for email, details in DEMO_USERS.items():
                    st.code(f"Username: {email}\nPassword: password")

    return st.session_state.authenticated