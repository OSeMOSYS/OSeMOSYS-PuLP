import os
import datetime as dt
import logging
import numpy as np
import pandas as pd
import pulp
import itertools

# ----------------------------------------------------------------------------------------------------------------------
#    FUNCTIONS
# ----------------------------------------------------------------------------------------------------------------------

def createParameter(_df, _name):
    return _df[_df['PARAM'] == _name].set_index('INDEX').to_dict()['VALUE']

def createParameterOT(_df, _name):
    _df =  _df.reset_index(drop=True)
    Index = _df.columns.tolist()
    Index.remove('VALUE')
    list1 = []
    for k in Index:
        df1 = _df[k]
        for i in range(0, len(df1)):
            if len(list1) < len(df1):
                list1.append(str(df1[i]))
            else:
                list1[i] = list1[i] + '-' + (str(df1[i]))
    _df['index'] = list1
    return _df.set_index('index').to_dict()['VALUE']


def createVariable(_name, _v):
    return newVarDict(_name, _v[_name]['lb'], _v[_name]['ub'], _v[_name]['cat'], _v[_name]['sets'])


def createTuple(_df, _set_name):
    if _set_name in ['DAYTYPE', 'DAILYTIMEBRACKET', 'SEASON', 'MODE_OF_OPERATION', 'YEAR', 'TIMESLICE']:
        return tuple([str(int(float(x))) for x in _df[_set_name] if x != 'nan'])
    else:
        return tuple([x for x in _df[_set_name] if x != 'nan'])

def createTupleOT(dictionary, _set_name):
    if _set_name in ['DAYTYPE', 'DAILYTIMEBRACKET', 'SEASON', 'MODE_OF_OPERATION', 'YEAR']:
        return tuple([str(int(float(x))) for x in dictionary[_set_name] if x != 'nan'])
    else:
        return tuple([x for x in dictionary[_set_name] if x != 'nan'])

def permutateSets(_sets_list):
    """ Permutation of sets """
    return tuple(itertools.product(*_sets_list))


def ci(_tuple):
    """ Combine indices """
    return "-".join([str(i) for i in _tuple])


def newVarDict(_name, _lb, _ub, _cat, _sets):
    """
    This function create a dictionary for a variable having a lower bound (lb),
    upper bound (ub), category (cat), using combined indices from the SETS
    """
    return {ci(v): pulp.LpVariable(f"{_name}_" + ci(v), lowBound=_lb, upBound=_ub, cat=_cat)
            for v in permutateSets(_sets)}


