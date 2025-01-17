# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Shravan Kumar Copyright 2025
# OSeMOSYS version: OSeMOSYS_PULP_v1

__doc__ = """

========================================================================================================================

    OSeMOSYS-PuLP: A Stochastic Modeling Framework for Long-Term Energy Systems Modeling

========================================================================================================================

    OSeMOSYS-PuLP-HP

    This is the high performance (HP) version of OSeMOSYS-PuLP
    This is a BETA version.

========================================================================================================================

    OSeMOSYS-PuLP: A Stochastic Modeling Framework for Long-Term Energy Systems Modeling

    Please cite this software by using the following reference of the original scientific article:

    Dennis Dreier, Mark Howells, OSeMOSYS-PuLP: A Stochastic Modeling Framework for Long-Term Energy Systems Modeling.
    Energies 2019, 12, 1382, https://doi.org/10.3390/en12071382

    Additional references to be cited for the OSeMOSYS modelling framework (see DOI links for complete references):
    Howells et al. (2011), https://doi.org/10.1016/j.enpol.2011.06.033
    Gardumi et al. (2018), https://doi.org/10.1016/j.esr.2018.03.005

    Other sources:
    OSeMOSYS GitHub: https://github.com/OSeMOSYS/
    OSeMOSYS website: http://www.osemosys.org/
    OpTIMUS community: http://www.optimus.community/

========================================================================================================================

"""
from utils.OSeMOSYS_PULP_functions import *
from utils.OSeMOSYS_PULP_Model import *
import os
import datetime as dt
import logging
import getopt
import sys
import warnings
warnings.filterwarnings("ignore")

def OSeMOSYS_PULP(argv):

    arg_input = ""
    arg_output = ""
    arg_solver = ""
    arg_help = "{0} -i <inputfile.xlsx> -s <solver> -o <output>".format(argv[0])
    
    try:
        opts, args = getopt.getopt(argv[1:], "hi:s:o:", ["help", "input=", 
        "solver=", "output="])
    except:
        print(arg_help)
        sys.exit(2)
    
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(arg_help)  # print the help message
            sys.exit(2)
        elif opt in ("-i", "--input"):
            arg_input = arg
        elif opt in ("-s", "--solver"):
            arg_solver = arg
        elif opt in ("-o", "--output"):
            arg_output = arg

    logging.basicConfig(level=logging.DEBUG)
    logging.info(f"\t{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\tOSeMOSYS-PuLP-HP started.")
    # ----------------------------------------------------------------------------------------------------------------------
    #	SETUP - DATA SOURCES and MONTE CARLO SIMULATION
    # ----------------------------------------------------------------------------------------------------------------------

    # Input data
    inputFile = arg_input  # Update with actual filename
    if 'txt' in str(arg_input):
        inputDir = "data"
    else:
        inputDir = "Input_Data"
    filename = os.path.splitext(os.path.basename(inputFile))[0]  # Get the input file name without extension
    outputDir = os.path.join(".\\Output_Data\\", filename)  # Create a directory path with the same name as the input file
    os.makedirs(outputDir, exist_ok=True)
    solver = arg_solver
    

    if 'txt' in str(arg_input):
        otoole = True
    else:
        otoole = False

    # ----------------------------------------------------------------------------------------------------------------------
    #    LOAD DATA
    # ----------------------------------------------------------------------------------------------------------------------

    res_df = OSeMOSYS_PULP_Model(inputFile, inputDir, solver, otoole)
    #res_df.to_csv('res.csv')
    modelName = inputFile.split('.')[0]
    # CSV
    if arg_output == 'csv':
        outputFileCSV = f"{modelName}_results.csv"
        saveResultsToCSV(res_df, outputDir, outputFileCSV)

    # Excel
    if arg_output == 'excel':
        outputFileExcel = f"{modelName}_results.xlsx"
        saveResultsToExcel(res_df, outputDir, outputFileExcel)

    logging.info(f"\t{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t"
                f"All results are saved now.")
    
if __name__ == "__main__":
    OSeMOSYS_PULP(sys.argv)