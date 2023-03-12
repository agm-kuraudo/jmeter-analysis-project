import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as md
from matplotlib.ticker import AutoMinorLocator
import glob
from datetime import datetime
import dataframeops.ops as ops

class ReadJTL :
    def __init__(self):
        pass

    def helloWorld(self):
        print("Hello World")

    def readDir(self, dir):
        '''readDir(string) Accepts a string representing a directory within JMeter results.  
        All JTL files in this directory will be added to one list which will be returned'''

        jtl_files_list= []

        for jtl_file in glob.glob(dir):
            jtl_files_list.append(jtl_file)
        
        if len(jtl_files_list) == 0:
            raise Exception("No files to read!")
        elif len(jtl_files_list)==1:
            return pd.read_csv(jtl_files_list[0], engine='python')
        else:
            return ops.OPs().combineJTLs(jtl_files_list)
    