def loadData(filePath, sheetSets, sheetParams, sheetParamsDefault, sheetMcs, sheetMcsNum):
    """
    This function loads all data from the input data set to dataframes.
    """

    # Data: SETS
    sets_df = pd.read_excel(io=filePath, sheet_name=sheetSets)
    sets_df['REGION'] = sets_df['REGION'].astype(str)
    sets_df['REGION2'] = sets_df['REGION2'].astype(str)
    sets_df['DAYTYPE'] = sets_df['DAYTYPE'].astype(str)
    sets_df['EMISSION'] = sets_df['EMISSION'].astype(str)
    sets_df['FUEL'] = sets_df['FUEL'].astype(str)
    sets_df['DAILYTIMEBRACKET'] = sets_df['DAILYTIMEBRACKET'].astype(str)
    sets_df['SEASON'] = sets_df['SEASON'].astype(str)
    sets_df['TIMESLICE'] = sets_df['TIMESLICE'].astype(str)
    sets_df['MODE_OF_OPERATION'] = sets_df['MODE_OF_OPERATION'].astype(str)
    sets_df['STORAGE'] = sets_df['STORAGE'].astype(str)
    sets_df['TECHNOLOGY'] = sets_df['TECHNOLOGY'].astype(str)
    sets_df['YEAR'] = sets_df['YEAR'].astype(str)
    sets_df['FLEXIBLEDEMANDTYPE'] = sets_df['FLEXIBLEDEMANDTYPE'].astype(str)

    # Data: PARAMETERS
    df = pd.read_excel(io=filePath, sheet_name=sheetParams)
    df['PARAM'] = df['PARAM'].astype(str)
    df['VALUE'] = df['VALUE'].apply(pd.to_numeric, downcast='signed')
    df['REGION'] = df['REGION'].astype(str)
    df['REGION2'] = df['REGION2'].astype(str)
    df['DAYTYPE'] = df['DAYTYPE'].astype('Int64')
    df['DAYTYPE'] = df['DAYTYPE'].astype(str)
    df['EMISSION'] = df['EMISSION'].astype(str)
    df['FUEL'] = df['FUEL'].astype(str)
    df['DAILYTIMEBRACKET'] = df['DAILYTIMEBRACKET'].astype('Int64')
    df['DAILYTIMEBRACKET'] = df['DAILYTIMEBRACKET'].astype(str)
    df['SEASON'] = df['SEASON'].astype('Int64')
    df['SEASON'] = df['SEASON'].astype(str)
    df['TIMESLICE'] = df['TIMESLICE'].astype('Int64')
    df['TIMESLICE'] = df['TIMESLICE'].astype(str)
    df['MODE_OF_OPERATION'] = df['MODE_OF_OPERATION'].astype('Int64')
    df['MODE_OF_OPERATION'] = df['MODE_OF_OPERATION'].astype(str)
    df['STORAGE'] = df['STORAGE'].astype(str)
    df['TECHNOLOGY'] = df['TECHNOLOGY'].astype(str)
    df['YEAR'] = df['YEAR'].astype('Int64')

    # Data: Parameters default values
    defaults_df = pd.read_excel(io=filePath, sheet_name=sheetParamsDefault)
    defaults_df = defaults_df.fillna(0)
    defaults_df['PARAM'] = defaults_df['PARAM'].astype(str)
    defaults_df['VALUE'] = defaults_df['VALUE'].apply(pd.to_numeric, downcast='signed')

    # Data: Monte Carlo Simulation (MCS)
    mcs_df = pd.read_excel(io=filePath, sheet_name=sheetMcs)
    mcs_df['DEFAULT_SETTING'] = mcs_df['DEFAULT_SETTING'].apply(pd.to_numeric, downcast='signed')
    #mcs_df['REL_SD'] = mcs_df['REL_SD'].astype('Int64')
    #mcs_df['REL_MIN'] = mcs_df['REL_MIN'].astype('Int64')
    #mcs_df['REL_MAX'] = mcs_df['REL_MAX'].astype('Int64')
    mcs_df['DISTRIBUTION'] = mcs_df['DISTRIBUTION'].astype(str)
    mcs_df['ARRAY'] = [[float(i) for i in str(x).split(",")] for x in mcs_df['ARRAY']]

    mcs_df['PARAM'] = mcs_df['PARAM'].astype(str)
    mcs_df['REGION'] = mcs_df['REGION'].astype(str)
    mcs_df['REGION2'] = mcs_df['REGION2'].astype(str)
    mcs_df['DAYTYPE'] = mcs_df['DAYTYPE'].astype('Int64')
    mcs_df['DAYTYPE'] = mcs_df['DAYTYPE'].astype(str)
    mcs_df['EMISSION'] = mcs_df['EMISSION'].astype(str)
    mcs_df['FUEL'] = mcs_df['FUEL'].astype(str)
    mcs_df['DAILYTIMEBRACKET'] = mcs_df['DAILYTIMEBRACKET'].astype('Int64')
    mcs_df['DAILYTIMEBRACKET'] = mcs_df['DAILYTIMEBRACKET'].astype(str)
    mcs_df['SEASON'] = mcs_df['SEASON'].astype('Int64')
    mcs_df['SEASON'] = mcs_df['SEASON'].astype(str)
    mcs_df['TIMESLICE'] = mcs_df['TIMESLICE'].astype(str)
    mcs_df['MODE_OF_OPERATION'] = mcs_df['MODE_OF_OPERATION'].astype('Int64')
    mcs_df['MODE_OF_OPERATION'] = mcs_df['MODE_OF_OPERATION'].astype(str)
    mcs_df['STORAGE'] = mcs_df['STORAGE'].astype(str)
    mcs_df['TECHNOLOGY'] = mcs_df['TECHNOLOGY'].astype(str)
    mcs_df['YEAR'] = mcs_df['YEAR'].astype('Int64')

    # Number of MCS simulations
    n_df = pd.read_excel(io=filePath, sheet_name=sheetMcsNum)
    n = n_df.at[0, 'MCS_num']
    return sets_df, df, defaults_df, mcs_df, n


