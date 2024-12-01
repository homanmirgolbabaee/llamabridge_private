import streamlit as st
from toolhouse import Toolhouse
from llms import llms, llm_call
from http_exceptions.client_exceptions import NotFoundException
from login import check_password,get_logo_path
from datetime import datetime, timedelta

from st_utils import print_messages, append_and_print
#from dotenv import load_dotenv
from login import *
import time

import streamlit as st
import webbrowser
from PIL import Image
import requests
from io import BytesIO

import base64


#load_dotenv()

def get_template_config():
    """Define templates with their additional system instructions"""
    return [
        {
            "logo": get_image_as_base64("assets/Poste.png"),
            "question": "How to obtain Residence Permit",
            "category": "Postal Services",
            "additional_instructions": """ use perplexity tool for query : "How to obtain Residence Permit as an Inernational Student Residing in city of Padova"  """
        },
        {
            "logo": get_image_as_base64("assets/Banco.png"),
            "question": "How to open a Bank account in Intesa Sanpaolo Bank?",
            "category": "Banking",
            "additional_instructions": """ use perplexity_byok tool for query: "How to Open a Bank account in Intesa Sanpaolo Bank? as an Inernational Student Residing in city of Padova """
        },
        {
            "logo": get_image_as_base64("assets/Entrate.png"),
            "question": "How to obtain Codice Fiscale",
            "category": "Insurance/Taxation",
            "additional_instructions": """ use perplexity tool for query : "How to obtain Codice Fiscale Inernational Student Residing in city of Padova" as an Inernational Student Residing in city of Padova  """
        },
        {
            "logo": get_image_as_base64("assets/Poste.png"),
            "question": "How to apply for Carta di identita ?",
            "category": "Services",
            "additional_instructions": """ use perplexity tool for query :  "How to apply for Carta di identita "  as an Inernational Student Residing in city of Padova """
        }
    ]



# Utility functions for student dashboard
def get_document_status():
    """Get the status of required documents"""
    return {
        "Passport Copy": "completed",
        "Student Visa": "completed",
        "Residence Permit": "in_progress",
        "Bank Account": "pending",
        "Codice Fiscale": "pending",
        "Health Insurance": "not_started"
    }

def get_upcoming_appointments():
    """Get upcoming appointments"""
    return [
        {
            "type": "Questura",
            "purpose": "Residence Permit",
            "date": datetime.now() + timedelta(days=5),
            "status": "confirmed"
        },
        {
            "type": "Bank",
            "purpose": "Account Opening",
            "date": datetime.now() + timedelta(days=8),
            "status": "pending"
        },
        {
            "type": "University",
            "purpose": "Codice Fiscale",
            "date": datetime.now() + timedelta(days=3),
            "status": "confirmed"
        }
    ]

import pandas as pd

def get_activity_data():
    """Get activity data for charts"""
    return pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr'],
        'Appointments': [15, 20, 18, 25],
        'Documents': [8, 12, 10, 15],
        'Community': [45, 72, 95, 127]
    })




def render_document_status(status):
    """Render document status with appropriate emoji"""
    status_emoji = {
        "completed": "✅",
        "in_progress": "⏳",
        "pending": "⌛",
        "not_started": "❌"
    }
    return status_emoji.get(status, "❓")

