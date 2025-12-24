#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===============================================================================================

import configparser

class gn_ConfRW:
    
    @staticmethod
    def configReader(filename, section):
        try:
            config = configparser.ConfigParser()
            config.optionxform = str # Preserve case
            config.read( filename )
            conf_dict = {}
            for option in config.options(section):
                conf_dict[option] = config.get(section, option)
            if len(conf_dict) == 0:
                raise Exception ("%s config reader error: section is empty!" % section)
            else:
                return conf_dict
        except Exception as error:
            raise Exception ("%s config reader error: %s" % (section, error))

    @staticmethod
    def configWriter(filename, section, conf_dict):
        try:
            config = configparser.ConfigParser()
            config.optionxform = str # Preserve case
            config.read( filename )
            for option in conf_dict:
                config.set(section, option, conf_dict[option])
            with open(filename, 'w') as configfile:
                config.write(configfile)
        except Exception as error:
            raise Exception ("%s config writer error: %s" % (section, error))
