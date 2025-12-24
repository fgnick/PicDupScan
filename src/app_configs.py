#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===============================================================================================
import os
import logging

from .gn_config import gn_ConfRW
from .settings.pic_constants import PicConst

class AppConfigs:

    _CONFIG_PATH = os.path.join(os.getcwd(), 'config', 'settings.conf')

    _SECTION_CONFIG_SCAN_EXT_SCOPE = "SCAN_EXTENSIONS_SCOPE"
    _SECTION_CONFIG_SCAN_EXT = 'SCAN_EXTENSIONS'



    # TODO: Maybe it needs a method to check all values are valid in the settings.conf file at the beginning of the application.



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
            raise Exception(f"Failed to read app config from config: {e}. Using defaults.")

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
            raise Exception(f"Failed to write app config to config: {e}. Using defaults.")

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
        except Exception as e:
            logging.warning(f"Failed to read app config from config: {e}. Using defaults.")
            return None

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
        except Exception as e:
            logging.warning(f"Failed to write app config to config: {e}. Using defaults.")
            return False

    @staticmethod
    def get_scan_extensions(as_set =False):
        filters = {}
        
        try:
            conf_data = AppConfigs._read_app_config(AppConfigs._SECTION_CONFIG_SCAN_EXT)
            if as_set is True:
                # convert config extensions strings to sets
                filters["Image"] ={
                    ext.strip()
                    for ext in conf_data.get('IMAGE_EXTENSIONS', "").split(",")
                }
                filters["Raw"] = {
                    ext.strip()
                    for ext in conf_data.get('RAW_EXTENSIONS', "").split(",")
                }
                filters["Video"] = {
                    ext.strip()
                    for ext in conf_data.get('VIDEO_EXTENSIONS', "").split(",")
                }
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
            logging.warning(f"Failed to read extensions from config: {e}. Using defaults.")
            return None

    @staticmethod
    def save_scan_extensions(filters):
        if not isinstance(filters, dict):
            raise ValueError("save_scan_extensions filters must be a dictionary")
        if not all(key in filters for key in ["Image", "Raw", "Video"]):
            raise ValueError("save_scan_extensions filters must contain all keys: Image, Raw, Video")

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
        
        is_success = AppConfigs._write_app_config(AppConfigs._SECTION_CONFIG_SCAN_EXT, config_data)
        if is_success is False:
            return False
        return filters

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
        
        