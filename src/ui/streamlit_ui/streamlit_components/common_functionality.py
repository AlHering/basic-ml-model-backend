# -*- coding: utf-8 -*-
from typing import Any
import streamlit as st
import requests
from time import sleep
from src.configuration import configuration as cfg
from src.ui.streamlit_ui.streamlit_components.backend_interaction import wait_for_setup


def reset_api_base():
    """
    Resets current backend connection.
    """
    st.session_state["SETUP"] = False
    st.session_state["available"] = False


def render_sidebar() -> None:
    """
    Renders the sidebar.
    """
    if "available" not in st.session_state:
        st.session_state["available"] = False
    if "SETUP" not in st.session_state:
        st.session_state["SETUP"] = False

    st.sidebar.text_input(
        label="Backend Server",
        key="API_BASE",
        value=f"http://{cfg.BACKEND_HOST}:{cfg.BACKEND_PORT}{cfg.BACKEND_ENDPOINT_BASE}",
        on_change=reset_api_base)
    st.sidebar.divider()
    if not st.session_state["SETUP"]:
        with st.spinner("Waiting for backend connection..."):
            try:
                if requests.get(st.session_state["API_BASE"] + "/status").status_code == 200:
                    st.session_state["available"] = True
                    st.sidebar.info("Backend server is available!")
                else:
                    st.sidebar.error("Backend server is not available!")
            except:
                st.sidebar.error("Backend server is not available!")
            if st.session_state["available"]:
                wait_for_setup()
            else:
                sleep(3.0)
                st.rerun()

    st.sidebar.write("#")
    st.sidebar.write("#")
    show_cache = st.sidebar.selectbox(
        label="Show Cache (Debug Mode)",
        options=["HIDE", "SHOW"])
    if show_cache == "SHOW":
        for key, value in st.session_state.items():
            st.sidebar.write(f"{key}: {value}")