def generateRandomData(_ref, _dist, _rel_sd, _rel_min, _rel_max, _array):
    """
    This function generates random data for the parameters included in the Monte Carlo Simulations.

    reference (format: float): mean for normal distribution, mode for both triangular and uniform distributions
    dist: type of distribution. Choose from: "normal", "triangular", "uniform" (format: string)
    rel_sd: relative standard deviation from mean or mode. Unit: percent as decimals (format: float)
    rel_min: relative minimum deviation from mean or mode. Unit: percent as decimals (format: float), must be a negative value
    rel_max: relative maximum deviation from mean or mode. Unit: percent as decimals (format: float), must be a positive value
    array: array with potential values. One value out of the array will be randomly chosen.
    ==================================================================================================================
    Note: To use the reference value without any distribution, then write as input in the excel file in the tab "MCS":
    Columns: PARAM: "parameter name", DEFAULT_SETTING:	"1", DIST: "normal", REL_SD: "0".
    This will make the code to choose the reference value as defined for the model without MCS.
    """

    if _dist == "normal":
        # mean, standard deviation, generate 1 value at the time
        value = np.random.normal(_ref, _rel_sd * _ref, 1)[0]
    elif _dist == "triangular":
        # minimum value, mode, maximum value, generate 1 value at the time
        value = np.random.triangular((1 + _rel_min) * _ref, _ref, (1 + _rel_max) * _ref, 1)[0]
    elif _dist == "uniform":
        # minimum value, maximum value, generate 1 value at the time
        value = np.random.uniform((1 + _rel_min) * _ref, (1 + _rel_max) * _ref, 1)[0]
    elif _dist == "choice":
        if len(_array) > 1:
            value = np.random.choice(_array)
        else:
            logging.error("ERROR: Review MCS_df array column. Expected length of array: larger than 1, but is: 0 or 1")
    else:
        logging.error("ERROR: Select an available distribution, review input data and/or add default input data for this parameter.")
        return

    # This if condition prevents input errors caused by negative values for the parameters
    if value >= 0:
        return value
    else:
        return 0


def saveResultsTemporary(_model, _scenario_i, variables):
    """
    This function saves results from one simulation temporary.
    """

    df = pd.DataFrame()

    # Cost
    cost_df = pd.DataFrame(data={'NAME': ['Cost'],
                                 'VALUE': [_model.objective.value()],
                                 'INDICES': [[np.nan]],
                                 'ELEMENTS': [[np.nan]],
                                 'SCENARIO': [_scenario_i]
                                 })

    df = pd.concat([df, cost_df])

    # All other variables
    res = tuple([v for v in _model.variables() if v.name != "Cost"])

    names = []
    values = []
    indices = []
    elements = []
    scenarios = []

    for v in res:
        full_name = v.name.split('_')
        name = full_name[0]
        # logging.info(full_name)
        if not "dummy" in v.name:
            value = v.value()
            index = variables[str(name)]['indices']
            element = full_name[1:]
            scenario = _scenario_i

            names.append(name)
            values.append(value)
            indices.append(index)
            elements.append(element)
            scenarios.append(scenario)


    other_df = pd.DataFrame(data={'NAME': names,
                                 'VALUE': values,
                                 'INDICES': indices,
                                 'ELEMENTS': elements,
                                 'SCENARIO': scenarios
                                 })

    df = pd.concat([df, other_df])
    df['REGION'] = [e[i.index('r')] if 'r' in i else np.nan for i, e in zip(df['INDICES'], df['ELEMENTS'])]
    df['REGION2'] = [e[i.index('rr')] if 'rr' in i else np.nan for i, e in zip(df['INDICES'], df['ELEMENTS'])]
    df['DAYTYPE'] = [e[i.index('ld')] if 'ld' in i else np.nan for i, e in zip(df['INDICES'], df['ELEMENTS'])]
    df['FUEL'] = [e[i.index('f')] if 'f' in i else np.nan for i, e in zip(df['INDICES'], df['ELEMENTS'])]
    df['EMISSION'] = [e[i.index('e')] if 'e' in i else np.nan for i, e in zip(df['INDICES'], df['ELEMENTS'])]
    df['DAILYTIMEBRACKET'] = [e[i.index('lh')] if 'lh' in i else np.nan for i, e in zip(df['INDICES'], df['ELEMENTS'])]
    df['SEASON'] = [e[i.index('ls')] if 'ls' in i else np.nan for i, e in zip(df['INDICES'], df['ELEMENTS'])]
    df['TIMESLICE'] = [e[i.index('l')] if 'l' in i else np.nan for i, e in zip(df['INDICES'], df['ELEMENTS'])]
    df['MODE_OF_OPERATION'] = [e[i.index('m')] if 'm' in i else np.nan for i, e in zip(df['INDICES'], df['ELEMENTS'])]
    df['STORAGE'] = [e[i.index('s')] if 's' in i else np.nan for i, e in zip(df['INDICES'], df['ELEMENTS'])]
    df['TECHNOLOGY'] = [e[i.index('t')] if 't' in i else np.nan for i, e in zip(df['INDICES'], df['ELEMENTS'])]
    df['YEAR'] = [e[i.index('y')] if 'y' in i else np.nan for i, e in zip(df['INDICES'], df['ELEMENTS'])]
    df.drop(columns={'INDICES', 'ELEMENTS'}, inplace=True)
    return df


