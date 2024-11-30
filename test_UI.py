import streamlit as st
import webbrowser
from PIL import Image
import requests
from io import BytesIO

import base64

def get_image_as_base64(file_path):
    with open(file_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
    return f"data:image/png;base64,{encoded}"


def create_service_cards():
    # Set page config
    st.set_page_config(page_title="Italian Services Portal", layout="wide")

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

    # Title
    st.title("Italian Services Portal")
    st.markdown("### Click on any service to visit their website")

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
    create_service_cards()