def render_template_questions():
    """Render template questions in a grid layout with larger agency logos"""
    # Custom CSS for the template cards with larger logos
    st.markdown("""
        <style>
        .template-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin: 8px;
            cursor: pointer;
            background-color: white;
            transition: transform 0.2s, box-shadow 0.2s;
            height: 100%;
            display: flex;
            flex-direction: column;
        }
        .template-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            background-color: #f8f9fa;
        }
        .template-icon {
            margin-bottom: 12px;
            text-align: center;
            min-height: 80px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .template-icon img {
            width: 80px;
            height: 80px;
            object-fit: contain;
        }
        .template-content {
            flex-grow: 1;
            display: flex;
            flex-direction: column;
        }
        .template-question {
            font-size: 0.95rem;
            margin: 8px 0;
            color: #1a1a1a;
            line-height: 1.4;
        }
        .template-category {
            color: #666;
            font-size: 0.8rem;
            margin-top: auto;
            padding-top: 8px;
            border-top: 1px solid #eee;
        }
        </style>
    """, unsafe_allow_html=True)

    # Template questions with agency logos
    templates = get_template_config()

    # Initialize session states
    if "selected_template" not in st.session_state:
        st.session_state.selected_template = None
    if "template_submitted" not in st.session_state:
        st.session_state.template_submitted = False
    if "additional_instructions" not in st.session_state:
        st.session_state.additional_instructions = None

    # Create a 2x2 grid for template questions
    col1, col2 = st.columns(2)

    # Display templates in grid
    for idx, template in enumerate(templates):
        with col1 if idx % 2 == 0 else col2:
            if st.button(
                template['question'],
                key=f"template_{idx}",
                use_container_width=True,
                help=f"Click to ask about {template['category']}"
            ):
                st.session_state.selected_template = template['question']
                st.session_state.additional_instructions = template['additional_instructions']
                st.session_state.template_submitted = True
                if template['question'] == "How to obtain Residence Permit":
                    st.session_state.show_download = True    
                st.rerun()  # Force a rerun to update the sidebar
def render_user_profile():
    """Render user profile section with optimized university logo display"""
    with st.container():
        # Adjusted column ratio for better logo visibility
        user_col, logo_col = st.columns([2, 1])
        
        with user_col:
            # Added padding and styling
            st.markdown("""
                <style>
                    .user-greeting { font-size: 1.2rem; margin-bottom: 0; }
                    .university-info { color: #666; margin-top: 0; }
                </style>
            """, unsafe_allow_html=True)
            
            # User information with improved styling
            st.markdown(f"<p class='user-greeting'> Hello, {st.session_state.user_first_name}👋</p>", 
                       unsafe_allow_html=True)
            st.markdown(f"<p class='university-info'>{UNIVERSITY_NAMES[st.session_state.university]}</p>", 
                       unsafe_allow_html=True)
            st.caption(f"Last login: Today at {datetime.now().strftime('%H:%M')}")
        
        with logo_col:
            # Load and display the logo with optimized settings
            logo_path = get_logo_path(st.session_state.university)
            if os.path.exists(logo_path):
                # Added container for better logo positioning
                with st.container():
                    # Increased size and added padding
                    st.image(logo_path, width=80, use_column_width=False)
                    
            else:
                # Fallback if logo is missing
                st.warning("University logo not found", icon="🏛️")