def saveResultsToCSV(dataframe, fileDir, fileName):
    """
    This function saves all results to a CSV file.
    """
    _df = dataframe
    # Shorten abstract variable names
    _df['NAME'].replace(
        regex={'Total': 'Tot', 'Annual': 'Ann', 'Technology': 'Tech', 'Discounted': 'Disc', 'Production': 'Prod'},
        inplace=True)

    if not os.path.exists(fileDir):
        os.makedirs(fileDir)
    _df.to_csv(path_or_buf=os.path.join(fileDir, fileName), sep=',', index=False)
    for i in _df['NAME'].unique():
            _df[_df['NAME'] == i].to_csv(path_or_buf=os.path.join(fileDir, f"{i}.csv"), sep=',', index=False, mode='wt')
    return


def saveResultsToExcel(dataframe, fileDir, fileName):
    """
    This function saves all results to an Excel file.
    """
    _df = dataframe
    # Shorten abstract variable names to keep Excel worksheet name limit of 31 characters
    _df['NAME'].replace(
        regex={'Total': 'Tot', 'Annual': 'Ann', 'Technology': 'Tech', 'Discounted': 'Disc', 'Production': 'Prod', 'Emission': 'EM', 'Penalty': 'Pen'},
        inplace=True)

    dataframe_list = [_df[_df['NAME'] == str(name)] for name in _df['NAME'].unique()]

    if not os.path.exists(fileDir):
        os.makedirs(fileDir)

    writer = pd.ExcelWriter(os.path.join(fileDir, fileName))

    for d, name in zip(dataframe_list, _df['NAME'].unique()):
        d.to_excel(writer, sheet_name=name, index=False)

    writer.save()
    return

def create_df(inputDir):
    files = os.listdir('data')
    inputDir = "data"
    df = pd.DataFrame()
    sets_df = pd.DataFrame()
    Setslist = ["REGION","REGION2","DAYTYPE", "EMISSION","FUEL","DAILYTIMEBRACKET","SEASON","TIMESLICE","STORAGE","MODE_OF_OPERATION","TECHNOLOGY","YEAR"]
    for i in files:
        if i.replace('.csv', '') not in Setslist:
            dftemp = pd.read_csv(os.path.join(inputDir, i))
            dftemp = dftemp.reindex(columns=["PARAM","VALUE", "REGION","REGION2","DAYTYPE", "EMISSION","FUEL","DAILYTIMEBRACKET","SEASON","TIMESLICE","STORAGE","MODE_OF_OPERATION","TECHNOLOGY","YEAR",])
            dftemp['PARAM'] = i.replace('.csv', '')
            df = pd.concat([df, dftemp])
        elif i.replace('.csv', '') in Setslist:
            dftempsets = pd.read_csv(os.path.join(inputDir, i))
            setslist = dftempsets['VALUE'].to_list()
            dftempsetsdup = pd.DataFrame()
            dftempsetsdup[str(i.replace('.csv', ''))] = setslist
            sets_df = pd.concat([sets_df, dftempsetsdup],axis=1)
    df.to_excel('inputs.xlsx')
    return(df, sets_df)

