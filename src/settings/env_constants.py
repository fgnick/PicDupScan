#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===============================================================================================

from dataclasses import dataclass

# ==================================================================
# Maybe you can move something here to a config file.
# And then you can create another function to load the config file.
# ==================================================================

@dataclass(frozen=True)
class EnvConst:
    # Root path
    ROOT_PATH = './'
    
    # Target path
    TARGET_PATH = './target_folder'
    
    # Scan path
    SCAN_PATH = './scan_folder'