def render_student_dashboard():
    """Render the complete student dashboard"""
    st.header("📊 Student Services Dashboard")

    # Custom CSS for better styling
    st.markdown("""
        <style>
        .metric-card {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .activity-item {
            padding: 0.5rem;
            border-left: 3px solid #007bff;
            margin-bottom: 0.5rem;
            background-color: #f8f9fa;
        }
        .document-status {
            margin: 0.5rem 0;
            padding: 0.5rem;
            border-radius: 0.25rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Main metrics
    col1, col2, col3 = st.columns(3)
    
    # Get data
    doc_status = get_document_status()
    appointments = get_upcoming_appointments()
    completed_docs = sum(1 for status in doc_status.values() if status == "completed")
    total_docs = len(doc_status)
    urgent_reminders = sum(1 for apt in appointments if apt["date"] <= datetime.now() + timedelta(days=7))

    with col1:
        st.metric(
            label="📅 Upcoming Appointments",
            value=len(appointments),
        )
    with col2:
        st.metric(
            label="📄 Document Status",
            value=f"{completed_docs}/{total_docs}",
        )
    with col3:
        st.metric(
            label="🔔 Pending Reminders",
            value=urgent_reminders,
        )

    # Two-column layout for main content
    left_col, right_col = st.columns([2, 1])

    with left_col:
        # Recent Activity
        st.subheader("🔄 Recent Activity")
        for appointment in appointments:
            st.markdown(
                f"""<div class="activity-item">
                    {appointment['type']}: {appointment['purpose']}
                    <br><small>📅 {appointment['date'].strftime('%B %d, %Y')}</small>
                </div>""",
                unsafe_allow_html=True
            )

    with right_col:
        # Document Checklist
        with st.expander("📋 Document Checklist", expanded=True):
            for doc, status in doc_status.items():
                st.markdown(
                    f"""<div class="document-status">
                        {render_document_status(status)} {doc}
                    </div>""",
                    unsafe_allow_html=True
                )
        
def render_advanced_settings():
    """Render advanced settings that were previously in sidebar"""
    t = Toolhouse(provider=st.session_state.provider)
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            llm_choice = st.selectbox("Model", tuple(llms.keys()), 
                                    index=tuple(llms.keys()).index(st.session_state.llm_choice))
            st.session_state.stream = st.toggle("Stream responses", True)
            user_input = st.text_input("User", st.session_state.user)
            if user_input != st.session_state.user:
                st.session_state.user = user_input


        with col2:
            st.session_state.bundle = st.text_input("Bundle", "default")
            available_tools = None
            #st.session_state.tools = t.get_tools(bundle=st.session_state.bundle)
            
            # Tool loading progress
            with st.spinner("Loading tools..."):
                progress_bar = st.progress(0)
                try:
                    for i in range(100):
                        time.sleep(0.01)
                        progress_bar.progress(i + 1)
                    
                    available_tools = t.get_tools(bundle=st.session_state.bundle)
                    st.session_state.tools = available_tools

                except NotFoundException:
                    available_tools = None
                finally:
                    progress_bar.empty()

            if not available_tools:
                st.error("⚠️ No tools installed", icon="🔧")
                st.caption(
                    "Go to the [Tool Store](https://app.toolhouse.ai/store) to install your tools, or visit [Bundles](https://app.toolhouse.ai/bundles) to check if the selected bundle exists."
                )
    
    return llm_choice







def render_chat():

    
    """Render the chat interface"""
    # Sidebar for chat settings
    with st.sidebar:
        t = Toolhouse(provider=st.session_state.provider)
        st.title("💬 Llama Bridge 🦙🌉")
        
        # Add download button section
        if "show_download" not in st.session_state:
            st.session_state.show_download = False
            
        # Debug information (you can remove these after confirming it works)
        #st.write("Debug Info:")
        #st.write(f"Selected Template: {st.session_state.get('selected_template')}")
        #st.write(f"Show Download: {st.session_state.show_download}")


        # Check if the Residence Permit template was selected
        if (hasattr(st.session_state, 'selected_template') and 
            st.session_state.selected_template == "How to obtain Residence Permit"):
            st.session_state.show_download = True
            st.write("Template matched - should show download button")

        # Show download button if template was selected
        if st.session_state.show_download:
            st.markdown("---")
            st.markdown("### 📑 Download Resources")
            
            try:
                # Add download button for PDF
                with open("data/guide.pdf", "rb") as pdf_file:
                    st.download_button(
                        label="📥 Download Residence Permit Guide",
                        data=pdf_file,
                        file_name="guide.pdf",
                        mime="application/pdf",
                        help="Download the complete guide for obtaining residence permit",
                        key="download_permit_guide"
                    )
                # Optional: Add a reset button to hide the download section
                if st.button("Hide Download Section"):
                    st.session_state.show_download = False
                    st.rerun()

            except FileNotFoundError:
                st.error("PDF file not found. Please ensure 'guide.pdf' exists in the 'data' folder.")
            


        # Add progress bar for tool loading
        with st.spinner("Loading tools..."):
            progress_bar = st.progress(0)
            try:
                # Simulate loading progress
                for i in range(100):
                    time.sleep(0.01)  # Small delay for visual effect
                    progress_bar.progress(i + 1)
                
                available_tools = t.get_tools(bundle=st.session_state.bundle)
                st.session_state.tools = available_tools

            except NotFoundException:
                available_tools = None

            finally:
                progress_bar.empty()  # Remove progress bar after loading

        # Custom CSS for tool display and footer
        st.markdown("""
            <style>
                .tool-container {
                    background-color: #f0f2f6;
                    border-radius: 4px;
                    padding: 8px;
                    margin: 4px 0;
                }
                .tool-header {
                    color: #0e1117;
                    font-size: 0.9em;
                    font-weight: 600;
                    margin-bottom: 8px;
                }
                .tool-list {
                    max-height: 200px;
                    overflow-y: auto;
                }
                .tool-item {
                    background-color: white;
                    border-radius: 3px;
                    padding: 4px 8px;
                    margin: 4px 0;
                    font-size: 0.8em;
                    border-left: 3px solid #ff4b4b;
                }
                .tool-count {
                    color: #666;
                    font-size: 0.8em;
                    margin-left: 4px;
                }
                .sidebar-footer {
                    position: fixed;
                    bottom: 20px;
                    left: 0;
                    width: 100%;
                    padding: 10px;
                    text-align: center;
                    background: linear-gradient(to bottom, transparent, rgba(255,255,255,0.9) 20%);
                }
                .footer-text {
                    margin: 0;
                    padding: 2px 0;
                    font-size: 0.7em;
                    color: #666;
                }
            </style>
        """, unsafe_allow_html=True)

        available_tools = st.session_state.tools
    
        # Tool display section
        if not available_tools:
            st.error("⚠️ No tools installed", icon="🔧")
            st.caption(
                "Go to the [Tool Store](https://app.toolhouse.ai/store) to install your tools, or visit [Bundles](https://app.toolhouse.ai/bundles) to check if the selected bundle exists."
            )

        else:
            with st.expander("🔧 Available Tools"):
                tool_count = len(available_tools)
                st.markdown(
                    f'<div class="tool-container">'
                    f'<div class="tool-header">Installed Tools <span class="tool-count">({tool_count})</span></div>'
                    '<div class="tool-list">',
                    unsafe_allow_html=True
                )
                
                for tool in available_tools:
                    tool_name = tool.get("name")
                    if st.session_state.provider != "anthropic":
                        tool_name = tool["function"].get("name")
                    st.markdown(
                        f'<div class="tool-item">'
                        f'<a href="https://app.toolhouse.ai/store/{tool_name}" target="_blank" '
                        f'style="text-decoration: none; color: inherit;">{tool_name}</a>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                
                st.markdown('</div></div>', unsafe_allow_html=True)
        
        # Add some vertical space before the captions
        st.markdown("<br>" * 5, unsafe_allow_html=True)
        
        # Simple captions at the bottom
        st.markdown("---")
        st.markdown('<div class="caption-container">', unsafe_allow_html=True)
        st.caption("Powered by Toolhouse & Groq")
        st.caption("Lablab.ai & LlamaImpact Hackathon Product")
        st.markdown('</div>', unsafe_allow_html=True)



    # Main chat area
    st.header("💬 Chat")

    with st.expander("📝 Quick Questions", expanded=True):
        render_template_questions()


    # Create a container for the chat history
    chat_container = st.container()
    
    # Initialize LLM settings
    llm = llms.get(st.session_state.llm_choice)
    st.session_state.provider = llm.get("provider")
    model = llm.get("model")
    
    th = Toolhouse(provider=llm.get("provider"))

    if st.session_state.bundle != st.session_state.previous_bundle:
        st.session_state.tools = th.get_tools(bundle=st.session_state.bundle)
        st.session_state.previous_bundle = st.session_state.bundle

    th.set_metadata("timezone", -7)
    if st.session_state.user:
        th.set_metadata("id", st.session_state.user)

    # Chat interface
    print_messages(st.session_state.messages, st.session_state.provider)

    # Handle both template selection and regular chat input
    prompt = None


    #if prompt := st.chat_input("What is up?"):
    #    st.session_state.messages.append({"role": "user", "content": prompt})
    #    with st.chat_message("user"):
    #        st.markdown(prompt)
    prompt = st.chat_input("What is up?")
    # Handle template selection
    if hasattr(st.session_state, 'template_submitted') and st.session_state.template_submitted:
        prompt = st.session_state.selected_template
        st.session_state.template_submitted = False
        st.session_state.selected_template = None  # Clear the selection


    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with llm_call(
            provider=st.session_state.llm_choice,
            model=model,
            messages=st.session_state.messages,
            stream=st.session_state.stream,
            tools=st.session_state.tools,
            max_tokens=4096,
            temperature=0.1,
        ) as response:
            completion = append_and_print(response)
            tool_results = th.run_tools(completion, append=False)

            while tool_results:
                st.session_state.messages += tool_results
                with llm_call(
                    provider=st.session_state.llm_choice,
                    model=model,
                    messages=st.session_state.messages,
                    stream=st.session_state.stream,
                    tools=st.session_state.tools,
                    max_tokens=4096,
                    temperature=0.1,
                ) as after_tool_response:
                    after_tool_response = append_and_print(after_tool_response)
                    tool_results = th.run_tools(after_tool_response, append=False)

def main():
    st.set_page_config(
        page_title="Llama Bridge 🦙🌉",
        page_icon="favicon.ico",
        layout="wide"
    )
    
    # Check authentication
    if not check_password():
        return
        
    # Initialize session states
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "stream" not in st.session_state:
        st.session_state.stream = True
    if "provider" not in st.session_state:
        st.session_state.provider = llms.get(next(iter(llms))).get("provider")
    if "bundle" not in st.session_state:
        st.session_state.bundle = "default"
    if "previous_bundle" not in st.session_state:
        st.session_state.previous_bundle = "default"
    if "llm_choice" not in st.session_state:
        st.session_state.llm_choice = next(iter(llms))
    if "user" not in st.session_state:
        st.session_state.user = st.session_state.user_first_name    
    if "selected_template" not in st.session_state:
        st.session_state.selected_template = None
    if "template_submitted" not in st.session_state:
        st.session_state.template_submitted = False    

    # Top navigation
    with st.container():
        # App title on the left
        left_col, right_col = st.columns([2,1])
        with left_col:
            st.title("🦙 Llama Bridge")
        # User profile with university logo on the right
        with right_col:
            render_user_profile()
    

    
    # Main content tabs
    # tab1, tab2, tab3 , tab4 = st.tabs(["Dashboard", "Chat", "Settings","Services"])
    tab1, tab2, tab3  = st.tabs(["Chat", "LLM Settings", "Dashboard"])
    with tab1:
        
        render_chat()
        
    with tab2:
        st.header("⚙️ Settings")
        with st.expander("Advanced Settings", expanded=True):
            llm_choice = render_advanced_settings()
            if llm_choice != st.session_state.llm_choice:
                st.session_state.llm_choice = llm_choice
    #    pass

    with tab3:
        render_student_dashboard()        
        

    #with tab4:
    #    st.header("🏛️ Public Grants Eligibility ")
    #    create_service_cards()



def get_image_as_base64(file_path):
    with open(file_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    return f"data:image/png;base64,{encoded}"


def create_service_cards():
    # Add custom CSS for card styling
    st.markdown("""
    <style>
    .service-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 20px;
        margin: 10px;
        text-align: center;
        background-color: white;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    .service-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .logo-container {
        height: 150px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 15px;
    }
    .service-info {
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Define services
    services = [
        {
            "name": "Poste Italiane",
            "website": "https://www.poste.it",
            "logo_path": get_image_as_base64("assets/Poste.png"),  # Replace with actual logo path
            "description": "Mail and financial services"
        },
        {
            "name": "Intesa Sanpaolo",
            "website": "https://www.intesasanpaolo.com",
            "logo_path":  get_image_as_base64("assets/Banco.png"),  # Replace with actual logo path
            "description": "Banking services"
        },
        {
            "name": "Agenzia delle Entrate",
            "website": "https://www.agenziaentrate.gov.it",
            "logo_path": get_image_as_base64("assets/Entrate.png"),  # Replace with actual logo path
            "description": "Tax services"
        }
    ]

    # Create grid layout
    cols = st.columns(3)

    # Display service cards
    for idx, service in enumerate(services):
        with cols[idx % 3]:
            # Create clickable card
            with st.container():
                st.markdown(f"""
                <div class="service-card">
                    <div class="logo-container">
                        <img src="{service['logo_path']}" alt="{service['name']}" style="max-width: 120px; max-height: 120px;">
                    </div>
                    <div class="service-info">
                        <h3>{service['name']}</h3>
                        <p>{service['description']}</p>
                        <p><a href="{service['website']}" target="_blank">{service['website']}</a></p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Create button
                if st.button(f"Visit {service['name']}", key=service['name']):
                    webbrowser.open_new_tab(service['website'])


if __name__ == "__main__":
    main()

