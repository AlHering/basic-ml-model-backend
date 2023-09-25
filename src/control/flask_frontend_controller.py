# -*- coding: utf-8 -*-
"""
****************************************************
*           aura-cognitive-architecture            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""

import os
import flask
from typing import List
from multiprocessing import Process
from flask import Flask, render_template, request, url_for, redirect, flash
from flask import session
from flask.logging import default_handler
import hashlib
import traceback
from flask import Blueprint
from src.model.flask_frontend_control.plugins import BlueprintPlugin
from src.model.flask_frontend_control import exceptions
from src.control.plugin_controller import PluginController
from src.configuration import configuration as cfg
from datetime import datetime
import uuid
import logging
logging.basicConfig(level=logging.INFO)


class FlaskFrontendController(object):
    """
    Controller for managing common flask-based applications.
    """

    def __init__(self, app_config: dict, support_login: bool = False) -> None:
        """
        Initiation method for Application Controller objects.
        :param app_config: Application config.
        :param support_login: Flag, geclaring whether to support login functionality.
            Defaults to False.
        """
        self._logger = cfg.LOGGER
        try:
            self._logger.addHandler(default_handler)
        except AttributeError:
            self._logger.warning(
                "Could not add flask logging handler to logger!")
        self._logger.info("Initiating flask frontend ...")
        self.config = app_config
        if "plugins" not in self.config:
            self.config["plugins"] = {}
        self.config["CONTROLLERS"] = {
        }
        self.config["backend"] = {
            "host": cfg.BACKEND_HOST,
            "port": cfg.BACKEND_PORT,
            "api_base_url": f"http://{cfg.BACKEND_HOST}:{cfg.BACKEND_PORT}"
        }

        if not self.check_config:
            raise exceptions.InvalidCFAConfigurationException(self.config)
        self.app = None
        self.support_login = support_login

        self.plugin_controller = PluginController(
            plugin_class_dictionary={"blueprints": BlueprintPlugin},
            plugin_folders=[cfg.PATHS.PLUGIN_PATH],
            supported_types=["blueprints"]
        )

        self._setup_app()
        self._setup_common_routs()
        if self.support_login:
            self._bind_login_manager()

        self._fix_config()

        self.process = Process(target=self._startup_app)

    def _fix_config(self) -> None:
        """
        Internal method for auto-fixing config after app and route creation and configuration.
        """
        for topic_index, topic in enumerate(self.config["menus"]):
            if "#meta" not in self.config["menus"][topic]:
                self.config["menus"][topic]["#meta"] = {
                    "icon": f"lock-icon.png",
                    "type": "lc"
                }
            if "current_topic" not in self.config:
                self.config["current_topic"] = list(
                    self.config["menus"].keys())[0]

    def _setup_app(self) -> None:
        """
        Internal method for setting up app.
        """
        self.app = Flask(__name__,
                         static_folder=cfg.PATHS.FLASK_COMMON_STATIC,
                         template_folder=cfg.PATHS.FLASK_COMMON_TEMPLATES)
        self.app.secret_key = os.environ.get("FLASK_SECRET")

    def _setup_common_routs(self) -> None:
        """
        Internal method for setting up common routs.
        """
        @self.app.route("/", methods=["GET"])
        @self.app.route("/index", methods=["GET", "POST"])
        def index():
            if request.method == "POST":
                data = request.form
                print(data)
            return render_template("index.html", **self.config)

        if self.support_login:
            self._setup_login_routs()

        for blueprint_plugin in self.plugin_controller.plugins.get("blueprints", []):
            self._logger.info(
                f"Importing Blueprints from '{blueprint_plugin}' ...")
            if blueprint_plugin not in self.config["plugins"]:
                self.config["plugins"][blueprint_plugin] = {}
            self.integrate_extension(self.plugin_controller.plugins["blueprints"][blueprint_plugin].get_blueprints(global_config=self.config),
                                     self.plugin_controller.plugins["blueprints"][blueprint_plugin].get_menu())

    def integrate_extension(self, blueprints: List[Blueprint], menus: dict = {}) -> None:
        """
        Method for integrating extensions.
        :param blueprints: Flask Blueprints.
        :param menus: New menu entries.
            Defaults to empty dictionary in which case no menu entries are added.
        """
        for blueprint in blueprints:
            self._logger.info(f"Registering Blueprint '{blueprint}'")
            self.app.register_blueprint(blueprint)
        for topic in menus:
            if topic in self.config["menus"]:
                self.config["menus"][topic].update(menus[topic])
            else:
                self.config["menus"][topic] = menus[topic]

    def check_config(self) -> bool:
        """
        Method for checking configuration on validity.
        :return: True, if profile is valid, else False.
        """
        self._logger.info("Checking configuration ...")
        """
        Menu Subprofile
        """
        menu_profile = self.config["menus"]
        mem = []
        for topic in menu_profile:
            for key in [key for key in menu_profile[topic] if "dropdown" in menu_profile[topic][key]]:
                if menu_profile[topic][key]["href"] not in mem:
                    if menu_profile[topic][key]["href"][0] == "#":
                        mem.append(menu_profile[topic][key]["href"])
                    else:
                        self._logger.warning(
                            f"{menu_profile[topic][key]['href']} must start with '#'.")
                        return False
                else:
                    self._logger.warning(
                        f"{menu_profile[topic][key]['href']} is used as dropdown href multiple times in menu configuration.")
                    return False
        return True

    def _startup_app(self, port: int = 5001, debug: bool = False) -> None:
        """
        Internal method for running app.
        :param port: Port to run app on.
        :param debug: Debugging flag.
        """
        # WebUI(app=self.app, port=port, debug=debug).run()
        self.app.run(debug=debug, port=port)

    def run_app(self) -> None:
        """
        Method for running app.
        """
        self.process.start()
        self.process.join()

    def stop_app(self) -> None:
        """
        Method for stopping app (and setting up a new instance for the case it is needed).
        @Taken from https://stackoverflow.com/questions/23554644/how-do-i-terminate-a-flask-app-thats-running-as-a-service and adjusted.
        """
        self.process.terminate()
        self._setup_app()
        self._setup_common_routs()
