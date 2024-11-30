import streamlit as st
from toolhouse import Toolhouse
from llms import llms, llm_call
from http_exceptions.client_exceptions import NotFoundException
from login import check_password,get_logo_path
import datetime
from st_utils import print_messages, append_and_print
import dotenv
from login import *
import time


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
            st.caption(f"Last login: Today at {datetime.datetime.now().strftime('%H:%M')}")
        
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

def render_dashboard():
    """Render the dashboard components"""
    st.header("📊 Dashboard")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Conversations", value="27", delta="↑ 2")
    with col2:
        st.metric(label="Average Response Time", value="1.2s", delta="-0.1s")
    with col3:
        st.metric(label="Tools Used", value="156", delta="↑ 12")
    
    left_col, right_col = st.columns([2, 1])
    with left_col:
        st.subheader("Usage Analytics")
        st.line_chart({"data": [1, 5, 2, 6, 2, 1]})
    with right_col:
        st.subheader("Recent Activity")
        with st.container():
            st.markdown("""
            - Chat with Climate API Tool
            - Generated report using Data Analysis Tool
            - Updated user preferences
            """)

def render_chat():
    """Render the chat interface"""
    # Sidebar for chat settings
    with st.sidebar:
        t = Toolhouse(provider=st.session_state.provider)
        st.title("💬 Llama Bridge 🦙🌉")
        
        with st.expander("Advanced"):
            llm_choice = st.selectbox("Model", tuple(llms.keys()))
            st.session_state.stream = st.toggle("Stream responses", True)
            user = st.text_input("User", st.session_state.user_first_name)
            st.session_state.bundle = st.text_input("Bundle", "default")
            st.session_state.tools = t.get_tools(bundle=st.session_state.bundle)

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
        st.caption("Powered by Toolhouse & Llama")
        st.caption("Lablab.ai & LlamaImpact Hackathon Product")
        st.markdown('</div>', unsafe_allow_html=True)



    # Main chat area
    st.header("💬 Chat")
    
    # Initialize LLM settings
    llm = llms.get(llm_choice)
    st.session_state.provider = llm.get("provider")
    model = llm.get("model")
    
    th = Toolhouse(provider=llm.get("provider"))

    if st.session_state.bundle != st.session_state.previous_bundle:
        st.session_state.tools = th.get_tools(bundle=st.session_state.bundle)
        st.session_state.previous_bundle = st.session_state.bundle

    th.set_metadata("timezone", -7)
    if user:
        th.set_metadata("id", user)

    # Chat interface
    print_messages(st.session_state.messages, st.session_state.provider)

    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with llm_call(
            provider=llm_choice,
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
                    provider=llm_choice,
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
    
    
    # Top navigation
    with st.container():
        # App title on the left
        left_col, right_col = st.columns([2,1])
        with left_col:
            st.title("🦙 Llama Bridge")
        # User profile with university logo on the right
        with right_col:
            render_user_profile()
    
    st.divider()
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["Dashboard", "Chat", "Settings"])
    
    with tab1:
        render_dashboard()
        
    with tab2:
        render_chat()
    #    pass

    with tab3:
        st.header("⚙️ Settings")
        st.info("Settings page under development")

if __name__ == "__main__":
    main()