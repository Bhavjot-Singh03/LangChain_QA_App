import streamlit as st
from config import config_page
from chat import chat_page

def main():
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv('LangChain/requirements.txt', override=True)

    st.sidebar.title("Navigation")

    # CSS to style the sidebar buttons
    st.sidebar.markdown(
        """
        <style>
        /* Sidebar background color */
        .css-1d391kg {
            background-color: #f8f9fa;
            padding: 10px;
        }
        /* Sidebar button styles */
        .sidebar-button {
            display: block;
            width: 100%;
            padding: 12px;
            font-size: 16px;
            font-weight: 600;
            color: #ffffff;
            background-color: #007bff;
            border: none;
            border-radius: 8px;
            text-align: center;
            cursor: pointer;
            box-sizing: border-box;
            margin-bottom: 12px;
            transition: background-color 0.3s ease, transform 0.2s ease, box-shadow 0.3s ease;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .sidebar-button:hover {
            background-color: #0056b3;
            transform: scale(1.02);
            box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
        }
        .sidebar-button:active {
            background-color: #003d7a;
        }
        .sidebar-button:focus {
            outline: none;
            box-shadow: 0 0 0 2px #0056b3;
        }
        </style>
        """, unsafe_allow_html=True
    )

    # Initialize the page state
    if 'page' not in st.session_state:
        st.session_state.page = "Configuration"

    # Sidebar buttons
    st.sidebar.button("Configuration", key="config", use_container_width=True, on_click=lambda: st.session_state.update(page="Configuration"))
    st.sidebar.button("File QA", key="chat", use_container_width=True, on_click=lambda: st.session_state.update(page="Chat"))

    # Display the selected page
    if st.session_state.page == "Configuration":
        config_page()
    elif st.session_state.page == "Chat":
        chat_page()

if __name__ == "__main__":
    main()
