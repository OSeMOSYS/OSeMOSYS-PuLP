from .OSeMOSYS_PULP_functions import *
from .Postprocessing import *
import os
import sys
import datetime as dt
import logging
import numpy as np
import pandas as pd
import pulp
import itertools
import shutil


def OSeMOSYS_PULP_Model(inputFile, inputDir, solver, otoole):
    if solver == 'cplex':
        executable = shutil.which(str(solver))
        #executable = f"{executable_path}/cplex"
        solver = pulp.CPLEX_CMD(path=executable)
    elif solver == 'scip':
        #executable = f"{executable_path}/scip"
        solver = pulp.SCIP_CMD(path=executable)
    elif solver == 'highs':
        #executable = f"{executable_path}/highs"
        solver = pulp.HiGHS_CMD(path=executable)
    elif solver == 'copt':
        solver = COPT_CMD(path=executable)
    elif solver == 'gurobi':
        executable = shutil.which(str((str(solver) + '_cl')))
        #executable = f"{executable_path}/gurobi"
        solver = pulp.GUROBI_CMD(path=executable, threads=8, options=[("Method","1")])
    else:
        solver = None

    ## SETUP

    modelName = inputFile.split('.')[0]
    sheetSets = "SETS"
    sheetParams = "PARAMETERS"
    sheetParamsDefault = "PARAMETERS_DEFAULT"
    sheetMcs = "MCS"
    sheetMcsNum = "MCS_num"

    # ----------------------------------------------------------------------------------------------------------------------
    #    LOAD DATA
    # ----------------------------------------------------------------------------------------------------------------------
    if otoole is False:
        inputPath = os.path.join(inputDir, inputFile)
        sets_df, df, defaults_df, mcs_df, n = loadData(
            inputPath, sheetSets, sheetParams, sheetParamsDefault, sheetMcs, sheetMcsNum)
        parameters_mcs = mcs_df['PARAM'].unique()  # list of parameters to be included in monte carlo simulation
    
            # Ouput mode of operation
        df_omoo =  df.loc[df["PARAM"] == "OutputActivityRatio"].copy(deep=False)
        df_omoo['FUEL'] = np.nan
        df_omoo['PARAM'] = 'OutputModeofoperation'
        df_omoo['VALUE'] = 1
        threshold = int((df_omoo['YEAR'].max() - df_omoo['YEAR'].min() + 1)) * int(df_omoo['MODE_OF_OPERATION'].max())
        for i in df_omoo['TECHNOLOGY'].unique():
        # Create a mask to track cumulative occurrences of the element
            df_omoo['element_count'] = (df_omoo['TECHNOLOGY'] == i).cumsum()

            # Filter to keep rows within the threshold
            df_filtered = df_omoo[~((df_omoo['TECHNOLOGY'] == i) & (df_omoo['element_count'] > threshold))]

           # Drop the helper column
        df_filtered = df_filtered.drop(columns='element_count')
        df_omoo = df_filtered
        techntincludedlist = []
        for i in sets_df['TECHNOLOGY']:
            if i not in df_omoo['TECHNOLOGY'].unique():
                techntincludedlist.append(i)
        dfimoo = df.loc[df["PARAM"] == "InputActivityRatio"].copy(deep=False)
        dfimoo = dfimoo.loc[dfimoo["TECHNOLOGY"].isin(techntincludedlist)].copy(deep=False)
       
        if len(dfimoo)!= 0:
            dfimoo['FUEL'] = np.nan
            dfimoo['PARAM'] = 'OutputModeofoperation'
            dfimoo['VALUE'] = 1
            threshold = int((dfimoo['YEAR'].max() - dfimoo['YEAR'].min() + 1)) * int(dfimoo['MODE_OF_OPERATION'].max())
            for i in df_omoo['TECHNOLOGY'].unique():
            # Create a mask to track cumulative occurrences of the element
                dfimoo['element_count'] = (dfimoo['TECHNOLOGY'] == i).cumsum()

                # Filter to keep rows within the threshold
                df_filtered = dfimoo[~((dfimoo['TECHNOLOGY'] == i) & (dfimoo['element_count'] > threshold))]

                # Drop the helper column
            df_filtered = df_filtered.drop(columns='element_count')
            dfimoo = df_filtered
        df_omoo = pd.concat([df_omoo, dfimoo], axis=0)
        
        df = pd.concat([df, df_omoo], axis=0)
        dr_f,dr_f1, dr_f2 = discount_factor(df=df, sets_df=sets_df, defaults_df=defaults_df)
        df = pd.concat([df, dr_f], ignore_index=True)
        df = pd.concat([df, dr_f1], ignore_index=True)
        df = pd.concat([df, dr_f2], ignore_index=True)
    elif otoole is True:
        AccumulatedAnnualDemand = pd.read_csv(os.path.join(inputDir, "AccumulatedAnnualDemand.csv"))
        AnnualEmissionLimit = pd.read_csv(os.path.join(inputDir,'AnnualEmissionLimit.csv'))
        AnnualExogenousEmission = pd.read_csv(os.path.join(inputDir,'AnnualExogenousEmission.csv'))
        AvailabilityFactor = pd.read_csv(os.path.join(inputDir,'AvailabilityFactor.csv'))
        CapacityFactor = pd.read_csv(os.path.join(inputDir,'CapacityFactor.csv'))
        CapacityOfOneTechnologyUnit = pd.read_csv(os.path.join(inputDir,'CapacityOfOneTechnologyUnit.csv'))
        CapacityToActivityUnit = pd.read_csv(os.path.join(inputDir,'CapacityToActivityUnit.csv'))
        CapitalCost = pd.read_csv(os.path.join(inputDir,'CapitalCost.csv'))
        CapitalCostStorage = pd.read_csv(os.path.join(inputDir,'CapitalCostStorage.csv'))
        Conversionld = pd.read_csv(os.path.join(inputDir,'Conversionld.csv'))
        Conversionlh = pd.read_csv(os.path.join(inputDir,'Conversionlh.csv'))
        Conversionls = pd.read_csv(os.path.join(inputDir,'Conversionls.csv'))
        DAILYTIMEBRACKET = pd.read_csv(os.path.join(inputDir,'DAILYTIMEBRACKET.csv'))
        DaysInDayType = pd.read_csv(os.path.join(inputDir,'DaysInDayType.csv'))
        DaySplit = pd.read_csv(os.path.join(inputDir,'DaySplit.csv'))
        DAYTYPE = pd.read_csv(os.path.join(inputDir,'DAYTYPE.csv'))
        default_values = pd.read_csv(os.path.join(inputDir,'default_values.csv'))
        DepreciationMethod = pd.read_csv(os.path.join(inputDir,'DepreciationMethod.csv'))
        DiscountRate = pd.read_csv(os.path.join(inputDir,'DiscountRate.csv'))
        EMISSION = pd.read_csv(os.path.join(inputDir,'EMISSION.csv'))
        EmissionActivityRatio = pd.read_csv(os.path.join(inputDir,'EmissionActivityRatio.csv'))
        EmissionsPenalty  = pd.read_csv(os.path.join(inputDir,'EmissionsPenalty.csv'))
        FixedCost = pd.read_csv(os.path.join(inputDir,'FixedCost.csv'))
        FUEL = pd.read_csv(os.path.join(inputDir,'FUEL.csv'))
        InputActivityRatio = pd.read_csv(os.path.join(inputDir,'InputActivityRatio.csv'))
        InputToNewCapacityRatio = pd.read_csv(os.path.join(inputDir,'InputActivityRatio.csv'))
        InputToTotalCapacityRatio = pd.read_csv(os.path.join(inputDir,'InputActivityRatio.csv'))
        GIS_Losses = pd.DataFrame()
        MaximumBudget = pd.DataFrame()
        DiscountRateTech = pd.DataFrame()
        DiscountRateSto = pd.DataFrame()
        MinStorageCharge = pd.read_csv(os.path.join(inputDir,'MinStorageCharge.csv'))
        ModelPeriodEmissionLimit = pd.read_csv(os.path.join(inputDir,'ModelPeriodEmissionLimit.csv'))
        ModelPeriodExogenousEmission = pd.read_csv(os.path.join(inputDir,'ModelPeriodExogenousEmission.csv'))
        MODE_OF_OPERATION = pd.read_csv(os.path.join(inputDir,'MODE_OF_OPERATION.csv'))
        OperationalLife = pd.read_csv(os.path.join(inputDir,'OperationalLife.csv'))
        OperationalLifeStorage = pd.read_csv(os.path.join(inputDir,'OperationalLifeStorage.csv'))
        OutputActivityRatio = pd.read_csv(os.path.join(inputDir,'OutputActivityRatio.csv'))
        REGION = pd.read_csv(os.path.join(inputDir,'REGION.csv'))
        REMinProductionTarget = pd.read_csv(os.path.join(inputDir,'REMinProductionTarget.csv'))
        ReserveMargin = pd.read_csv(os.path.join(inputDir,'ReserveMargin.csv'))
        ReserveMarginTagFuel = pd.read_csv(os.path.join(inputDir,'ReserveMarginTagFuel.csv'))
        ReserveMarginTagTechnology = pd.read_csv(os.path.join(inputDir,'ReserveMarginTagTechnology.csv'))
        ResidualCapacity = pd.read_csv(os.path.join(inputDir,'ResidualCapacity.csv'))
        ResidualStorageCapacity = pd.read_csv(os.path.join(inputDir,'ResidualStorageCapacity.csv'))
        RETagFuel = pd.read_csv(os.path.join(inputDir,'RETagFuel.csv'))
        RETagTechnology = pd.read_csv(os.path.join(inputDir,'RETagTechnology.csv'))
        SEASON = pd.read_csv(os.path.join(inputDir,'SEASON.csv'))
        SpecifiedAnnualDemand = pd.read_csv(os.path.join(inputDir,'SpecifiedAnnualDemand.csv'))
        SpecifiedDemandProfile = pd.read_csv(os.path.join(inputDir,'SpecifiedDemandProfile.csv'))
        STORAGE = pd.read_csv(os.path.join(inputDir,'STORAGE.csv'))
        StorageLevelStart = pd.read_csv(os.path.join(inputDir,'StorageLevelStart.csv'))
        StorageMaxChargeRate = pd.read_csv(os.path.join(inputDir,'StorageMaxChargeRate.csv'))
        StorageMaxDischargeRate = pd.read_csv(os.path.join(inputDir,'StorageMaxDischargeRate.csv'))
        TECHNOLOGY = pd.read_csv(os.path.join(inputDir,'TECHNOLOGY.csv'))
        TechnologyFromStorage = pd.read_csv(os.path.join(inputDir,'TechnologyFromStorage.csv'))
        TechnologyToStorage = pd.read_csv(os.path.join(inputDir,'TechnologyToStorage.csv'))
        TIMESLICE = pd.read_csv(os.path.join(inputDir,'TIMESLICE.csv'))
        TotalAnnualMaxCapacity = pd.read_csv(os.path.join(inputDir,'TotalAnnualMaxCapacity.csv'))
        TotalAnnualMaxCapacityInvestment = pd.read_csv(os.path.join(inputDir,'TotalAnnualMaxCapacityInvestment.csv'))
        TotalAnnualMinCapacity = pd.read_csv(os.path.join(inputDir,'TotalAnnualMinCapacity.csv'))
        TotalAnnualMinCapacityInvestment = pd.read_csv(os.path.join(inputDir,'TotalAnnualMinCapacityInvestment.csv'))
        TotalTechnologyAnnualActivityLowerLimit = pd.read_csv(os.path.join(inputDir,'TotalTechnologyAnnualActivityLowerLimit.csv'))
        TotalTechnologyAnnualActivityUpperLimit = pd.read_csv(os.path.join(inputDir,'TotalTechnologyAnnualActivityUpperLimit.csv'))
        TotalTechnologyModelPeriodActivityLowerLimit = pd.read_csv(os.path.join(inputDir,'TotalTechnologyModelPeriodActivityLowerLimit.csv'))
        TotalTechnologyModelPeriodActivityUpperLimit = pd.read_csv(os.path.join(inputDir,'TotalTechnologyModelPeriodActivityUpperLimit.csv'))
        TradeRoute = pd.read_csv(os.path.join(inputDir,'TradeRoute.csv'))
        VariableCost = pd.read_csv(os.path.join(inputDir,'VariableCost.csv'))
        YEAR = pd.read_csv(os.path.join(inputDir,'YEAR.csv'))
        YearSplit = pd.read_csv(os.path.join(inputDir,'YearSplit.csv'))
        YearSplit = YearSplit.sort_values(["TIMESLICE"], ascending=True)
        SpecifiedDemandProfile = SpecifiedDemandProfile.sort_values(['FUEL','TIMESLICE'],ascending=[True,True])
        CapacityFactor = CapacityFactor.sort_values(['TECHNOLOGY','TIMESLICE'],ascending=[True,True])
        AccumulatedAnnualDemand = AccumulatedAnnualDemand[["VALUE","REGION","FUEL","YEAR"]]
        AccumulatedAnnualDemand['VALUE'] = AccumulatedAnnualDemand['VALUE'].round(3)
        AnnualEmissionLimit = AnnualEmissionLimit[["VALUE","REGION","EMISSION","YEAR"]]     
        AnnualExogenousEmission = AnnualExogenousEmission[["VALUE","REGION","EMISSION","YEAR"]] 
        AvailabilityFactor = AvailabilityFactor[["VALUE","REGION","TECHNOLOGY","YEAR"]] 
        CapacityFactor = CapacityFactor[["VALUE","REGION","TIMESLICE","TECHNOLOGY","YEAR"]]
        CapacityOfOneTechnologyUnit = CapacityOfOneTechnologyUnit[["VALUE","REGION","TECHNOLOGY","YEAR"]]
        CapacityToActivityUnit = CapacityToActivityUnit[["VALUE","REGION","TECHNOLOGY"]]
        CapitalCost = CapitalCost[["VALUE","REGION","TECHNOLOGY","YEAR"]]
        CapitalCostStorage = CapitalCostStorage[["VALUE","REGION","STORAGE","YEAR"]]
        Conversionld = Conversionld[["VALUE","DAYTYPE","TIMESLICE"]]
        Conversionlh = Conversionlh[["VALUE","DAILYTIMEBRACKET","TIMESLICE"]]
        Conversionls = Conversionls[["VALUE","SEASON","TIMESLICE"]]
        DaysInDayType = DaysInDayType[["VALUE","DAYTYPE","SEASON","YEAR"]]
        DaySplit = DaySplit[["VALUE","DAILYTIMEBRACKET","YEAR"]]
        DepreciationMethod = DepreciationMethod[["VALUE","REGION"]]
        DiscountRate = DiscountRate[["VALUE","REGION"]]
        EmissionActivityRatio = EmissionActivityRatio[["VALUE","REGION","EMISSION","MODE_OF_OPERATION","TECHNOLOGY","YEAR"]]
        EmissionsPenalty = EmissionsPenalty[["VALUE","REGION","EMISSION","YEAR"]]
        FixedCost = FixedCost[["VALUE","REGION","TECHNOLOGY","YEAR"]]
        InputActivityRatio = InputActivityRatio[["VALUE","REGION","FUEL","MODE_OF_OPERATION","TECHNOLOGY","YEAR"]]
        GIS_Losses['VALUE'] = ''
        GIS_Losses['REGION'] = ''
        GIS_Losses['FUEL'] = ''
        MaximumBudget['VALUE'] = ''
        MaximumBudget['REGION'] = ''
        DiscountRateTech['VALUE'] = ''
        DiscountRateTech['REGION'] = ''
        DiscountRateTech['TECHNOLOGY'] = ''
        DiscountRateSto['VALUE'] = ''
        DiscountRateSto['REGION'] = ''
        DiscountRateSto['STORAGE'] = ''
        MinStorageCharge = MinStorageCharge[["VALUE","REGION","STORAGE","YEAR"]]
        ModelPeriodEmissionLimit = ModelPeriodEmissionLimit[["VALUE","REGION","EMISSION"]]
        ModelPeriodExogenousEmission = ModelPeriodExogenousEmission[["VALUE","REGION","EMISSION"]]
        OperationalLife = OperationalLife[["VALUE","REGION","TECHNOLOGY"]]
        OperationalLifeStorage = OperationalLifeStorage[["VALUE","REGION","STORAGE"]]
        OutputActivityRatio = OutputActivityRatio[["VALUE","REGION","FUEL","MODE_OF_OPERATION","TECHNOLOGY","YEAR"]]
        REMinProductionTarget = REMinProductionTarget[["VALUE","REGION","YEAR"]]
        ReserveMargin = ReserveMargin[["VALUE","REGION","YEAR"]]
        vallist = ReserveMargin["VALUE"].to_list()
        corvallist = []
        for i in vallist:
            if i == 0:
                corvallist.append(1)
            else:
                corvallist.append(i)
        ReserveMargin["VALUE"] = corvallist
        ReserveMarginTagFuel = ReserveMarginTagFuel[["VALUE","REGION","FUEL","YEAR"]]
        ReserveMarginTagTechnology = ReserveMarginTagTechnology[["VALUE","REGION","TECHNOLOGY","YEAR"]]
        ResidualCapacity = ResidualCapacity[["VALUE","REGION","TECHNOLOGY","YEAR"]]
        ResidualStorageCapacity = ResidualStorageCapacity[["VALUE","REGION","STORAGE","YEAR"]]
        RETagFuel = RETagFuel[["VALUE","REGION","FUEL","YEAR"]]
        RETagTechnology = RETagTechnology[["VALUE","REGION","TECHNOLOGY","YEAR"]]      
        SpecifiedAnnualDemand = SpecifiedAnnualDemand[["VALUE","REGION","FUEL","YEAR"]]
        SpecifiedDemandProfile = SpecifiedDemandProfile[["VALUE","REGION","FUEL","TIMESLICE","YEAR"]]
        StorageLevelStart = StorageLevelStart[["VALUE","REGION","STORAGE"]]
        StorageMaxChargeRate = StorageMaxChargeRate[["VALUE","REGION","STORAGE"]]
        StorageMaxChargeRate["YEAR"] = ''
        StorageMaxDischargeRate = StorageMaxDischargeRate[["VALUE","REGION","STORAGE"]]
        StorageMaxDischargeRate["YEAR"] = ''
        TechnologyFromStorage = TechnologyFromStorage[["VALUE","REGION","MODE_OF_OPERATION","STORAGE","TECHNOLOGY"]]
        TechnologyToStorage = TechnologyToStorage[["VALUE","REGION","MODE_OF_OPERATION","STORAGE","TECHNOLOGY"]]
        TotalAnnualMaxCapacity = TotalAnnualMaxCapacity[["VALUE","REGION","TECHNOLOGY","YEAR"]]  
        TotalAnnualMaxCapacityInvestment = TotalAnnualMaxCapacityInvestment[["VALUE","REGION","TECHNOLOGY","YEAR"]]
        TotalAnnualMinCapacity = TotalAnnualMinCapacity[["VALUE","REGION","TECHNOLOGY","YEAR"]]    
        TotalAnnualMinCapacityInvestment = TotalAnnualMinCapacityInvestment[["VALUE","REGION","TECHNOLOGY","YEAR"]]
        TotalTechnologyAnnualActivityLowerLimit = TotalTechnologyAnnualActivityLowerLimit[["VALUE","REGION","TECHNOLOGY","YEAR"]]
        TotalTechnologyAnnualActivityUpperLimit = TotalTechnologyAnnualActivityUpperLimit[["VALUE","REGION","TECHNOLOGY","YEAR"]]
        TotalTechnologyModelPeriodActivityLowerLimit = TotalTechnologyModelPeriodActivityLowerLimit[["VALUE","REGION","TECHNOLOGY"]]
        TotalTechnologyModelPeriodActivityUpperLimit = TotalTechnologyModelPeriodActivityUpperLimit[["VALUE","REGION","TECHNOLOGY"]]
        TradeRoute["REGION2"] = ''
        TradeRoute = TradeRoute[["VALUE","REGION","REGION2","FUEL","YEAR"]]
        VariableCost = VariableCost[["VALUE","REGION","MODE_OF_OPERATION","TECHNOLOGY","YEAR"]]
        YearSplit = YearSplit[["VALUE","TIMESLICE","YEAR"]]

        OutputModeofoperation =  OutputActivityRatio[OutputActivityRatio['VALUE']>0].copy(deep=False)
        del OutputModeofoperation['FUEL']
        n = 0
        parameters_mcs = {}
    logging.info(f"\t{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t"
                f"Data is loaded.")
    # ----------------------------------------------------------------------------------------------------------------------
    #    SETS
    # ----------------------------------------------------------------------------------------------------------------------
    if otoole is False:
        YEAR = createTuple(sets_df, 'YEAR')
        TECHNOLOGY = createTuple(sets_df, 'TECHNOLOGY')
        TIMESLICE = createTuple(sets_df, 'TIMESLICE')
        FUEL = createTuple(sets_df, 'FUEL')
        EMISSION = createTuple(sets_df, 'EMISSION')
        MODE_OF_OPERATION = createTuple(sets_df, 'MODE_OF_OPERATION')
        REGION = createTuple(sets_df, 'REGION')
        REGION2 = createTuple(sets_df, 'REGION2')
        SEASON = createTuple(sets_df, 'SEASON')
        DAYTYPE = createTuple(sets_df, 'DAYTYPE')
        DAILYTIMEBRACKET = createTuple(sets_df, 'DAILYTIMEBRACKET')
        FLEXIBLEDEMANDTYPE = createTuple(sets_df, 'FLEXIBLEDEMANDTYPE')
        STORAGE = createTuple(sets_df, 'STORAGE')
    
    elif otoole is True:
        sets_df = {}
        sets_df['REGION'] = REGION['VALUE']
        sets_df['REGION2'] = ""
        sets_df['DAYTYPE'] = DAYTYPE['VALUE']
        sets_df['EMISSION'] = EMISSION['VALUE']
        sets_df['FUEL'] = FUEL['VALUE']
        sets_df['DAILYTIMEBRACKET'] = DAILYTIMEBRACKET['VALUE']
        sets_df['SEASON'] = SEASON['VALUE']
        sets_df['TIMESLICE'] = TIMESLICE['VALUE']
        sets_df['MODE_OF_OPERATION'] = MODE_OF_OPERATION['VALUE']
        sets_df['STORAGE'] = STORAGE['VALUE']
        sets_df['TECHNOLOGY'] = TECHNOLOGY['VALUE']
        sets_df['YEAR'] = YEAR['VALUE']
        sets_df['FLEXIBLEDEMANDTYPE'] = " "
            
        YEAR = createTupleOT(sets_df, 'YEAR')
        TECHNOLOGY = createTupleOT(sets_df, 'TECHNOLOGY')
        TIMESLICE = createTupleOT(sets_df, 'TIMESLICE')
        FUEL = createTupleOT(sets_df, 'FUEL')
        EMISSION = createTupleOT(sets_df, 'EMISSION')
        MODE_OF_OPERATION = createTupleOT(sets_df, 'MODE_OF_OPERATION')
        REGION = createTupleOT(sets_df, 'REGION')
        REGION2 = createTupleOT(sets_df, 'REGION2')
        SEASON = createTupleOT(sets_df, 'SEASON')
        DAYTYPE = createTupleOT(sets_df, 'DAYTYPE')
        DAILYTIMEBRACKET = createTupleOT(sets_df, 'DAILYTIMEBRACKET')
        FLEXIBLEDEMANDTYPE = createTupleOT(sets_df, 'FLEXIBLEDEMANDTYPE')
        STORAGE = createTupleOT(sets_df, 'STORAGE')
   
    logging.info(f"\t{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t"
                 f"Sets are created.")
        # ----------------------------------------------------------------------------------------------------------------------
        #    PARAMETERS AND DATA
        # ----------------------------------------------------------------------------------------------------------------------
        # Dictionaries for parameters
    if otoole is False:
        df['INDEX'] = [ci([str(r), str(rr), str(ld), str(e), str(f), str(lh), str(ls), str(l), str(s), str(m), str(t), str(y)])\
                        .replace('nan-', '').replace('<NA>-', '').replace('-nan', '').replace('-<NA>', '')
                    for r, rr, ld, e, f, lh, ls, l, s, m, t, y in
                        zip(df.REGION, df.REGION2, df.DAYTYPE, df.EMISSION, df.FUEL, df.DAILYTIMEBRACKET, df.SEASON,\
                            df.TIMESLICE, df.STORAGE, df.MODE_OF_OPERATION, df.TECHNOLOGY, df.YEAR)]
        
        AccumulatedAnnualDemand = createParameter(df, 'AccumulatedAnnualDemand')
        AnnualEmissionLimit = createParameter(df, 'AnnualEmissionLimit')
        AnnualExogenousEmission = createParameter(df, 'AnnualExogenousEmission')
        AvailabilityFactor = createParameter(df, 'AvailabilityFactor')
        CapacityFactor = createParameter(df, 'CapacityFactor')
        CapacityOfOneTechnologyUnit = createParameter(df, 'CapacityOfOneTechnologyUnit')
        CapacityToActivityUnit = createParameter(df, 'CapacityToActivityUnit')
        CapitalCost = createParameter(df, 'CapitalCost')
        CapitalCostStorage = createParameter(df, 'CapitalCostStorage')
        Conversionld = createParameter(df, 'Conversionld')
        Conversionlh = createParameter(df, 'Conversionlh')
        Conversionls = createParameter(df, 'Conversionls')
        DaySplit = createParameter(df, 'DaySplit')
        DaysInDayType = createParameter(df, 'DaysInDayType')
        DepreciationMethod = createParameter(df, 'DepreciationMethod')
        DiscountRateTech = createParameter(df, 'DiscountRateTech')
        DiscountRateSto = createParameter(df, 'DiscountRateSto')
        DiscountRate = createParameter(df, 'DiscountRate')
        DiscountFactor = createParameter(df, 'DiscountFactor')
        DiscountFactorMid = createParameter(df, 'DiscountFactorMid')
        DiscountFactorIndProd = createParameter(df, 'DiscountFactorIndProd')
        EmissionActivityRatio = createParameter(df, 'EmissionActivityRatio')
        EmissionsPenalty = createParameter(df, 'EmissionsPenalty')
        FixedCost = createParameter(df, 'FixedCost')
        GIS_Losses = createParameter(df, 'GIS_Losses')
        InputActivityRatio = createParameter(df, 'InputActivityRatio')
        InputToNewCapacityRatio = createParameter(df, 'InputToNewCapacityRatio')
        InputToTotalCapacityRatio = createParameter(df, 'InputToTotalCapacityRatio')
        MaximumBudget = createParameter(df, 'MaximumBudget')
        MinStorageCharge = createParameter(df, 'MinStorageCharge')
        ModelPeriodEmissionLimit = createParameter(df, 'ModelPeriodEmissionLimit')
        ModelPeriodExogenousEmission = createParameter(df, 'ModelPeriodExogenousEmission')
        OperationalLife = createParameter(df, 'OperationalLife')
        OperationalLifeStorage = createParameter(df, 'OperationalLifeStorage')
        OutputActivityRatio = createParameter(df, 'OutputActivityRatio')
        OutputModeofoperation = createParameter(df, 'OutputModeofoperation')
        REMinProductionTarget = createParameter(df, 'REMinProductionTarget')
        RETagFuel = createParameter(df, 'RETagFuel')
        RETagTechnology = createParameter(df, 'RETagTechnology')
        ReserveMargin = createParameter(df, 'ReserveMargin')
        ReserveMarginTagFuel = createParameter(df, 'ReserveMarginTagFuel')
        ReserveMarginTagTechnology = createParameter(df, 'ReserveMarginTagTechnology')
        ResidualCapacity = createParameter(df, 'ResidualCapacity')
        ResidualStorageCapacity = createParameter(df, 'ResidualStorageCapacity')
        SpecifiedAnnualDemand = createParameter(df, 'SpecifiedAnnualDemand')
        SpecifiedDemandProfile = createParameter(df, 'SpecifiedDemandProfile')
        StorageMaxChargeRate = createParameter(df, 'StorageMaxChargeRate')
        StorageMaxDischargeRate = createParameter(df, 'StorageMaxDischargeRate')
        StorageMaxCapacity = createParameter(df, 'StorageMaxCapacity')
        StorageLevelStart = createParameter(df, 'StorageLevelStart')
        StorageL2D = createParameter(df, 'StorageL2D')
        StorageUvalue = createParameter(df, 'StorageUvalue')
        StorageFlowTemperature = createParameter(df, 'StorageFlowTemperature')
        StorageReturnTemperature = createParameter(df, 'StorageReturnTemperature')
        StorageAmbientTemperature = createParameter(df, 'StorageAmbientTemperature')
        Storagetagheating = createParameter(df, 'Storagetagheating')
        Storagetagcooling = createParameter(df, 'Storagetagcooling')
        TechWithCapacityNeededToMeetPeakTS = createParameter(df, 'TechWithCapacityNeededToMeetPeakTS')
        TechnologyFromStorage = createParameter(df, 'TechnologyFromStorage')
        TechnologyToStorage = createParameter(df, 'TechnologyToStorage')
        TotalAnnualMaxCapacity = createParameter(df, 'TotalAnnualMaxCapacity')
        TotalAnnualMaxCapacityInvestment = createParameter(df, 'TotalAnnualMaxCapacityInvestment')
        TotalAnnualMinCapacity = createParameter(df, 'TotalAnnualMinCapacity')
        TotalAnnualMinCapacityInvestment = createParameter(df, 'TotalAnnualMinCapacityInvestment')
        TotalTechnologyAnnualActivityLowerLimit = createParameter(df, 'TotalTechnologyAnnualActivityLowerLimit')
        TotalTechnologyAnnualActivityUpperLimit = createParameter(df, 'TotalTechnologyAnnualActivityUpperLimit')
        TechnologyActivityDecreaseByModeLimit = createParameter(df, 'TechnologyActivityDecreaseByModeLimit')
        TechnologyActivityIncreaseByModeLimit = createParameter(df, 'TechnologyActivityIncreaseByModeLimit')
        TotalTechnologyModelPeriodActivityLowerLimit = createParameter(df, 'TotalTechnologyModelPeriodActivityLowerLimit')
        TotalTechnologyModelPeriodActivityUpperLimit = createParameter(df, 'TotalTechnologyModelPeriodActivityUpperLimit')
        TradeRoute = createParameter(df, 'TradeRoute')
        VariableCost = createParameter(df, 'VariableCost')
        YearSplit = createParameter(df, 'YearSplit')

        # Default values for parameters
        dflt = defaults_df.set_index('PARAM').to_dict()['VALUE']

    elif otoole is True:
        AccumulatedAnnualDemand = createParameterOT(AccumulatedAnnualDemand, 'AccumulatedAnnualDemand')
        AnnualEmissionLimit = createParameterOT(AnnualEmissionLimit, 'AnnualEmissionLimit')
        AnnualExogenousEmission = createParameterOT(AnnualExogenousEmission, 'AnnualExogenousEmission')
        AvailabilityFactor = createParameterOT(AvailabilityFactor, 'AvailabilityFactor')
        CapacityFactor = createParameterOT(CapacityFactor, 'CapacityFactor')
        CapacityOfOneTechnologyUnit = createParameterOT(CapacityOfOneTechnologyUnit, 'CapacityOfOneTechnologyUnit')
        CapacityToActivityUnit = createParameterOT(CapacityToActivityUnit, 'CapacityToActivityUnit')
        CapitalCost = createParameterOT(CapitalCost, 'CapitalCost')
        CapitalCostStorage = createParameterOT(CapitalCostStorage, 'CapitalCostStorage')
        Conversionld = createParameterOT(Conversionld, 'Conversionld')
        Conversionlh = createParameterOT(Conversionlh, 'Conversionlh')
        Conversionls = createParameterOT(Conversionls, 'Conversionls')
        DaySplit = createParameterOT(DaySplit, 'DaySplit')
        DaysInDayType = createParameterOT(DaysInDayType, 'DaysInDayType')
        DepreciationMethod = createParameterOT(DepreciationMethod, 'DepreciationMethod')
        DiscountRate = createParameterOT(DiscountRate, 'DiscountRate')
        EmissionActivityRatio = createParameterOT(EmissionActivityRatio, 'EmissionActivityRatio')
        EmissionsPenalty = createParameterOT(EmissionsPenalty, 'EmissionsPenalty')
        FixedCost = createParameterOT(FixedCost, 'FixedCost')
        InputActivityRatio = createParameterOT(InputActivityRatio, 'InputActivityRatio')
        GIS_Losses = createParameterOT(GIS_Losses, 'GIS_Losses')
        MinStorageCharge = createParameterOT(MinStorageCharge, 'MinStorageCharge')
        ModelPeriodEmissionLimit = createParameterOT(ModelPeriodEmissionLimit, 'ModelPeriodEmissionLimit')
        ModelPeriodExogenousEmission = createParameterOT(ModelPeriodExogenousEmission, 'ModelPeriodExogenousEmission')
        OperationalLife = createParameterOT(OperationalLife, 'OperationalLife')
        OperationalLifeStorage = createParameterOT(OperationalLifeStorage, 'OperationalLifeStorage')
        OutputActivityRatio = createParameterOT(OutputActivityRatio, 'OutputActivityRatio')
        OutputModeofoperation = createParameterOT(OutputModeofoperation, 'OutputModeofoperation')
        REMinProductionTarget = createParameterOT(REMinProductionTarget, 'REMinProductionTarget')
        RETagFuel = createParameterOT(RETagFuel, 'RETagFuel')
        RETagTechnology = createParameterOT(RETagTechnology, 'RETagTechnology')
        ReserveMargin = createParameterOT(ReserveMargin, 'ReserveMargin')
        ReserveMarginTagFuel = createParameterOT(ReserveMarginTagFuel, 'ReserveMarginTagFuel')
        ReserveMarginTagTechnology = createParameterOT(ReserveMarginTagTechnology, 'ReserveMarginTagTechnology')
        ResidualCapacity = createParameterOT(ResidualCapacity, 'ResidualCapacity')
        ResidualStorageCapacity = createParameterOT(ResidualStorageCapacity, 'ResidualStorageCapacity')
        SpecifiedAnnualDemand = createParameterOT(SpecifiedAnnualDemand, 'SpecifiedAnnualDemand')
        SpecifiedDemandProfile = createParameterOT(SpecifiedDemandProfile, 'SpecifiedDemandProfile')
        StorageMaxChargeRate = createParameterOT(StorageMaxChargeRate, 'StorageMaxChargeRate')
        StorageMaxDischargeRate= createParameterOT(StorageMaxDischargeRate, 'StorageMaxDischargeRate')
        #StorageMaxCapacity = createParameterOT(StorageMaxCapacity, 'StorageMaxCapacity')
        StorageLevelStart = createParameterOT(StorageLevelStart, 'StorageLevelStart')
        #TechWithCapacityNeededToMeetPeakTS = createParameterOT(TechWithCapacityNeededToMeetPeakTS, 'TechWithCapacityNeededToMeetPeakTS')
        TechnologyFromStorage = createParameterOT(TechnologyFromStorage, 'TechnologyFromStorage')
        TechnologyToStorage = createParameterOT(TechnologyToStorage, 'TechnologyToStorage')
        TotalAnnualMaxCapacity = createParameterOT(TotalAnnualMaxCapacity, 'TotalAnnualMaxCapacity')
        TotalAnnualMaxCapacityInvestment = createParameterOT(TotalAnnualMaxCapacityInvestment, 'TotalAnnualMaxCapacityInvestment')
        TotalAnnualMinCapacity = createParameterOT(TotalAnnualMinCapacity, 'TotalAnnualMinCapacity')
        TotalAnnualMinCapacityInvestment = createParameterOT(TotalAnnualMinCapacityInvestment, 'TotalAnnualMinCapacityInvestment')
        TotalTechnologyAnnualActivityLowerLimit = createParameterOT(TotalTechnologyAnnualActivityLowerLimit, 'TotalTechnologyAnnualActivityLowerLimit')
        TotalTechnologyAnnualActivityUpperLimit = createParameterOT(TotalTechnologyAnnualActivityUpperLimit, 'TotalTechnologyAnnualActivityUpperLimit')
        TotalTechnologyModelPeriodActivityLowerLimit = createParameterOT(TotalTechnologyModelPeriodActivityLowerLimit, 'TotalTechnologyModelPeriodActivityLowerLimit')
        TotalTechnologyModelPeriodActivityUpperLimit = createParameterOT(TotalTechnologyModelPeriodActivityUpperLimit, 'TotalTechnologyModelPeriodActivityUpperLimit')
        TradeRoute = createParameterOT(TradeRoute, 'TradeRoute')
        VariableCost = createParameterOT(VariableCost, 'VariableCost')
        YearSplit = createParameterOT(YearSplit, 'YearSplit')

        dflt = default_values.set_index('name').to_dict()['default_value']

    logging.info(f"\t{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t"
                f"Parameters are created.")

    # # PREPROCESS#

    # #rflmty#
    # rflmtypre = ()
    # A_r = df[df['PARAM'].isin(['InputActivityRatio', 'OutputActivityRatio'])] # df with the parameter Input or output AR
    # A_r_i = list(A_r['INDEX'])           # list of the INDEX, contains the current techs and In or Out AR
    # A_r_i_t = []
    # for j in A_r_i:
    #     for i in range(1,len(TIMESLICE)):
    #         aux = A_r_i[1].split('-')
    #         A_r_i_t.append(str((str(aux[0]) + '-' + str(aux[1]) + '-' + str(i) + '-' +  str(aux[2]) + '-' +  str(aux[3]) + '-' +  str(aux[4]))))
    # for i in range(0, len(A_r_i_t)):
    #     aux = A_r_i_t[i].split('-')
    #     rflmtypre = (*rflmtypre, tuple(aux))

    # ----------------------------------------------------------------------------------------------------------------------
    #    PERMUTATION OF SETS
    # ----------------------------------------------------------------------------------------------------------------------

    # Global sets
    # REGION (no permutation needed for REGION)
    REGION_FUEL_TIMESLICE_YEAR = permutateSets([REGION, FUEL, TIMESLICE, YEAR])
    REGION_TECHNOLOGY_YEAR = permutateSets([REGION, TECHNOLOGY, YEAR])
    REGION_TIMESLICE_TECHNOLOGY_YEAR = permutateSets([REGION, TIMESLICE, TECHNOLOGY, YEAR])
    REGION_REGION2_FUEL_TIMESLICE_YEAR = permutateSets([REGION, REGION2, FUEL, TIMESLICE, YEAR])
    REGION_FUEL_YEAR = permutateSets([REGION, FUEL, YEAR])
    REGION_REGION2_FUEL_YEAR = permutateSets([REGION, REGION2, FUEL, YEAR])
    REGION_STORAGE = permutateSets([REGION, STORAGE])
    REGION_STORAGE_YEAR = permutateSets([REGION, STORAGE, YEAR])
    REGION_STORAGE_TIMESLICE_YEAR = permutateSets([REGION, STORAGE, TIMESLICE, YEAR])
    REGION_YEAR = permutateSets([REGION, YEAR])
    REGION_TECHNOLOGY = permutateSets([REGION, TECHNOLOGY])
    REGION_TIMESLICE_YEAR = permutateSets([REGION, TIMESLICE, YEAR])
    REGION_FUEL_TECHNOLOGY_YEAR = permutateSets([REGION, FUEL, TECHNOLOGY, YEAR])
    REGION_MODE_OF_OPERATION_TECHNOLOGY_YEAR = permutateSets([REGION, MODE_OF_OPERATION, TECHNOLOGY, YEAR])
    REGION_EMISSION_TECHNOLOGY_YEAR = permutateSets([REGION, EMISSION, TECHNOLOGY, YEAR])
    REGION_EMISSION_YEAR = permutateSets([REGION, EMISSION, YEAR])
    REGION_EMISSION = permutateSets([REGION, EMISSION])
    # Local sets within equations
    #MODE_OF_OPERATION_YEAR = permutateSets([MODE_OF_OPERATION, YEAR])
    TIMESLICE_MODE_OF_OPERATION_TECHNOLOGY = permutateSets([TIMESLICE, MODE_OF_OPERATION, TECHNOLOGY])
    TIMESLICE_MODE_OF_OPERATION_TECHNOLOGY_YEAR = permutateSets([TIMESLICE, MODE_OF_OPERATION, TECHNOLOGY, YEAR])
    FUEL_TECHNOLOGY = permutateSets([FUEL, TECHNOLOGY])
    FUEL_TIMESLICE = permutateSets([FUEL, TIMESLICE])
    MODE_OF_OPERATION_TECHNOLOGY = permutateSets([ MODE_OF_OPERATION, TECHNOLOGY])
    TIMESLICE_YEAR = permutateSets([ TIMESLICE, YEAR])
    TIMESLICE_MODE_OF_OPERATION = permutateSets([TIMESLICE, MODE_OF_OPERATION])
    FUEL_TIMESLICE_MODE_OF_OPERATION_TECHNOLOGY  = permutateSets([FUEL, TIMESLICE, MODE_OF_OPERATION, TECHNOLOGY])
    EMISSION_TIMESLICE_MODE_OF_OPERATION = permutateSets([EMISSION, TIMESLICE, MODE_OF_OPERATION])
    TIMESLICE_MODE_OF_OPERATION_YEAR = permutateSets([TIMESLICE, MODE_OF_OPERATION, YEAR])
    FUEL_MODE_OF_OPERATION_TECHNOLOGY = permutateSets([FUEL, MODE_OF_OPERATION, TECHNOLOGY])
    TECHNOLOGY_YEAR = permutateSets([TECHNOLOGY, YEAR])
    # ----------------------------------------------------------------------------------------------------------------------
    #    MODEL CONSTRUCTION
    # ----------------------------------------------------------------------------------------------------------------------

    i = 0
    while i <= n:

    # ====  Simulation loops  ====

        logging.info(f"\t{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t"
                    f"Model run: {i}")

        # ------------------------------------------------------------------------------------------------------------------
        #    MODEL INITIALIZATION
        # ------------------------------------------------------------------------------------------------------------------

        model = pulp.LpProblem(modelName, pulp.LpMinimize)

        # ------------------------------------------------------------------------------------------------------------------
        #    MODEL VARIABLES
        # ------------------------------------------------------------------------------------------------------------------

        variables = {

            # ====  Net Present Cost  ====

            # 'Cost'

            # ====  Demands  ====

        'Demand': {'sets': [REGION, FUEL, TIMESLICE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'f', 'l', 'y']},

            # ====  Storage  ====

        'StorageLevelYearStart': {'sets': [REGION, STORAGE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 's', 'y']},
        'StorageLevelYearFinish': {'StorageLevelYearFinish': {'sets': [REGION, STORAGE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 's', 'y']},'sets': [REGION, STORAGE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 's', 'y']},
        'StorageLevelTimesliceStart': {'sets': [REGION, STORAGE, TIMESLICE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 's', 'l', 'y']},
        'StorageLosses': {'sets': [REGION, STORAGE, TIMESLICE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 's', 'l', 'y']},
        'StorageLowerLimit': {'sets': [REGION, STORAGE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 's', 'y']},
        'StorageUpperLimit': {'sets': [REGION, STORAGE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 's', 'y']},
        'StorageLossesheating': {'sets': [REGION, STORAGE, TIMESLICE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 's', 'l', 'y']},
        'StorageLossescooling': {'sets': [REGION, STORAGE, TIMESLICE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 's', 'l', 'y']},
        'StorageSurfaceArea': {'sets': [REGION, STORAGE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 's', 'y']},
        'NewStorageCapacity': {'sets': [REGION, STORAGE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 's', 'y']},
        'SalvageValueStorage': {'sets': [REGION, STORAGE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 's', 'y']},
        'TotalDiscountedStorageCost': {'sets': [REGION, STORAGE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 's', 'y']},
            # ====  Capacity Variables  ====

        'NumberOfNewTechnologyUnits': {'sets': [REGION, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Integer', 'indices': ['r', 't', 'y']},
        'NewCapacity': {'sets': [REGION, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 't', 'y']},
        
            # ====  Activity Variables  ====

        'RateOfActivity': {'sets': [REGION, TIMESLICE, MODE_OF_OPERATION, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'l', 'm', 't', 'y']},
        'TotalTechnologyModelPeriodActivity': {'sets': [REGION, TECHNOLOGY], 'lb': None, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 't']},
        'ProductionByTechnologyAnnual': {'sets': [REGION, FUEL, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'f', 't', 'y']},
        'Production': {'sets': [REGION, FUEL, TIMESLICE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'f', 'l', 'y']},
        'Use': {'sets': [REGION, FUEL, TIMESLICE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'f', 'l', 'y']},
        'Trade': {'sets': [REGION, REGION2, FUEL, TIMESLICE, YEAR], 'lb': None, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'rr', 'f', 'l', 'y']},
        'TradeAnnual': {'sets': [REGION, REGION2, FUEL, YEAR], 'lb': None, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'rr', 'f', 'y']},
        'ProductionAnnual': {'sets': [REGION, FUEL, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'f', 'y']},
        'UseAnnual': {'sets': [REGION, FUEL, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'f', 'y']},
        'InputToNewCapacity': {'sets': [REGION, FUEL, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'f', 't', 'y']},
        'InputToTotalCapacity': {'sets': [REGION, FUEL, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'f', 't', 'y']},
            # ====  Costing Variables  ====

        'CapitalInvestment': {'sets': [REGION, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 't', 'y']},
        'DiscountedCapitalInvestment': {'sets': [REGION, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 't', 'y']},
        'DiscountedCapitalInvestmentByTechnology': {'sets': [REGION, TECHNOLOGY], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 't']},
        'SalvageValue': {'sets': [REGION, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 't', 'y']},
        'DiscountedSalvageValue': {'sets': [REGION, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 't', 'y']},
        'OperatingCost': {'sets': [REGION, TECHNOLOGY, YEAR], 'lb': None, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 't', 'y']},
        'DiscountedOperatingCost': {'sets': [REGION, TECHNOLOGY, YEAR], 'lb': None, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 't', 'y']},
        'AnnualVariableOperatingCost': {'sets': [REGION, TECHNOLOGY, YEAR], 'lb': None, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 't', 'y']},
        'AnnualFixedOperatingCost': {'sets': [REGION, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 't', 'y']},
        'TotalDiscountedCostByTechnology': {'sets': [REGION, TECHNOLOGY, YEAR], 'lb': None, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 't', 'y']},
        'TotalDiscountedCost': {'sets': [REGION, YEAR], 'lb': None, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'y']},
        'ModelPeriodCostByRegion': {'sets': [REGION], 'lb': None, 'ub': None, 'cat': 'Continuous', 'indices': ['r']},

            # ====  Reserve Margin  ====

        'TotalCapacityInReserveMargin': {'sets': [REGION, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'y']},
        'DemandNeedingReserveMargin': {'sets': [REGION, TIMESLICE, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 'l', 'y']},

            # ====  Emissions  ====

        'DiscountedTechnologyEmissionsPenalty': {'sets': [REGION, TECHNOLOGY, YEAR], 'lb': 0, 'ub': None, 'cat': 'Continuous', 'indices': ['r', 't', 'y']},
        }

        # Dictionaries for variables

        # ====  Net Present Cost  ====

        # 'Cost'

        # ====  Demands  ====
        Demand = createVariable('Demand', variables)

        if len(STORAGE)!= 0:

            # ====  Storage  ====

            StorageLevelYearStart = createVariable('StorageLevelYearStart', variables)
            StorageLevelYearFinish = createVariable('StorageLevelYearFinish', variables)
            StorageLevelTimesliceStart = createVariable('StorageLevelTimesliceStart', variables)
            StorageLosses = createVariable('StorageLosses', variables)
            StorageLowerLimit = createVariable('StorageLowerLimit', variables)
            StorageUpperLimit = createVariable('StorageUpperLimit', variables)
            StorageSurfaceArea = createVariable('StorageSurfaceArea', variables)
            StorageLossescooling = createVariable('StorageLossescooling', variables)
            StorageLossesheating = createVariable('StorageLossesheating', variables)
            NewStorageCapacity = createVariable('NewStorageCapacity', variables)
            SalvageValueStorage = createVariable('SalvageValueStorage', variables)
            TotalDiscountedStorageCost = createVariable('TotalDiscountedStorageCost', variables)

        # ====  Capacity Variables  ====

        NumberOfNewTechnologyUnits = createVariable('NumberOfNewTechnologyUnits', variables)
        NewCapacity = createVariable('NewCapacity', variables)

        # ====  Activity Variables  ====

        RateOfActivity = createVariable('RateOfActivity', variables)
        ProductionByTechnologyAnnual = createVariable('ProductionByTechnologyAnnual', variables)
        Production = createVariable('Production', variables)
        Use = createVariable('Use', variables)
        Trade = createVariable('Trade', variables)
        TradeAnnual = createVariable('TradeAnnual', variables)
        ProductionAnnual = createVariable('ProductionAnnual', variables)
        UseAnnual = createVariable('UseAnnual', variables)
        InputToNewCapacity = createVariable('InputToNewCapacity', variables)
        InputToTotalCapacity = createVariable('InputToTotalCapacity', variables)

        # ====  Costing Variables  ====

        CapitalInvestment = createVariable('CapitalInvestment', variables)
        DiscountedCapitalInvestment = createVariable('DiscountedCapitalInvestment', variables)
        SalvageValue = createVariable('SalvageValue', variables)
        DiscountedSalvageValue = createVariable('DiscountedSalvageValue', variables)
        OperatingCost = createVariable('OperatingCost', variables)
        DiscountedCapitalInvestmentByTechnology = createVariable('DiscountedCapitalInvestmentByTechnology', variables)
        DiscountedOperatingCost = createVariable('DiscountedOperatingCost', variables)
        AnnualVariableOperatingCost = createVariable('AnnualVariableOperatingCost', variables)
        AnnualFixedOperatingCost = createVariable('AnnualFixedOperatingCost', variables)
        TotalDiscountedCostByTechnology = createVariable('TotalDiscountedCostByTechnology', variables)
        TotalDiscountedCost = createVariable('TotalDiscountedCost', variables)
        ModelPeriodCostByRegion = createVariable('ModelPeriodCostByRegion', variables)
        # ====  Reserve Margin  ====

        TotalCapacityInReserveMargin = createVariable('TotalCapacityInReserveMargin', variables)
        DemandNeedingReserveMargin = createVariable('DemandNeedingReserveMargin', variables)

        # ====  Emissions  ====

        if len(EMISSION)!= 0:

            DiscountedTechnologyEmissionsPenalty = createVariable('DiscountedTechnologyEmissionsPenalty', variables)
            

        logging.info(f"\t{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t"
                    f"Variables are created.")

        # ------------------------------------------------------------------------------------------------------------------
        #    OBJECTIVE FUNCTION
        # ------------------------------------------------------------------------------------------------------------------

        Cost = pulp.LpVariable("Cost", cat='Continuous')
        model += Cost, "Objective"
        model += Cost == pulp.lpSum([TotalDiscountedCost.get(ci(ry)) for ry in REGION_YEAR]), "Cost_function"

        # ------------------------------------------------------------------------------------------------------------------
        #    CONSTRAINTS
        # ------------------------------------------------------------------------------------------------------------------
        
        # ====  Capacity Adequacy A  ====

        for rlty in REGION_TIMESLICE_TECHNOLOGY_YEAR:
            # CAa4_Constraint_Capacity
            model += pulp.lpSum([(RateOfActivity.get(ci([*rlty[0:2], m, *rlty[2:4]])) * OutputModeofoperation.get(ci([rlty[0], m, *rlty[2:4]]), dflt.get('OutputModeofoperation'))) for m in MODE_OF_OPERATION]) <= (pulp.lpSum([NewCapacity.get(ci([rlty[0], rlty[2], yy])) for yy in YEAR if (float(int(rlty[3]) - int(yy)) < float(OperationalLife.get(ci([rlty[0], rlty[2]]), dflt.get('OperationalLife')))) and (int(rlty[3]) - int(yy) >= 0)]) + ResidualCapacity.get(ci([rlty[0], *rlty[2:4]]), dflt.get('ResidualCapacity'))) * CapacityFactor.get(ci(rlty), dflt.get('CapacityFactor')) * CapacityToActivityUnit.get(ci([rlty[0], rlty[2]]), dflt.get('CapacityToActivityUnit')), ""

        for rty in REGION_TECHNOLOGY_YEAR:
            if CapacityOfOneTechnologyUnit.get(ci(rty), dflt.get('CapacityOfOneTechnologyUnit')) != 0:
                # CAa5_TotalNewCapacity
                model += NewCapacity.get(ci(rty)) == CapacityOfOneTechnologyUnit.get(ci(rty), dflt.get('CapacityOfOneTechnologyUnit')) * NumberOfNewTechnologyUnits.get(ci(rty)), ""

        # ====  Capacity Adequacy B  ====
            # CAb1_PlannedMaintenance
            model += pulp.lpSum([RateOfActivity.get(ci([rty[0], *lm, *rty[1:3]])) * OutputModeofoperation.get(ci([rty[0], lm[1], *rty[1:3]]), dflt.get('OutputModeofoperation')) * YearSplit.get(ci([lm[0], rty[2]])) for lm in TIMESLICE_MODE_OF_OPERATION]) <= pulp.lpSum(([(pulp.lpSum([NewCapacity.get(ci([*rty[0:2], yy])) for yy in YEAR if (float(int(rty[2]) - int(yy)) < float(OperationalLife.get(ci(rty[0:2]), dflt.get('OperationalLife')))) and (int(rty[2]) - int(yy) >= 0)]) + ResidualCapacity.get(ci(rty), dflt.get('ResidualCapacity'))) * CapacityFactor.get(ci([rty[0], l, *rty[1:3]]), dflt.get('CapacityFactor')) * YearSplit.get(ci([l, rty[2]])) for l in TIMESLICE])) * CapacityToActivityUnit.get(ci([rty[0], rty[1]]), dflt.get('CapacityToActivityUnit')) * AvailabilityFactor.get(ci([rty[0], *rty[1:3]]), dflt.get('AvailabilityFactor')), ""
        
        # ====  Energy Balance A  ====
        for rfly in REGION_FUEL_TIMESLICE_YEAR:
            # EBa7_EnergyBalanceEachTS1
            model += Production.get(ci(rfly)) == (pulp.lpSum([(RateOfActivity.get(ci([rfly[0], rfly[2], *mt, rfly[3]])) * OutputActivityRatio.get(ci([*rfly[0:2], *mt, rfly[3]]), dflt.get('OutputActivityRatio'))) * YearSplit.get(ci(rfly[2:4])) for mt in MODE_OF_OPERATION_TECHNOLOGY if OutputActivityRatio.get(ci([*rfly[0:2], *mt, rfly[3]]), dflt.get('OutputActivityRatio')) != 0])), ""
            # EBa8_EnergyBalanceEachTS2
            model += Use.get(ci(rfly)) == pulp.lpSum([(RateOfActivity.get(ci([rfly[0], rfly[2], *mt, rfly[3]])) * InputActivityRatio.get(ci([*rfly[0:2], *mt, rfly[3]]), dflt.get('InputActivityRatio'))) * YearSplit.get(ci(rfly[2:4])) for mt in MODE_OF_OPERATION_TECHNOLOGY if InputActivityRatio.get(ci([*rfly[0:2], *mt, rfly[3]]), dflt.get('InputActivityRatio')) != 0]), ""

            # EBa9_EnergyBalanceEachTS3
            model += Demand.get(ci(rfly)) == SpecifiedAnnualDemand.get(ci([*rfly[0:2], rfly[3]]), dflt.get('SpecifiedAnnualDemand')) * SpecifiedDemandProfile.get(ci(rfly), dflt.get('SpecifiedDemandProfile')), ""

            # EBa11_EnergyBalanceEachTS5
            model += Production.get(ci(rfly)) >= Demand.get(ci(rfly)) + Use.get(ci(rfly)) + (GIS_Losses.get(ci([*rfly[0:2]]), dflt.get('GIS_Losses')) * (8760 / int(max(TIMESLICE)))) + pulp.lpSum([Trade.get(ci([rfly[0], rr, *rfly[1:4]])) * TradeRoute.get(ci([rfly[0], rr, rfly[1], rfly[3]]), dflt.get('TradeRoute')) for rr in REGION2]), ""

        for rr2fly in REGION_REGION2_FUEL_TIMESLICE_YEAR:
            # EBa10_EnergyBalanceEachTS4
            model += Trade.get(ci(rr2fly)) == -Trade.get(ci([rr2fly[1], rr2fly[0], *rr2fly[2:5]])), ""

        # ====  Energy Balance B  ====

        for rfy in REGION_FUEL_YEAR:
            
        # EBb1_EnergyBalanceEachYear1 
            model += ProductionAnnual.get(ci(rfy)) == (pulp.lpSum([(RateOfActivity.get(ci([rfy[0], *lmt, rfy[2]])) * OutputActivityRatio.get(ci([*rfy[0:2], *lmt[1:3], rfy[2]]), dflt.get('OutputActivityRatio')) * YearSplit.get(ci([lmt[0], rfy[2]]))) for lmt in TIMESLICE_MODE_OF_OPERATION_TECHNOLOGY if OutputActivityRatio.get(ci([*rfy[0:2], *lmt[1:3], rfy[2]]), dflt.get('OutputActivityRatio')) != 0])), ""
            # EBb2_EnergyBalanceEachYear2
            model += UseAnnual.get(ci(rfy)) == (pulp.lpSum([(RateOfActivity.get(ci([rfy[0], *lmt, rfy[2]])) * InputActivityRatio.get(ci([*rfy[0:2], *lmt[1:3], rfy[2]]), dflt.get('InputActivityRatio')) * YearSplit.get(ci([lmt[0], rfy[2]]))) for lmt in TIMESLICE_MODE_OF_OPERATION_TECHNOLOGY if InputActivityRatio.get(ci([*rfy[0:2], *lmt[1:3], rfy[2]]), dflt.get('InputActivityRatio')) != 0])), ""

        for rr2fy in REGION_REGION2_FUEL_YEAR:
            if TradeRoute.get(ci(rr2fy), dflt.get('TradeRoute'))!= 0:
            # EBb3_EnergyBalanceEachYear3
                model += TradeAnnual.get(ci(rr2fy)) == pulp.lpSum([Trade.get(ci([*rr2fy[0:2], l, *rr2fy[2:4]])) for l in TIMESLICE]), ""
        
        for rfy in REGION_FUEL_YEAR:
            
            # EBb4_EnergyBalanceEachYear4
            model += ProductionAnnual.get(ci(rfy)) >= UseAnnual.get(ci(rfy)) + pulp.lpSum([TradeAnnual.get(ci([rfy[0], rr, *rfy[1:3]])) * TradeRoute.get(ci([rfy[0], rr, *rfy[1:3]]), dflt.get('TradeRoute')) for rr in REGION2]) + AccumulatedAnnualDemand.get(ci(rfy), dflt.get('AccumulatedAnnualDemand')) + pulp.lpSum([InputToNewCapacity.get(ci([*rfy[0:2], t, rfy[2]])) for t in TECHNOLOGY]) + pulp.lpSum([InputToTotalCapacity.get(ci([*rfy[0:2], t, rfy[2]])) for t in TECHNOLOGY]), ""

        # ====  Accounting Technology Production/Use  ====

        for r in REGION:
            # Acc4_ModelPeriodCostByRegion
            model += ModelPeriodCostByRegion.get(r) == pulp.lpSum([TotalDiscountedCost.get(ci([r, y])) for y in YEAR]), ""
        
        ### STORAGE EQUATIONS ###
        if len(STORAGE) != 0:
            # ====  Storage equations for Thermal storage -  ====
            
            for rsy in REGION_STORAGE_YEAR:
                if(StorageL2D.get(ci(rsy[0:2]), dflt.get('StorageL2D')) == 0):
                    model += StorageSurfaceArea.get(ci(rsy)) == 0.0744 * (pulp.lpSum([NewStorageCapacity.get(ci([*rsy[0:2], yy])) for yy in YEAR if (float(int(rsy[2]) - int(yy)) < float(OperationalLifeStorage.get(ci(rsy[0:2]), dflt.get('OperationalLifeStorage')))) and (int(rsy[2])-int(yy) >= 0)]) + ResidualStorageCapacity.get(ci(rsy), dflt.get('ResidualStorageCapacity'))) * Storagetagheating.get(ci(rsy[0:2]), dflt.get('Storagetagheating')) + 0.0361 * (pulp.lpSum([NewStorageCapacity.get(ci([*rsy[0:2], yy])) for yy in YEAR if (float(int(rsy[2]) - int(yy)) < float(OperationalLifeStorage.get(ci(rsy[0:2]), dflt.get('OperationalLifeStorage')))) and (int(rsy[2])-int(yy) >= 0)]) + ResidualStorageCapacity.get(ci(rsy), dflt.get('ResidualStorageCapacity'))) * Storagetagcooling.get(ci(rsy[0:2]), dflt.get('Storagetagcooling')), ""  
                elif(StorageL2D.get(ci(rsy[0:2]), dflt.get('StorageL2D')) == 1):
                    model += StorageSurfaceArea.get(ci(rsy)) == 0.1339 * (pulp.lpSum([NewStorageCapacity.get(ci([*rsy[0:2], yy])) for yy in YEAR if (float(int(rsy[2]) - int(yy)) < float(OperationalLifeStorage.get(ci(rsy[0:2]), dflt.get('OperationalLifeStorage')))) and (int(rsy[2])-int(yy) >= 0)]) + ResidualStorageCapacity.get(ci(rsy), dflt.get('ResidualStorageCapacity'))) * Storagetagheating.get(ci(rsy[0:2]), dflt.get('Storagetagheating')) + 0.065 * (pulp.lpSum([NewStorageCapacity.get(ci([*rsy[0:2], yy])) for yy in YEAR if (float(int(rsy[2]) - int(yy)) < float(OperationalLifeStorage.get(ci(rsy[0:2]), dflt.get('OperationalLifeStorage')))) and (int(rsy[2])-int(yy) >= 0)]) + ResidualStorageCapacity.get(ci(rsy), dflt.get('ResidualStorageCapacity'))) * Storagetagcooling.get(ci(rsy[0:2]), dflt.get('Storagetagcooling')), ""
                        
            for rsly in REGION_STORAGE_TIMESLICE_YEAR:
                #SL1_Storage_losses
                model += StorageLossesheating.get(ci(rsly)) == (StorageSurfaceArea.get(ci([*rsly[0:2], rsly[3]])) * 0.0036 * (8760 / int(max(TIMESLICE))) * (StorageUvalue.get(ci([*rsly[0:2], rsly[3]]), dflt.get('StorageUvalue'))) * ((((StorageFlowTemperature.get(ci([*rsly[0:2], rsly[3]]), dflt.get('StorageFlowTemperature'))) + (StorageReturnTemperature.get(ci([*rsly[0:2], rsly[3]]), dflt.get('StorageReturnTemperature')))) / 2) - (StorageAmbientTemperature.get(ci([*rsly[0:2], rsly[3]]), dflt.get('StorageAmbientTemperature')))) / 1000 * Storagetagheating.get(ci(rsly[0:2]), dflt.get('Storagetagheating'))) ,"" 

                model += StorageLossescooling.get(ci(rsly)) == (StorageSurfaceArea.get(ci([*rsly[0:2], rsly[3]])) * 0.0036 * (8760 / int(max(TIMESLICE))) * (StorageUvalue.get(ci([*rsly[0:2], rsly[3]]), dflt.get('StorageUvalue'))) * ((StorageAmbientTemperature.get(ci([*rsly[0:2], rsly[3]]), dflt.get('StorageAmbientTemperature'))) - (((StorageFlowTemperature.get(ci([*rsly[0:2], rsly[3]]), dflt.get('StorageFlowTemperature'))) + (StorageReturnTemperature.get(ci([*rsly[0:2], rsly[3]]), dflt.get('StorageReturnTemperature')))) / 2)) / 1000 * Storagetagcooling.get(ci(rsly[0:2]), dflt.get('Storagetagcooling'))) ,""       

                model += StorageLosses.get(ci(rsly)) ==  StorageLossesheating.get(ci(rsly)) + StorageLossescooling.get(ci(rsly)), ""      
            
            for rsy in REGION_STORAGE_YEAR:
            #S5_and_S6_StorageLevelYearStart
                if int(rsy[2]) == int(min(YEAR)):
                    model += StorageLevelYearStart.get(ci(rsy)) == StorageLevelStart.get(ci(rsy[0:2]), dflt.get('StorageLevelStart')), ""
                else:
                    model += StorageLevelYearStart.get(ci(rsy)) == StorageLevelYearStart.get(ci([*rsy[0:2], str(int(rsy[2])-1)])) + (pulp.lpSum([(RateOfActivity.get(ci([rsy[0], *lmt, rsy[2]])) * TechnologyToStorage.get(ci([*rsy[0:2], *lmt[1:3]]), dflt.get('TechnologyToStorage'))) - (RateOfActivity.get(ci([rsy[0], *lmt, rsy[2]])) * TechnologyFromStorage.get(ci([*rsy[0:2], *lmt[1:3]]), dflt.get('TechnologyFromStorage'))) for lmt in TIMESLICE_MODE_OF_OPERATION_TECHNOLOGY])) , ""
                        
            for rsly in REGION_STORAGE_TIMESLICE_YEAR:
                #S1_and_S2_StorageLevelTimesliceStart  
                if int(rsly[2]) == int(min(TIMESLICE)):
                    model += StorageLevelTimesliceStart.get(ci(rsly)) == StorageLevelYearStart.get(ci([*rsly[0:2], rsly[3]])), ""
                else:
                    model += StorageLevelTimesliceStart.get(ci(rsly)) == StorageLevelTimesliceStart.get(ci([*rsly[0:2], str(int(rsly[2])-1), rsly[3]])) - StorageLosses.get(ci([*rsly[0:2], str(int(rsly[2])-1), rsly[3]]))  + pulp.lpSum([(RateOfActivity.get(ci([rsly[0], rsly[2], *mt, rsly[3]])) * TechnologyToStorage.get(ci([*rsly[0:2], *mt]), dflt.get('TechnologyToStorage')) - RateOfActivity.get(ci([rsly[0], rsly[2], *mt, rsly[3]])) * TechnologyFromStorage.get(ci([*rsly[0:2], *mt]), dflt.get('TechnologyFromStorage'))) * YearSplit.get(ci([str(int(rsly[2])-1), rsly[3]])) for mt in MODE_OF_OPERATION_TECHNOLOGY if TechnologyToStorage.get(ci(([*rsly[0:2],*mt])), dflt.get('TechnologyToStorage')) > 0 or TechnologyFromStorage.get(ci([*rsly[0:2], *mt]), dflt.get('TechnologyFromStorage')) > 0]), ""

            for rs in REGION_STORAGE:
                #SC8_StorageRefilling 
                model += 0 == pulp.lpSum([RateOfActivity.get(ci([rs[0], *lmty])) * TechnologyToStorage.get(ci([*rs[0:2], *lmty[1:3]]), dflt.get('TechnologyToStorage')) * YearSplit.get(ci([lmty[0], lmty[3]])) for lmty in TIMESLICE_MODE_OF_OPERATION_TECHNOLOGY_YEAR if TechnologyToStorage.get(ci(([*rs[0:2], *lmty[1:3]])), dflt.get('TechnologyToStorage')) > 0]) - pulp.lpSum([RateOfActivity.get(ci([rs[0], *lmty])) * TechnologyFromStorage.get(ci([*rs[0:2], *lmty[1:3]]), dflt.get('TechnologyFromStorage')) * YearSplit.get(ci([lmty[0], lmty[3]])) for lmty in TIMESLICE_MODE_OF_OPERATION_TECHNOLOGY_YEAR if TechnologyFromStorage.get(ci([*rs[0:2], *lmty[1:3]]), dflt.get('TechnologyFromStorage')) > 0]) , ""
                    
            #===== Storage Constraints ====
            
            for rsy in REGION_STORAGE_YEAR:        
            # SI1_StorageMaxCapacity
                model += pulp.lpSum([NewStorageCapacity.get(ci([*rsy[0:2], yy])) for yy in YEAR if (float(int(rsy[2]) - int(yy)) < float(OperationalLifeStorage.get(ci(rsy[0:2]), dflt.get('OperationalLifeStorage')))) and (int(rsy[2])-int(yy) >= 0)]) + ResidualStorageCapacity.get(ci(rsy), dflt.get('ResidualStorageCapacity')) <= StorageMaxCapacity.get(ci(rsy[0:2]), dflt.get('StorageMaxCapacity')), ""
        
            for rsly in REGION_STORAGE_TIMESLICE_YEAR:
                #SC1_LowerLimit
                model += StorageLevelTimesliceStart.get(ci(rsly)) >= MinStorageCharge.get(ci([*rsly[0:2], rsly[3]]), dflt.get('MinStorageCharge')) * (pulp.lpSum([NewStorageCapacity.get(ci([*rsy[0:2], yy])) for yy in YEAR if (float(int(rsy[2]) - int(yy)) < float(OperationalLifeStorage.get(ci(rsy[0:2]), dflt.get('OperationalLifeStorage')))) and (int(rsy[2])-int(yy) >= 0)]) + ResidualStorageCapacity.get(ci(rsy), dflt.get('ResidualStorageCapacity'))), ""
                
                #SC2_Upper_Limit
                model += StorageLevelTimesliceStart.get(ci(rsly)) <= pulp.lpSum([NewStorageCapacity.get(ci([*rsly[0:2], yy])) for yy in YEAR if (float(int(rsly[3]) - int(yy)) < float(OperationalLifeStorage.get(ci(rsly[0:2]), dflt.get('OperationalLifeStorage')))) and (int(rsly[3])-int(yy) >= 0)]) + ResidualStorageCapacity.get(ci([*rsly[0:2], rsly[3]]), dflt.get('ResidualStorageCapacity')), "" 
                
                #SC3_Charging_Upper_Limit
                #model += StorageMaxChargeRate.get(ci([*rsly[0:2], rsly[3]]), dflt.get('StorageMaxChargeRate')) >= StorageLevelTimesliceStart.get(ci(rsly)) - StorageLevelTimesliceStart.get(ci([*rsly[0:2], str(int(rsly[2])-1), rsly[3]])), ""

                #SC4_Charging_Lower_Limit
                #model += StorageMaxDischargeRate.get(ci([*rsly[0:2], rsly[3]]), dflt.get('StorageMaxDischargeRate')) >= StorageLevelTimesliceStart.get(ci([*rsly[0:2], str(int(rsly[2])-1), rsly[3]])) - StorageLevelTimesliceStart.get(ci(rsly)), ""
        
            # ====  Storage Investments  ====   
            
            # SI4_UndiscountedCapitalInvestmentStorage
            for rsy in REGION_STORAGE_YEAR: 
            # SI6_SalvageValueStorageAtEndOfPeriod1
                if float(int(rsy[2]) + OperationalLifeStorage.get(ci(rsy[0:2]), dflt.get('OperationalLifeStorage'))) - 1 <= float(max(YEAR)):
                    model += SalvageValueStorage.get(ci(rsy)) == 0, ""
                # SI7_SalvageValueStorageAtEndOfPeriod2
                if ((DepreciationMethod.get(rsy[0], dflt.get('DepreciationMethod')) == 1) and (float(int(rsy[2])+OperationalLifeStorage.get(ci(rsy[0:2]), dflt.get('OperationalLifeStorage'))-1) > float(max(YEAR))) and (DiscountRateSto.get(ci(rsy[0:2]), dflt.get('DiscountRateSto')) == 0)) or ((DepreciationMethod.get(rsy[0], dflt.get('DepreciationMethod')) == 2) and (float(int(rsy[2])+OperationalLifeStorage.get(ci(rsy[0:2]), dflt.get('OperationalLifeStorage'))-1) > float(max(YEAR)))):
                    model += SalvageValueStorage.get(ci(rsy)) == (CapitalCostStorage.get(ci(rsy), dflt.get('CapitalCostStorage')) * NewStorageCapacity.get(ci(rsy))) * (1-(int(max(YEAR))-int(rsy[2])+1))/OperationalLifeStorage.get(ci(rsy[0:2]), dflt.get('OperationalLifeStorage')), ""
                # SI8_SalvageValueStorageAtEndOfPeriod3
                if (DepreciationMethod.get(rsy[0], dflt.get('DepreciationMethod')) == 1) and (float(int(rsy[2])+OperationalLifeStorage.get(ci(rsy[0:2]), dflt.get('OperationalLifeStorage'))-1) > float(max(YEAR))) and (DiscountRateSto.get(ci(rsy[0:2]), dflt.get('DiscountRateSto')) > 0):
                    model += SalvageValueStorage.get(ci(rsy)) == (CapitalCostStorage.get(ci(rsy), dflt.get('CapitalCostStorage')) * NewStorageCapacity.get(ci(rsy))) * (1-(((1+DiscountRateSto.get(ci(rsy[0:2]), dflt.get('DiscountRateSto')))**(int(max(YEAR)) - int(rsy[2])+1)-1)/((1+DiscountRateSto.get(ci(rsy[0:2]), dflt.get('DiscountRateSto')))**OperationalLifeStorage.get(ci(rsy[0:2]), dflt.get('OperationalLifeStorage'))-1))), ""
                # SI10_TotalDiscountedCostByStorage
                model += TotalDiscountedStorageCost.get(ci(rsy)) == (CapitalCostStorage.get(ci(rsy), dflt.get('CapitalCostStorage')) * NewStorageCapacity.get(ci(rsy))) * (1/ ((1+DiscountRateSto.get(ci(rsy[0:2]), dflt.get('DiscountRateSto')))**(int(rsy[2]) - int(min(YEAR))))) - (SalvageValueStorage.get(ci(rsy)) * (1 /((1+DiscountRateSto.get(ci(rsy[0:2]), dflt.get('DiscountRateSto')))**(int(max(YEAR))-int(min(YEAR))+1)))), ""
            
        for r in REGION:
        # # ====  Budegt constraint ====
            model += MaximumBudget.get((r), dflt.get('MaximumBudget')) >=  pulp.lpSum([(((CapitalCost.get(ci([r, *ty]), dflt.get('CapitalCost')) * NewCapacity.get(ci([r, *ty]))) * (1/((1 + DiscountRateTech.get(ci([r,ty[0]]), dflt.get('DiscountRateTech'))) ** (int(ty[1]) - int(min(YEAR)))))) - (SalvageValue.get(ci([r, *ty])) * (1 / ((1 +  DiscountRateTech.get(ci([r, ty[0]]), dflt.get('DiscountRateTech'))) ** (1 + int(max(YEAR)) - int(min(YEAR))))))) for ty in TECHNOLOGY_YEAR]), ""   
            
        for rty in REGION_TECHNOLOGY_YEAR:
        # ====  Salvage Value  ====
            # SV1_SalvageValueAtEndOfPeriod1
            if (DepreciationMethod.get(rty[0], dflt.get('DepreciationMethod')) == 1) and (float(int(rty[2]) + OperationalLife.get(ci(rty[0:2]), dflt.get('OperationalLife'))) - 1 > float(max(YEAR))) and (DiscountRate.get(ci(rty[0:2]), dflt.get('DiscountRate')) > 0):
                model += SalvageValue.get(ci(rty)) == CapitalCost.get(ci(rty), dflt.get('CapitalCost')) * NewCapacity.get(ci(rty)) * DiscountFactorIndProd.get(ci(rty)) * (1 - (((1 +  DiscountRate.get(ci(rty[0:2]), dflt.get('DiscountRate'))) ** (int(max(YEAR)) - int(rty[2]) + 1) - 1) / ((1 +  DiscountRate.get(ci(rty[0:2]), dflt.get('DiscountRate'))) ** OperationalLife.get(ci(rty[0:2]), dflt.get('OperationalLife')) - 1))), ""
            # SV2_SalvageValueAtEndOfPeriod2
            if ((DepreciationMethod.get(rty[0], dflt.get('DepreciationMethod')) == 2) and (float(int(rty[2]) + OperationalLife.get(ci(rty[0:2]), dflt.get('OperationalLife'))) - 1 > float(max(YEAR))) and ( DiscountRate.get(ci(rty[0:2]), dflt.get('DiscountRate')) == 0)) or ((DepreciationMethod.get(rty[0], dflt.get('DepreciationMethod')) == 2) and (float(int(rty[2]) + OperationalLife.get(ci(rty[0:2]), dflt.get('OperationalLife'))) - 1 > float(max(YEAR)))):
                model += SalvageValue.get(ci(rty)) == CapitalCost.get(ci(rty), dflt.get('CapitalCost')) * NewCapacity.get(ci(rty)) *  DiscountFactorIndProd.get(ci(rty)) * (1 - (int(max(YEAR)) - int(rty[2]) + 1) / OperationalLife.get(ci(rty[0:2]), dflt.get('OperationalLife'))), ""
            # SV3_SalvageValueAtEndOfPeriod3)
            if float(int(rty[2]) + OperationalLife.get(ci(rty[0:2]), dflt.get('OperationalLife')) - 1) <= float(max(YEAR)):
                model += SalvageValue.get(ci(rty)) == 0, ""
            
        # ====  Total Discounted Costs  ====

        for ry in REGION_YEAR:
            # TDC2_TotalDiscountedCost
            model += TotalDiscountedCost.get(ci(ry)) == pulp.lpSum([TotalDiscountedCostByTechnology.get(ci([ry[0], t, ry[1]])) for t in TECHNOLOGY]) + pulp.lpSum([TotalDiscountedStorageCost.get(ci([ry[0], s, ry[1]])) for s in STORAGE]), ""

        for rty in REGION_TECHNOLOGY_YEAR:
            varcost = df[df['PARAM']=='VariableCost']
            if len(varcost['TIMESLICE'].unique()) == 1 and varcost['TIMESLICE'].unique()[0] == '<NA>':
            # TDC1_TotalDiscountedCostByTechnology
                model += TotalDiscountedCostByTechnology.get(ci(rty)) == ((pulp.lpSum([RateOfActivity.get(ci([rty[0], *lm, *rty[1:3]])) * YearSplit.get(ci([lm[0], rty[2]])) * VariableCost.get(ci([rty[0], lm[1], *rty[1:3]]), dflt.get('VariableCost')) for lm in TIMESLICE_MODE_OF_OPERATION])\
                                                                        + (pulp.lpSum([NewCapacity.get(ci([*rty[0:2], yy])) for yy in YEAR if (float(int(rty[2]) - int(yy)) < float(OperationalLife.get(ci(rty[0:2]), dflt.get('OperationalLife')))) and (int(rty[2]) - int(yy) >= 0)]) + ResidualCapacity.get(ci(rty), dflt.get('ResidualCapacity'))) * FixedCost.get(ci(rty), dflt.get('FixedCost'))) * (1/DiscountFactorMid.get(ci(rty))))\
                                                                            + ((CapitalCost.get(ci(rty), dflt.get('CapitalCost')) * NewCapacity.get(ci(rty))) * DiscountFactorIndProd.get(ci(rty))/DiscountFactor.get(ci(rty)))\
                                                                                + (pulp.lpSum([EmissionActivityRatio.get(ci([*rty[0], elm[0], elm[2] , rty[1:3]]), dflt.get('EmissionActivityRatio')) * RateOfActivity.get(ci([rty[0], *elm[1:3], *rty[1:3]])) * YearSplit.get(ci([elm[1], rty[2]])) * EmissionsPenalty.get(ci([rty[0], elm[0], rty[2]]), dflt.get('EmissionsPenalty')) * (1/DiscountFactorMid.get(ci(rty))) for elm in EMISSION_TIMESLICE_MODE_OF_OPERATION]))\
                                                                                    - (SalvageValue.get(ci(rty)) * (1 / ((1 +  DiscountRate.get(ci(rty[0:2]), dflt.get('DiscountRate'))) ** (1 + int(max(YEAR)) - int(min(YEAR)))))), ""
            else:
                model += TotalDiscountedCostByTechnology.get(ci(rty)) == ((pulp.lpSum([RateOfActivity.get(ci([rty[0], *lm, *rty[1:3]])) * YearSplit.get(ci([lm[0], rty[2]])) * VariableCost.get(ci([rty[0], *lm, *rty[1:3]]), dflt.get('VariableCost')) for lm in TIMESLICE_MODE_OF_OPERATION])\
                                                                        + (pulp.lpSum([NewCapacity.get(ci([*rty[0:2], yy])) for yy in YEAR if (float(int(rty[2]) - int(yy)) < float(OperationalLife.get(ci(rty[0:2]), dflt.get('OperationalLife')))) and (int(rty[2]) - int(yy) >= 0)]) + ResidualCapacity.get(ci(rty), dflt.get('ResidualCapacity'))) * FixedCost.get(ci(rty), dflt.get('FixedCost'))) * (1/DiscountFactorMid.get(ci(rty))))\
                                                                            + ((CapitalCost.get(ci(rty), dflt.get('CapitalCost')) * NewCapacity.get(ci(rty))) * DiscountFactorIndProd.get(ci(rty))/DiscountFactor.get(ci(rty)))\
                                                                                + (pulp.lpSum([EmissionActivityRatio.get(ci([*rty[0], elm[0], elm[2] , rty[1:3]]), dflt.get('EmissionActivityRatio')) * RateOfActivity.get(ci([rty[0], *elm[1:3], *rty[1:3]])) * YearSplit.get(ci([elm[1], rty[2]])) * EmissionsPenalty.get(ci([rty[0], elm[0], rty[2]]), dflt.get('EmissionsPenalty')) * (1/DiscountFactorMid.get(ci(rty))) for elm in EMISSION_TIMESLICE_MODE_OF_OPERATION]))\
                                                                                    - (SalvageValue.get(ci(rty)) * (1 / ((1 +  DiscountRate.get(ci(rty[0:2]), dflt.get('DiscountRate'))) ** (1 + int(max(YEAR)) - int(min(YEAR)))))), ""

        # ====  Total Capacity Constraints  ====

            # TCC1_TotalAnnualMaxCapacityConstraint
            model += pulp.lpSum([NewCapacity.get(ci([*rty[0:2], yy])) for yy in YEAR if (float(int(rty[2]) - int(yy)) < float(OperationalLife.get(ci(rty[0:2]), dflt.get('OperationalLife')))) and (int(rty[2]) - int(yy) >= 0)]) + ResidualCapacity.get(ci(rty), dflt.get('ResidualCapacity')) <= TotalAnnualMaxCapacity.get(ci(rty), dflt.get('TotalAnnualMaxCapacity')), ""
            # TCC2_TotalAnnualMinCapacityConstraint
            if TotalAnnualMinCapacity.get(ci(rty), dflt.get('TotalAnnualMinCapacity')) > 0:
                model += pulp.lpSum([NewCapacity.get(ci([*rty[0:2], yy])) for yy in YEAR if (float(int(rty[2]) - int(yy)) < float(OperationalLife.get(ci(rty[0:2]), dflt.get('OperationalLife')))) and (int(rty[2]) - int(yy) >= 0)]) + ResidualCapacity.get(ci(rty), dflt.get('ResidualCapacity'))  >= TotalAnnualMinCapacity.get(ci(rty), dflt.get('TotalAnnualMinCapacity')), ""

        # ====  New Capacity Constraints  ====

            # NCC1_TotalAnnualMaxNewCapacityConstraint
            model += NewCapacity.get(ci(rty)) <= TotalAnnualMaxCapacityInvestment.get(ci(rty), dflt.get('TotalAnnualMaxCapacityInvestment')), ""
            # NCC2_TotalAnnualMinNewCapacityConstraint
            if TotalAnnualMinCapacityInvestment.get(ci(rty), dflt.get('TotalAnnualMinCapacityInvestment')) > 0:
                model += NewCapacity.get(ci(rty)) >= TotalAnnualMinCapacityInvestment.get(ci(rty), dflt.get('TotalAnnualMinCapacityInvestment')), ""

        # ====  Annual Activity Constraints  ====

            # AAC2_TotalAnnualTechnologyActivityUpperLimit
            model += pulp.lpSum([RateOfActivity.get(ci([rty[0], *lm, *rty[1:3]])) * OutputModeofoperation.get(ci([rty[0], lm[1], *rty[1:3]]), dflt.get('OutputModeofoperation')) * YearSplit.get(ci([lm[0], rty[2]])) for lm in TIMESLICE_MODE_OF_OPERATION]) <= TotalTechnologyAnnualActivityUpperLimit.get(ci(rty), dflt.get('TotalTechnologyAnnualActivityUpperLimit')), ""
            # AAC3_TotalAnnualTechnologyActivityLowerLimit
            if TotalTechnologyAnnualActivityLowerLimit.get(ci(rty), dflt.get('TotalTechnologyAnnualActivityLowerLimit')) > 0:
                model += pulp.lpSum([RateOfActivity.get(ci([rty[0], *lm, *rty[1:3]])) * OutputModeofoperation.get(ci([rty[0], lm[1], *rty[1:3]]), dflt.get('OutputModeofoperation')) * YearSplit.get(ci([lm[0], rty[2]])) for lm in TIMESLICE_MODE_OF_OPERATION]) >= TotalTechnologyAnnualActivityLowerLimit.get(ci(rty), dflt.get('TotalTechnologyAnnualActivityLowerLimit')), ""

        # ====  Total Activity Constraints  ====

        for rt in REGION_TECHNOLOGY:
        # TAC2_TotalModelHorizonTechnologyActivityUpperLimit
            model += pulp.lpSum([RateOfActivity.get(ci([rt[0], *lmy[0:2], rt[1], lmy[2]])) * OutputModeofoperation.get(ci([rt[0], lmy[1], rt[1], lmy[2]]), dflt.get('OutputModeofoperation')) * YearSplit.get(ci([lmy[0], lmy[2]])) for lmy in TIMESLICE_MODE_OF_OPERATION_YEAR]) <= TotalTechnologyModelPeriodActivityUpperLimit.get(ci(rt), dflt.get('TotalTechnologyModelPeriodActivityUpperLimit')), ""
            #TAC3_TotalModelHorizenTechnologyActivityLowerLimit
            if TotalTechnologyModelPeriodActivityLowerLimit.get(ci(rt), dflt.get('TotalTechnologyModelPeriodActivityLowerLimit')) > 0:
                model += pulp.lpSum([RateOfActivity.get(ci([rt[0], *lmy[0:2], rt[1], lmy[2]])) * OutputModeofoperation.get(ci([rt[0], lmy[1], rt[1], lmy[2]]), dflt.get('OutputModeofoperation')) * YearSplit.get(ci([lmy[0], lmy[2]])) for lmy in TIMESLICE_MODE_OF_OPERATION_YEAR]) >= TotalTechnologyModelPeriodActivityLowerLimit.get(ci(rt), dflt.get('TotalTechnologyModelPeriodActivityLowerLimit')), ""
        
        # ====  Input to Capacity Constraints  ====
        for rfty in REGION_FUEL_TECHNOLOGY_YEAR:
            if InputToNewCapacityRatio.get(ci(rfty), dflt.get('InputToNewCapacityRatio')) > 0:
                model += NewCapacity.get(ci([rfty[0], *rfty[2:4]])) * InputToNewCapacityRatio.get(ci(rfty), dflt.get('InputToNewCapacity')) == InputToNewCapacity.get(ci(rfty))

            if InputToTotalCapacityRatio.get(ci(rfty), dflt.get('InputToTotalCapacityRatio')) > 0:
                model += (pulp.lpSum([NewCapacity.get(ci([rfty[0], rfty[2], yy])) for yy in YEAR if (float(int(rfty[3]) - int(yy)) < float(OperationalLife.get(ci([rfty[1], rfty[2]]), dflt.get('OperationalLife')))) and (int(rfty[3]) - int(yy) >= 0)]) + ResidualCapacity.get(ci([rfty[0], *rfty[2:4]]), dflt.get('ResidualCapacity'))) * InputToTotalCapacityRatio.get(ci(rfty), dflt.get('InputToTotalCapacityRatio')) == InputToTotalCapacity.get(ci(rfty)), ""


        # ====  Total Activity Increase and decrease Constraints  ====

        for rmty in REGION_MODE_OF_OPERATION_TECHNOLOGY_YEAR:
            #LU3_TechnologyActivityIncreaseByMode
            if TechnologyActivityIncreaseByModeLimit.get(ci(rmty), dflt.get('TechnologyActivityIncreaseByModeLimit')) > 0:
                model += pulp.lpSum([RateOfActivity.get(ci([rmty[0], l, *rmty[1:4]])) * OutputModeofoperation.get(ci(rmty), dflt.get('OutputModeofoperation')) * YearSplit.get(ci([l, rmty[3]])) for l in TIMESLICE]) <= (1 + TechnologyActivityIncreaseByModeLimit.get(ci(rmty), dflt.get('TechnologyActivityIncreaseByModeLimit'))) * (pulp.lpSum([RateOfActivity.get(ci([rmty[0], l, *rmty[1:3], str(int(rmty[3])-1)])) * OutputModeofoperation.get(ci([*rmty[0:3], str(int(rmty[3])-1)]), dflt.get('OutputModeofoperation')) * YearSplit.get(ci([l, str(int(rmty[3])-1)])) for l in TIMESLICE])), ""
            
            #LU4_TechnologyActivityDecreaseByMode
            if TechnologyActivityDecreaseByModeLimit.get(ci(rmty), dflt.get('TechnologyActivityDecreaseByModeLimit')) > 0:
                model += pulp.lpSum([RateOfActivity.get(ci([rmty[0], l, *rmty[1:4]])) * OutputModeofoperation.get(ci(rmty), dflt.get('OutputModeofoperation')) * YearSplit.get(ci([l, rmty[3]])) for l in TIMESLICE]) >= (1 - TechnologyActivityDecreaseByModeLimit.get(ci(rmty), dflt.get('TechnologyActivityDecreaseByModeLimit'))) * (pulp.lpSum([RateOfActivity.get(ci([rmty[0], l, *rmty[1:3], str(int(rmty[3])-1)])) * OutputModeofoperation.get(ci([*rmty[0:3], str(int(rmty[3])-1)]), dflt.get('OutputModeofoperation')) * YearSplit.get(ci([l, str(int(rmty[3])-1)])) for l in TIMESLICE])), ""
    


        # ====  Reserve Margin Constraint  ====

        for rly in REGION_TIMESLICE_YEAR:
            # RM3_ReserveMargin_Constraint
            model += pulp.lpSum([(RateOfActivity.get(ci([*rly[0:2], *fmt[1:3], rly[2]])) * OutputActivityRatio.get(ci([rly[0], *fmt, rly[2]]), dflt.get('OutputActivityRatio'))) * ReserveMarginTagFuel.get(ci([rly[0], fmt[0], rly[2]]), dflt.get('ReserveMarginTagFuel')) for fmt in FUEL_MODE_OF_OPERATION_TECHNOLOGY if OutputActivityRatio.get(ci([rly[0], *fmt, rly[2]]), dflt.get('OutputActivityRatio')) != 0 ]) <= pulp.lpSum([(pulp.lpSum([NewCapacity.get(ci([rly[0], t, yy])) for yy in YEAR if (float(int(rly[2]) - int(yy)) < float(OperationalLife.get(ci([rly[0], t]), dflt.get('OperationalLife')))) and (int(rly[2]) - int(yy) >= 0)]) + ResidualCapacity.get(ci([rly[0], t , rly[2]]), dflt.get('ResidualCapacity'))) * ReserveMarginTagTechnology.get(ci([rly[0], t, rly[2]]), dflt.get('ReserveMarginTagTechnology')) * CapacityToActivityUnit.get(ci([rly[0], t]), dflt.get('CapacityToActivityUnit')) for t in TECHNOLOGY]) * (1/ReserveMargin.get(ci([rly[0], rly[2]]), dflt.get('ReserveMargin'))), ""

        # ====  RE Production Target  ====

        for ry in REGION_YEAR:
            # RE4_EnergyConstraint
            model += pulp.lpSum([(RateOfActivity.get(ci([ry[0], *flmt[1:4], ry[1]])) * OutputActivityRatio.get(ci([ry[0], flmt[0], *flmt[2:4], ry[1]]), dflt.get('OutputActivityRatio'))) * YearSplit.get(ci([flmt[1], ry[1]])) * RETagTechnology.get(ci([ry[0], flmt[3], ry[1]]), dflt.get('RETagTechnology')) for flmt in FUEL_TIMESLICE_MODE_OF_OPERATION_TECHNOLOGY if OutputActivityRatio.get(ci([ry[0], flmt[0], *flmt[2:4], ry[1]]), dflt.get('OutputActivityRatio')) != 0]) >= REMinProductionTarget.get(ci(ry), dflt.get('REMinProductionTarget')) * pulp.lpSum([(RateOfActivity.get(ci([ry[0], *flmt[1:4], ry[1]])) * OutputActivityRatio.get(ci([ry[0], flmt[0], *flmt[2:4], ry[1]]), dflt.get('OutputActivityRatio'))) * YearSplit.get(ci([flmt[1], ry[1]])) * RETagFuel.get(ci([ry[0], flmt[0], ry[1]]), dflt.get('RETagFuel'))  for flmt in FUEL_TIMESLICE_MODE_OF_OPERATION_TECHNOLOGY if OutputActivityRatio.get(ci([ry[0], flmt[0], *flmt[2:4], ry[1]]), dflt.get('OutputActivityRatio')) != 0]), ""
        
        # ====  Emissions Accounting  ====
        if len(EMISSION) != 0:
            for rey in REGION_EMISSION_YEAR:
                # E8_AnnualEmissionsLimit
                model += pulp.lpSum([EmissionActivityRatio.get(ci([*rey[0:2], *lmt[1:3], rey[2]]), dflt.get('EmissionActivityRatio')) * RateOfActivity.get(ci([rey[0], *lmt, rey[2]])) * YearSplit.get(ci([lmt[0], rty[2]])) for lmt in TIMESLICE_MODE_OF_OPERATION_TECHNOLOGY]) <= AnnualEmissionLimit.get(ci(rey), dflt.get('AnnualEmissionLimit')) - AnnualExogenousEmission.get(ci(rey), dflt.get('AnnualExogenousEmission')), ""

            for re in REGION_EMISSION:
                # E9_ModelPeriodEmissionsLimit
                model += pulp.lpSum([EmissionActivityRatio.get(ci([*re[0:2], *lmty[1:4]]), dflt.get('EmissionActivityRatio')) * RateOfActivity.get(ci([re[0], *lmty])) * YearSplit.get(ci([lmty[0], lmty[3]])) for lmty in TIMESLICE_MODE_OF_OPERATION_TECHNOLOGY_YEAR]) + ModelPeriodExogenousEmission.get(ci(re), dflt.get('ModelPeriodExogenousEmission')) <= ModelPeriodEmissionLimit.get(ci(re), dflt.get('ModelPeriodEmissionLimit')), ""

        logging.info(f"\t{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t"
                    f"Model is built.")

        # ------------------------------------------------------------------------------------------------------------------
        #    SAVE MODEL
        # ------------------------------------------------------------------------------------------------------------------

        #Write model to LP-file
        #model.writeLP(f"{modelName}_{i}.lp")

        # ------------------------------------------------------------------------------------------------------------------
        #    SOLVE
        # ------------------------------------------------------------------------------------------------------------------

        model.solve(solver)
        logging.info(f"\t{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t"
                    f"Model is solved. Solution is: "
                    f"{pulp.LpStatus[model.status]}")
        # ------------------------------------------------------------------------------------------------------------------
        #    SAVE RESULTS
        # ------------------------------------------------------------------------------------------------------------------

        if str(pulp.LpStatus[model.status]) == "Optimal":
            logging.info(f"\t{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t"
                        f"The optimal solution found a cost value of "
                        f"{round(model.objective.value(), 2)}")

            # Create dataframe to save results after the model was run the first time
            if i == 0:
                res_df = pd.DataFrame()
            res_df = pd.concat([res_df, saveResultsTemporary(model, i, variables)])

            logging.info(f"\t{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t"
                        f"Results are saved temporarily.")
        else:
            logging.error(f"\t{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t"
                        f"Error: Optimisation status for Scenario_{i} is: {pulp.LpStatus[model.status]}")
            
        if otoole is True:
            df, sets_df = create_df(inputDir)
        #res_df.to_csv('sampleoutputs.csv')
        res_df = postprocessing(res_df, df, sets_df, defaults_df)
        #res_df.to_csv('res_df.csv')

        del model  # Delete model

        i += 1
        
        # ------------------------------------------------------------------------------------------------------------------
        #    MONTE CARLO SIMULATION
        # ------------------------------------------------------------------------------------------------------------------

        if n > 0:

            # Note: Monte Carlo Simulation is applied to all selected parameters (parameters_mcs).
            # For each parameter, the parameters_mcs is only applied to parameter values that are not equal to default values,
            # i.e. values that were explicitly set.

            # ====  Reference parameters and data  ====

            mcs_df['INDEX'] = [ci([str(r), str(rr), str(ld), str(e), str(f), str(lh), str(ls), str(l), str(m), str(s), str(t), str(y)])\
                            .replace('nan-', '').replace('<NA>-', '').replace('-nan', '').replace('-<NA>', '')
                        for r, rr, ld, e, f, lh, ls, l, m, s, t, y in
                            zip(mcs_df.REGION, mcs_df.REGION2, mcs_df.DAYTYPE, mcs_df.EMISSION, mcs_df.FUEL, mcs_df.DAILYTIMEBRACKET, mcs_df.SEASON,\
                                mcs_df.TIMESLICE, mcs_df.MODE_OF_OPERATION, mcs_df.STORAGE, mcs_df.TECHNOLOGY, mcs_df.YEAR)]

            if i == 1:
                dflt_ref = dflt.copy()

                # All parameters
                parameters = list(df.PARAM.unique())
                parameters.extend(list(defaults_df.PARAM.unique()))
                parameters = sorted(tuple(set(parameters)))

                for p in parameters:
                    # Copy of original data as reference
                    globals()[f"{p}_ref"] = globals()[f"{p}"].copy()

            # ====  Random data generation  ====

            for p_mcs in parameters_mcs:
                # Dict with value where: Distribution specified, without default_setting:
                d1_df = mcs_df[(mcs_df['PARAM'] == p_mcs) & (mcs_df['DEFAULT_SETTING'] != 1)].copy()

                if len(d1_df) > 0:
                    d1_df['VALUE'] = [generateRandomData(globals()[f"{p_mcs}_ref"].get(index, dflt.get(p_mcs)), dist, rel_sd, rel_min, rel_max, array)
                                            for dist, rel_sd, rel_min, rel_max, array, index in zip(
                            d1_df['DISTRIBUTION'], d1_df['REL_SD'], d1_df['REL_MIN'], d1_df['REL_MAX'], d1_df['ARRAY'], d1_df['INDEX'])]

                    d1 = d1_df.set_index('INDEX').to_dict()['VALUE']

                # Default setting is not supported, yet.
                if len(mcs_df[(mcs_df['PARAM'] == p_mcs) & (mcs_df['DEFAULT_SETTING'] == 1)]) > 0:
                    logging.error(f"\t{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t"
                                f"Error: DEFAULT_SETTING in Monte Carlo Simulation is not supported, yet.")

                # Update global dictionary with new values from random generation
                globals()[f"{p_mcs}"].update(d1)

    # ----------------------------------------------------------------------------------------------------------------------
    #	SAVE ALL RESULTS
    # ----------------------------------------------------------------------------------------------------------------------

    logging.info(f"\t{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\t"
                f"Analysis is finished. Please wait until the results are saved!")
    return(res_df)