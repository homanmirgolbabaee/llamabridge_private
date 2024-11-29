import streamlit as st
from toolhouse import Toolhouse
from llms import llms, llm_call
from http_exceptions.client_exceptions import NotFoundException
from login import check_password
import datetime
from st_utils import print_messages, append_and_print
import dotenv

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

        try:
            available_tools = t.get_tools(bundle=st.session_state.bundle)
        except NotFoundException:
            available_tools = None

        if not available_tools:
            st.subheader("No tools installed")
            st.caption(
                "Go to the [Tool Store](https://app.toolhouse.ai/store) to install your tools, or visit [Bundles](https://app.toolhouse.ai/bundles) to check if the selected bundle exists."
            )
        else:
            st.subheader("Installed tools")
            for tool in available_tools:
                tool_name = tool.get("name")
                if st.session_state.provider != "anthropic":
                    tool_name = tool["function"].get("name")
                st.page_link(f"https://app.toolhouse.ai/store/{tool_name}", label=tool_name)
            st.markdown("---")
            st.caption("Powered by Toolhouse & LLama")
            st.caption("Lablab.ai & Llamaimpact Hackathon Product")

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
        col1, col2, col3 = st.columns([2,1,1])
        with col1:
            st.title("🦙 Llama Bridge")
        with col2:
            st.empty()
        with col3:
            st.write(f"👋 Hello, {st.session_state.user_first_name}!")
            st.caption(f"Last login: Today at {datetime.datetime.now().strftime('%H:%M')}")
    
    st.divider()
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["Dashboard", "Chat", "Settings"])
    
    with tab1:
        render_dashboard()
        
    with tab2:
        render_chat()
    
    with tab3:
        st.header("⚙️ Settings")
        st.info("Settings page under development")

if __name__ == "__main__":
    main()