def discount_factor(df, sets_df, defaults_df):
    df_drtech = df[df['PARAM'] == 'DiscountRateTech']
    techlist = df_drtech['TECHNOLOGY'].to_list()
    vallist = df_drtech['VALUE'].to_list()
    reglist = df_drtech['REGION'].to_list()
    sets_df1 = sets_df[sets_df['TECHNOLOGY']!= 'nan']
    for i in sets_df1['TECHNOLOGY']:
            if i not in df_drtech['TECHNOLOGY'].unique():
                techlist.append(i)
                vallist.append(defaults_df[defaults_df['PARAM'] == 'DiscountRate']['VALUE'].item())
                reglist.append(sets_df['REGION'][0])

    df_drtechnew = pd.DataFrame()
    df_drtechnew['REGION'] = reglist
    df_drtechnew['VALUE'] = vallist
    df_drtechnew['TECHNOLOGY'] = techlist

    df_op = df[df['PARAM'] == 'OperationalLife']
    techlist1 = df_op['TECHNOLOGY'].to_list()
    vallist1 = df_op['VALUE'].to_list()
    reglist1 = df_op['REGION'].to_list()
    for i in sets_df1['TECHNOLOGY']:
            if i not in df_drtech['TECHNOLOGY'].unique():
                techlist1.append(i)
                vallist1.append(defaults_df[defaults_df['PARAM'] == 'OperationalLife']['VALUE'].item())
                reglist1.append(sets_df['REGION'][0])

    df_opnew = pd.DataFrame()
    df_opnew['REGION'] = reglist1
    df_opnew['VALUE'] = vallist1
    df_opnew['TECHNOLOGY'] = techlist1

    dr_global = defaults_df[defaults_df['PARAM'] == 'DiscountRate']['VALUE'].item()
    df_merge = pd.merge(df_drtechnew, df_opnew, on=['TECHNOLOGY', 'REGION'])
    df_merge #discoun rate individual and operational life
    

    sets_df2 = sets_df['YEAR']# years as float
    sets_df2 = sets_df2.replace('nan', np.nan)
    sets_df2 = sets_df2.dropna()
    sets_df2 = sets_df2.astype(float)

    techlist = df_merge['TECHNOLOGY'].to_list()
    vallist = df_merge['VALUE_x'].to_list() #discount rate
    val1list = df_merge['VALUE_y'].to_list() #operational life
    finalvallist = []
    finalvallist1 = []
    finalvallist2 = []
    finalyearlist = []
    finaltechlist = []
    finalregionlist = []
    

    region = df_merge['REGION'].unique()[0]
    for i in range(0,len(techlist)):
        for j in sets_df2:
            if j != 'nan':
                CRF = (1-(1+vallist[i])**(-1)) / (1-(1+vallist[i])**(-val1list[i])) #capital recovery factor
                PVA = (1-(1+dr_global)**(-val1list[i])) * (1+dr_global) / dr_global # Present Value annuity
                DF = (1+dr_global)**(j-min(sets_df2))    #discount factor
                DFmid = (1+dr_global)**(j-min(sets_df2)+0.5)
                finalvallist.append(DF)
                finalvallist1.append(CRF*PVA)
                finalvallist2.append(DFmid)
                finalyearlist.append(j)
                finaltechlist.append(techlist[i])
                finalregionlist.append(region)
    dr_f = pd.DataFrame()
    dr_f['REGION'] = finalregionlist
    dr_f['VALUE'] = finalvallist # Discount factor
    dr_f['TECHNOLOGY'] = finaltechlist
    dr_f['YEAR'] = finalyearlist
    dr_f['YEAR'] =  dr_f['YEAR'].astype('int')
    dr_f['PARAM'] = 'DiscountFactor'

    dr_f1 = pd.DataFrame()
    dr_f1['REGION'] = finalregionlist
    dr_f1['VALUE'] = finalvallist1 # Factor CRF*PVA
    dr_f1['TECHNOLOGY'] = finaltechlist
    dr_f1['YEAR'] = finalyearlist
    dr_f1['YEAR'] = dr_f1['YEAR'].astype('int')
    dr_f1['PARAM'] = 'DiscountFactorIndProd'

    dr_f2 = pd.DataFrame()
    dr_f2['REGION'] = finalregionlist
    dr_f2['VALUE'] = finalvallist2 # Discoutn factor mid
    dr_f2['TECHNOLOGY'] = finaltechlist
    dr_f2['YEAR'] = finalyearlist
    dr_f2['YEAR'] = dr_f1['YEAR'].astype('int')
    dr_f2['PARAM'] = 'DiscountFactorMid'

    return dr_f, dr_f1, dr_f2