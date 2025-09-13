# -*- coding: utf-8 -*-
import sys
import os
import streamlit as streamlit
from src.configuration import configuration as cfg


def run_streamlit() -> None:
    """
    Runner function for streamlit interface.
    """
    import streamlit.web.bootstrap as streamlit_bootstrap
    streamlit_bootstrap.run(os.path.join(cfg.PATHS.SOURCE_PATH, "ui",
                            "streamlit_ui", "ModelHelper.py"), is_hello=False, args=[], flag_options=[],)


def run_commandline() -> None:
    """
    Runner function for commandline interface.
    """
    raise NotImplementedError("CLI is not yet implemented.")


if __name__ == "__main__":
    if "--cli" in sys.argv:
        run_commandline()
    else:
        run_streamlit()
