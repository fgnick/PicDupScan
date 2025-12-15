#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===============================================================================================

import configparser
from mysql.connector.constants import ClientFlag

class gn_ConfReader:
    @staticmethod
    def db_configReader (filename, section):
        try:
            # Database connection settings
            config = configparser.ConfigParser()
            config.read( filename )
            conf_dict = {
                "user": config.get( section, "user" ),
                "password": config.get( section, "password" ),
                "host": config.get( section, "host" ),
                "port": config.get( section, "port" ),
                "database": config.get( section, "database" ),
                "use_unicode": config.getboolean( section, "use_unicode" ),
                "charset": config.get( section, "charset" ),
                "raise_on_warnings": config.getboolean( section, "raise_on_warnings" )
            }
            # If there are ssl ,put them into directory.
            if (config.has_option(section, "ssl_ca_path") and config.has_option(section, "ssl_cert_path") and config.get( section, "ssl_key_path" )):
                conf_dict["client_flags"] = [ClientFlag.SSL]
                conf_dict["ssl_ca"] = config.get( section, "ssl_ca_path" )
                conf_dict["ssl_cert"] = config.get( section, "ssl_cert_path" )
                conf_dict["ssl_key"] = config.get( section, "ssl_key_path" )
            return conf_dict
        except Exception as error:
            raise Exception ("Database config reader error: %s" % error)
        
    @staticmethod
    def mail_smtp_configReader (filename, section):
        return gn_ConfReader.configReader(filename, section)

    @staticmethod
    def configReader(filename, section):
        try:
            # Database connection settings
            config = configparser.ConfigParser()
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
