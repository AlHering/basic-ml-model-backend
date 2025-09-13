# -*- coding: utf-8 -*-
from typing import Any
import streamlit as st
import requests
from src.ui.streamlit_ui.streamlit_components.common_functionality import render_sidebar


def main_page_content() -> None:
    """
    Renders main page content.
    """
    collection_options = [entry["name"] +
                          f"({entry['uuid']})" for entry in st.session_state["CLIENT"].cache["collection"]]
    st.selectbox(
        "Collection",
        key=f"active_collection",
        placeholder="None",
        options=collection_options,
    )
    service_buttons = st.columns(3)
    new_collection_name = service_buttons[0].text_input(
        "New Collection", key="main_new_collection_name")
    new_collection_path = service_buttons[1].text_input(
        "Path", key="main_new_collection_path")
    if service_buttons[2].button("Load default services..."):
        print(f"{new_collection_name} {new_collection_path}")

###################
# Entrypoint
###################


if __name__ == "__main__":
    # Basic metadata
    st.set_page_config(
        page_title="ModelHelper",
        page_icon=":ocean:",
        layout="wide"
    )

    # Page content
    st.title("ModelHelper")

    # Wait for backend and dependencies
    if "SETUP" not in st.session_state or not st.session_state["SETUP"]:
        st.info("System inactive. Please enter a correct backend server API in the sidebar (Local example: 'http://127.0.0.1:7861/api/v1').")
    else:
        main_page_content()

    render_sidebar()
