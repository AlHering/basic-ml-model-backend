# -*- coding: utf-8 -*-
import os
import streamlit as st
from typing import List, Any, Tuple
from copy import deepcopy
import traceback
from src.utility import json_utility
from src.configuration import configuration as cfg
from src.ui.client import Client


DEFAULTS = {}


CONFIGURATION_PARAMETERS = {
    "collection": {
        "name": {"title": "Name", "type": str, "default": None},
        "path": {"title": "Path", "type": str, "default": None},
        "description": {"title": "Description", "type": str, "default": None},
        "config": {"title": "Config", "type": dict, "default": None}
    }
}


AVAILABLE_SERVICES = ["collection"]


def clear_tab_config(tab_key) -> None:
    """
    Clears config session state key.
    :param tab_key: Tab key.
    """
    for key in [key for key in st.session_state if key.startswith(tab_key)]:
        st.session_state.pop(key)


def validate_config(config_type: str, config: dict) -> Tuple[bool | None, str]:
    """
    Validates an configuration.
    :param config_type: Config type.
    :param config: Module configuration.
    :return: True or False and validation report depending on validation success. 
        None and validation report in case of warnings. 
    """
    try:
        return True
    except Exception as ex:
        return False, f"Exception {ex} appeared: {traceback.format_exc()}."


def setup() -> None:
    """
    Sets up and assistant.
    """
    st.session_state["WORKDIR"] = os.path.join(cfg.PATHS.DATA_PATH, "frontend")
    st.session_state["CLIENT"] = Client(
        base_api_url=st.session_state["API_BASE"])


def wait_for_setup() -> None:
    """
    Waits for setup to finish.
    """
    populate_state_cache()
    setup()
    st.session_state["SETUP"] = True
    st.rerun()


def save_cache() -> None:
    """
    Saves config to file system.
    """
    json_utility.save({key: st.session_state["CACHE"][key]
                      for key in cfg.DEFAULT_FRONTEND_CACHE}, cfg.PATHS.FRONTEND_CACHE)


def populate_state_cache() -> None:
    """
    Populates state cache.
    """
    st.session_state["CACHE"] = json_utility.load(
        cfg.PATHS.FRONTEND_CACHE
    ) if os.path.exists(cfg.PATHS.FRONTEND_CACHE) else {}
    for key in cfg.DEFAULT_FRONTEND_CACHE:
        if key not in st.session_state["CACHE"]:
            st.session_state["CACHE"][key] = deepcopy(
                cfg.DEFAULT_FRONTEND_CACHE[key])


def remove_state_cache_element(field_path: List[Any]) -> None:
    """
    Removes a target element from cache.
    :param field_path: Field path for traversing cache to target element.
    """
    target = field_path[-1]
    field_path.remove(target)
    data = st.session_state["CACHE"]
    for key in field_path:
        data = data[key]
    data.pop(target)


def clear_tab_config(tab_key) -> None:
    """
    Clears config session state key.
    :param tab_key: Tab key.
    """
    for key in [key for key in st.session_state if key.startswith(tab_key)]:
        st.session_state.pop(key)
