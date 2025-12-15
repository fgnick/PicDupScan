#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===============================================================================================

import datetime
import os
import sys
from .path_proc import PathProc
from pathlib import Path

class Logger:
    # public const
    LOG_LV_DEBUG     = 100
    LOG_LV_INFO      = 200
    LOG_LV_NOTICE    = 250
    LOG_LV_WARNING   = 300
    LOG_LV_ERROR     = 400
    LOG_LV_CRITICAL  = 500
    LOG_LV_ALERT     = 550
    LOG_LV_EMERGENCY = 600

    LOG_LV_TEXT = {
        LOG_LV_DEBUG: "DEBUG",
        LOG_LV_INFO: "INFO",
        LOG_LV_NOTICE: "NOTICE",
        LOG_LV_WARNING: "WARNING",
        LOG_LV_ERROR: "ERROR",
        LOG_LV_CRITICAL: "CRITICAL",
        LOG_LV_ALERT: "ALERT",
        LOG_LV_EMERGENCY: "EMERGENCY"
    }
    
    # private default log saving directory path.
    _logDir = ""
    _defaultDatetimeFormat = "%Y-%m-%d %H:%M:%S"
    _print2Terminal = True      # you can turn off it if you don't want it to display on terminal UI
    _rootMarkerName = os.path.basename(sys.argv[0]) # default root marker name is the name of the executing file  resource_path
    _log_file_name = "log"
    _log_callback = None
    
    # to let user to know the class have no constructor
    def __init__(self):
        raise Exception( "You cannot construct Logger class! This is a static class." )

    @staticmethod
    def setCallback(callback):
        Logger._log_callback = callback
    
    @staticmethod
    def setLog( lv_const, msg_str ):
        # if there is no root marker file, the function cannot keep going
        if Logger._rootMarkerName == "" or Logger._rootMarkerName is None:
            raise Exception( "You have to set up a project root marker file name first or keep default at the beginning." )
        
        # get current time for log text content to save
        now_time = datetime.datetime.now()
        # generate text with time string
        msg_str = "[" + now_time.strftime( Logger._defaultDatetimeFormat ) + "] (" + Logger.LOG_LV_TEXT[lv_const] + ")" + msg_str
        
        if Logger._print2Terminal:
            print(msg_str)

        if Logger._log_callback:
            Logger._log_callback(msg_str)
    
        if Logger._logDir == "" or Logger._logDir is None:
            Logger._logDir = os.path.join(PathProc.get_real_base_path(), "log")
            os.makedirs(Logger._logDir, exist_ok=True)

            if Logger._logDir is None or Logger._logDir == "":
                raise Exception( f"Log process cannot find out the project root directory ({Logger._logDir}/{Logger._rootMarkerName}), it needs a marker file to detect to!" )
            Logger._logDir = Logger._logDir + os.sep + Logger._log_file_name + ".log"
            #print( f"Log directory: {Logger._logDir}" )
        
        with open( Logger._logDir + "." + now_time.strftime( "%Y%m%d" ), "a", encoding="utf-8" ) as f:
            f.write( msg_str + "\n" )
            f.flush()
            f.close()
    
    # You better user the method to set up log dir path, _logDir, value. 
    # It can inhance correctness.
    @staticmethod
    def setLogDirPath( path_str: str ):
        if ( not isinstance( path_str, str ) or len( path_str ) == 0 ):
            return False
        p = Path(path_str) # give a path string to Path object
        if p.exists():
            Logger._logDir = path_str
            return True
        else:
            return False
    
    @staticmethod
    def setTerminalDisplay(flg: bool):
        if not isinstance( path_str, bool ):
            return False
        Logger._print2Terminal = flg
        return True
        
    @staticmethod
    def setLogFileName( file_name: str ):
        if ( not isinstance( file_name, str ) or len( file_name ) == 0 ):
            return False
        Logger._log_file_name = file_name
        return True
        
        