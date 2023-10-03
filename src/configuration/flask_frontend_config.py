# -*- coding: utf-8 -*-
"""
****************************************************
*           aura-cognitive-architecture            *
*            (c) 2023 Alexander Hering             *
****************************************************
"""
global_config = {
    "page_title": "LLM Tutor",
    "page_icon_path": "img/icons/favicon.ico"
}
endpoint_config = {
    "endpoints": {
        "index": ""
    }
}
# Note that icons are xlink or font-awesome references
menu_config = {
    "menus": {
        "control": {
            "#meta": {
                "icon": "#real-estate-1",
                "type": "xl",
            },
            "Environment": {
                "icon": "#real-estate-1",
                "type": "xl",
                "href": "index"
            },
            "Blueprints": {
                "icon": "#browser-window-1",
                "type": "xl",
                "href": "#docker_control_blueprints_dropdown",
                "dropdown": {
                    "Environments": {
                        "href": "index"
                    },
                    "Agents": {
                        "href": "index"
                    },
                    "Interfaces": {
                        "href": "index"
                    }
                }
            }
        }
    }
}

for dictionary in [endpoint_config, menu_config]:
    global_config.update(dictionary)
