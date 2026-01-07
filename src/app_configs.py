#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===============================================================================================
import os
import logging
from typing import Literal

from .gn_config import gn_ConfRW

class AppConfigs:
    # for config file
    _CONFIG_PATH = os.path.join(os.getcwd(), 'config', 'settings.conf')

    _SECTION_CONFIG_PREFERENCES = "PREFERENCES"
    _SECTION_CONFIG_ENVIRONMENT = "ENVIRONMENT"

    _SECTION_CONFIG_SCAN_EXT_SCOPE = "SCAN_EXTENSIONS_SCOPE"
    _SECTION_CONFIG_SCAN_EXT = 'SCAN_EXTENSIONS'

    # to let user to know the class have no constructor
    def __init__(self):
        raise Exception( "You cannot construct AppConfigs class! This is a static class." )

    # ==================================================================
    # Config file paths and section names
    # ==================================================================
    @staticmethod
    def _read_app_config(section):
        if not isinstance(section, str):
            raise ValueError("_read_app_config section must be a string")

        if not os.path.exists(AppConfigs._CONFIG_PATH):
            raise FileNotFoundError(f"Config file not found: {AppConfigs._CONFIG_PATH}")
        try:
            conf_data = gn_ConfRW.configReader(AppConfigs._CONFIG_PATH, section)
            return conf_data
        except Exception as e:
            logging.error(f"Failed to read {section} from config: {e}")
            raise Exception(f"Failed to read {section} from config: {e}")

    @staticmethod
    def _write_app_config(section, data):
        if not isinstance(section, str):
            raise ValueError("_write_app_config section must be a string")
        if not isinstance(data, dict):
            raise ValueError("_write_app_config data must be a dictionary")

        if not os.path.exists(AppConfigs._CONFIG_PATH):
            raise FileNotFoundError(f"Config file not found: {AppConfigs._CONFIG_PATH}")
        try:
            gn_ConfRW.configWriter(AppConfigs._CONFIG_PATH, section, data)
            return True
        except Exception as e:
            logging.error(f"Failed to write {section}: {data} to config: {e}")
            raise Exception(f"Failed to write {section}: {data} to config: {e}")

    @staticmethod
    def get_scan_scope():
        try:
            conf_data = AppConfigs._read_app_config(AppConfigs._SECTION_CONFIG_SCAN_EXT_SCOPE)
            if not all(key in conf_data for key in ["IMAGE", "RAW", "VIDEO"]):
                raise ValueError("Data must contain all keys: IMAGE, RAW, VIDEO")
            
            for key, value in conf_data.items():
                if value not in {'0', '1', 0, 1}:
                    raise ValueError("Data must be '0' or '1'")
                else:
                    conf_data[key] = bool(int(value))  # Convert to boolean from the beginning

            return conf_data
        except Exception:
            return False

    @staticmethod
    def save_scan_scope(data):
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")
        if not all(key in data for key in ["IMAGE", "RAW", "VIDEO"]):
            raise ValueError("Data must contain all keys: IMAGE, RAW, VIDEO")
        
        for key, value in data.items():
            if not isinstance(value, bool): # Because it is converted to boolean from the beginning
                raise ValueError("Data must contain boolean values")
            else:
                data[key] = str(int(value))  # Convert to integer for writing to config
        try:
            AppConfigs._write_app_config(AppConfigs._SECTION_CONFIG_SCAN_EXT_SCOPE, data)
            return True
        except Exception:
            return False

    @staticmethod
    def get_environment():
        try:
            conf_data = AppConfigs._read_app_config(AppConfigs._SECTION_CONFIG_ENVIRONMENT)
            return conf_data
        except Exception:
            return {}

    @staticmethod
    def get_scan_extensions(return_type: Literal["set", "tuple", "list", "str"] = "str"):
        try:
            conf_data = AppConfigs._read_app_config(AppConfigs._SECTION_CONFIG_SCAN_EXT)
            
            filters = {}
            if return_type in ("set", "tuple", "list"):
                # Common logic: parse to list first
                for key, conf_key in [("Image", 'IMAGE_EXTENSIONS'), ("Raw", 'RAW_EXTENSIONS'), ("Video", 'VIDEO_EXTENSIONS')]:
                    raw_str = conf_data.get(conf_key, "")
                    # Split comma, strip spaces, filter empty
                    ext_list = [ext.strip() for ext in raw_str.split(",") if ext.strip()]
                    
                    if return_type == "set":
                        filters[key] = set(ext_list)
                    elif return_type == "tuple":
                        filters[key] = tuple(ext_list)
                    elif return_type == "list":
                        filters[key] = ext_list
            else:
                # keep config extensions strings
                filters["Image"] = conf_data.get('IMAGE_EXTENSIONS', "")
                filters["Raw"] = conf_data.get('RAW_EXTENSIONS', "")
                filters["Video"] = conf_data.get('VIDEO_EXTENSIONS', "")
            
            # Simple validation to ensure we got something
            if not filters["Image"] or not filters["Raw"] or not filters["Video"]:
                raise ValueError("Missing keys in config file")

            return filters

        except Exception as e:
            logging.error(f"Error in get_scan_extensions: {e}")
            return None

    @staticmethod
    def save_scan_extensions(filters):
        if not isinstance(filters, dict):
            raise ValueError("save scan extensions filters must be a dictionary")
        if not all(key in filters for key in ["Image", "Raw", "Video"]):
            raise ValueError("save scan extensions filters must contain all keys: Image, Raw, Video")

        for key, value in filters.items():
            temp_value = False
            if isinstance(value, str):
                temp_value = AppConfigs.check_extensions_str(value)
            elif isinstance(value, set):
                temp_value = AppConfigs.check_extensions_set(value)
            if temp_value is False:
                return False

            filters[key] = temp_value

        # Map back to config keys
        config_data = {
            'IMAGE_EXTENSIONS': filters.get("Image", ""),
            'RAW_EXTENSIONS': filters.get("Raw", ""),
            'VIDEO_EXTENSIONS': filters.get("Video", "")
        }
        
        try:
            AppConfigs._write_app_config(AppConfigs._SECTION_CONFIG_SCAN_EXT, config_data)
            return True
        except Exception as e:
            logging.error(f"Error saving scan extensions: {e}")
            return False

    @staticmethod
    def check_extensions_str(ext_str):
        if not isinstance(ext_str, str):
            raise ValueError("check_extensions_str ext_str must be a string")

        text = ext_str.strip()
        # Simple validation
        valid_extensions = []
        if text:
            parts = text.split(',')
            for part in parts:
                ext = part.strip()

                if not ext:
                    continue
                
                if not ext.startswith('.'):
                    return False
                
                if len(ext) < 2:
                    return False

                valid_extensions.append(ext)
        return ", ".join(valid_extensions)

    @staticmethod
    def check_extensions_set(ext_set):
        if not isinstance(ext_set, set):
            raise ValueError("check_extensions_set ext_set must be a set")

        valid_extensions = []
        for ext in ext_set:
            if not isinstance(ext, str):
                raise ValueError("check_extensions_set ext_set must be a set of strings")

            if not ext.startswith('.'):
                return False

            if len(ext) < 2:
                return False

            valid_extensions.append(ext)
        return ", ".join(valid_extensions)
        
    @staticmethod
    def get_preferences(name:str):
        if not isinstance(name, str):
            raise ValueError("get preferences name must be a string")

        try:
            conf_data = AppConfigs._read_app_config(AppConfigs._SECTION_CONFIG_PREFERENCES)
            if not name in conf_data:
                raise ValueError("get preferences name does not exist")

            return conf_data[name]
        except Exception as e:
            logging.error(f"Error getting preference {name}: {e}")
            return None

    @staticmethod
    def save_preferences(name:str, value):
        if not isinstance(name, str):
            raise ValueError("save preferences name must be a string")

        # Map to configuration strings
        final_value = str(value)
        if name == "VIEW_SHOW_EXIF_PANEL":
            # Boolean values should be "1" or "0"
            if isinstance(value, bool):
                final_value = "1" if value else "0"
            elif str(value).lower() in ("true", "1", "yes"):
                final_value = "1"
            else:
                final_value = "0"
        else:
            final_value = str(value)
    
        try:
            AppConfigs._write_app_config(AppConfigs._SECTION_CONFIG_PREFERENCES, {name: final_value})
            return True
        except Exception as e:
            logging.error(f"Error saving preference {name}: {e}")
            return False
