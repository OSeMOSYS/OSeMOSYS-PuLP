# Post processing for OSeMOSYS short

import pandas as pd
from .OSeMOSYS_PULP_functions import *
def postprocessing(res_df, df, sets_df, defaults_df):
    #Setup
    defaults_df = defaults_df
    roa = res_df[res_df['NAME']=='RateOfActivity'].copy()
    roa['YEAR'] = roa['YEAR'].astype(int)
    roa['MODE_OF_OPERATION'] = roa['MODE_OF_OPERATION'].astype(int)
    roa['TIMESLICE'] = roa['TIMESLICE'].astype(int)
    NSC = res_df[res_df['NAME']=='NewStorageCapacity'].copy()
    NSC['YEAR'] = NSC['YEAR'].astype(int)
    oar = df[df['PARAM']=='OutputActivityRatio']
    oar = oar[oar['VALUE'] >0].copy(deep=False)
    oar_f = oar[['FUEL', 'MODE_OF_OPERATION', 'TECHNOLOGY', 'YEAR', 'VALUE']].copy()
    oar_f['YEAR'] = oar_f['YEAR'].astype(int)
    oar_f['MODE_OF_OPERATION'] = oar_f['MODE_OF_OPERATION'].astype(int)
    #oar_f['TECHNOLOGY'] = oar_f['MODE_OF_OPERATION'].astype(str)
    iar = df[df['PARAM']=='InputActivityRatio']
    iar_f = iar[['FUEL', 'MODE_OF_OPERATION', 'TECHNOLOGY', 'YEAR', 'VALUE']].copy()
    iar_f['YEAR'] = iar_f['YEAR'].astype(int)
    iar_f['MODE_OF_OPERATION'] = iar_f['MODE_OF_OPERATION'].astype(int)
    ear = df[df['PARAM']=='EmissionActivityRatio']
    ear_f = ear[['EMISSION', 'MODE_OF_OPERATION', 'TECHNOLOGY', 'YEAR', 'VALUE']].copy()
    ear_f['YEAR'] = ear_f['YEAR'].astype(int)
    ear_f['MODE_OF_OPERATION'] = ear_f['MODE_OF_OPERATION'].astype(int)
    dr = df[df['PARAM']=='DiscountRateTech']
    dr_f = dr[['TECHNOLOGY', 'VALUE']].copy()
    
    #ep_f = df[df['PARAM']=='EmissionsPenalty'][['EMISSION', 'YEAR', 'VALUE']].copy()
    #if (ep_f['VALUE']!=0).any():
    #    ep_f['YEAR'] = ep_f['YEAR'].astype(int)
    #else:
    #    pass
    
    ys = df[df['PARAM']=='YearSplit']
    ys_f = ys[['TIMESLICE', 'YEAR', 'VALUE']].copy()
    ys_f['YEAR'] = ys_f['YEAR'].astype(int)
    ys_f['TIMESLICE'] = ys_f['TIMESLICE'].astype(int)
    omoo = df[df['PARAM']=='OutputModeofoperation']
    omoo_f = omoo[['MODE_OF_OPERATION', 'TECHNOLOGY', 'YEAR', 'VALUE']].copy()
    omoo_f['MODE_OF_OPERATION'] = omoo_f['MODE_OF_OPERATION'].astype(int)
    NSC = res_df[res_df['NAME']=='NewStorageCapacity'].copy()
    NSC['YEAR'] = NSC['YEAR'].astype(int)

    if len(sets_df['STORAGE']) != 0:
        CCS = df[df['PARAM']=='CapitalCostStorage']
        CCS = CCS[['REGION', 'STORAGE', 'YEAR', 'VALUE']].copy()
        drs = df[df['PARAM']=='DiscountRateSto']
        drs_f = drs[['STORAGE', 'VALUE']].copy()
    #Production By technology
    df_merge = pd.merge(roa, oar_f, on=['MODE_OF_OPERATION', 'TECHNOLOGY', 'YEAR'])
    df_merge = pd.merge(df_merge, ys_f, on=['TIMESLICE', 'YEAR'])
    namelist = []
    for i in range(0,len(df_merge)):
        namelist.append('ProductionByTechnology')
    df_PBT = df_merge
    df_PBT['VALUE_r'] = df_PBT['VALUE'] * df_PBT['VALUE_x'] * df_PBT['VALUE_y']
    df_PBT['NAME'] = namelist
    df_PBT = df_PBT.drop(['VALUE_x', 'VALUE', 'VALUE_y', 'FUEL_x'], axis=1)
    df_PBT.rename(columns = {'VALUE_r':'VALUE', 'FUEL_y': 'FUEL' }, inplace = True)
    res_df = pd.concat([res_df, df_PBT], ignore_index=True, sort=False)

    #ProductionbyTechnologyAnnual

    df2 = df_PBT.groupby(['YEAR', 'TECHNOLOGY', 'NAME', 'FUEL']).sum()
    df2=df2.reset_index()
    namelist = []
    for i in range(0, len(df2)):
        namelist.append('ProductionByTechnologyAnnual')
    df2['NAME'] = namelist
    res_df = pd.concat([res_df, df2], ignore_index=True, sort=False)
    
    df_merge = pd.merge(roa, iar_f, on=['MODE_OF_OPERATION', 'TECHNOLOGY', 'YEAR'])
    df_merge = pd.merge(df_merge, ys_f, on=['TIMESLICE', 'YEAR'])

    #Use By technology
    namelist = []
    for i in range(0,len(df_merge)):
        namelist.append('UseByTechnology')
    df_UBT = df_merge
    df_UBT['VALUE_r'] = df_UBT['VALUE'] * df_UBT['VALUE_x'] * df_UBT['VALUE_y']
    df_UBT['NAME'] = namelist
    df_UBT = df_UBT.drop(['VALUE_x', 'VALUE', 'VALUE_y', 'FUEL_x'], axis=1)
    df_UBT.rename(columns = {'VALUE_r':'VALUE', 'FUEL_y': 'FUEL' }, inplace = True)
    res_df = pd.concat([res_df, df_UBT], ignore_index=True, sort=False)

    #UsebyTechnologyAnnual

    df2 = df_UBT.groupby(['YEAR', 'TECHNOLOGY', 'NAME']).sum()
    df2=df2.reset_index()
    namelist = []
    for i in range(0, len(df2)):
        namelist.append('UseByTechnologyAnnual')
    df2['NAME'] = namelist
    res_df = pd.concat([res_df, df2], ignore_index=True, sort=False)
    
    #AccumulatedNewCapacity
    newcap = res_df[res_df['NAME'] == 'NewCapacity']
    oplife = df[df['PARAM'] == 'OperationalLife'].copy()
    oplife = oplife[['PARAM', 'VALUE', 'TECHNOLOGY']]
    df_merge = pd.merge(oplife, newcap, on=['TECHNOLOGY'])

    ACC_df = pd.DataFrame()
    techlist = df_merge['TECHNOLOGY'].unique()
    for i in techlist:
        dfint = df_merge[df_merge['TECHNOLOGY'] == str(i)].copy()
        corvallist = []
        vallist = dfint['VALUE_y'].to_list()
        oplife = dfint['VALUE_x'].unique()[0]
        yearlist = dfint['YEAR'].to_list()
        for y in dfint['YEAR']:
            sum = 0
            for i in range(0, len(vallist)):
                if int(y) - int(yearlist[i]) >=0 and int(y) - int(yearlist[i]) < oplife:
                    sum = sum + vallist[i]
            corvallist.append(sum)
    newcap = res_df[res_df['NAME'] == 'NewCapacity']
    oplife = df[df['PARAM'] == 'OperationalLife'].copy()
    oplife = oplife[['PARAM', 'VALUE', 'TECHNOLOGY']]
    df_merge = pd.merge(oplife, newcap, on=['TECHNOLOGY'])

    ACC_df = pd.DataFrame()
    techlist = df_merge['TECHNOLOGY'].unique()
    for i in techlist:
        dfint = df_merge[df_merge['TECHNOLOGY'] == str(i)].copy()
        corvallist = []
        vallist = dfint['VALUE_y'].to_list()
        oplife = dfint['VALUE_x'].unique()[0]
        yearlist = dfint['YEAR'].to_list()
        for y in dfint['YEAR']:
            sum = 0
            for i in range(0, len(vallist)):
                if int(y) - int(yearlist[i]) >=0 and int(y) - int(yearlist[i]) < oplife:
                    sum = sum + vallist[i]
            corvallist.append(sum)
        dfint['VALUE'] = corvallist
        ACC_df = pd.concat([ACC_df, dfint], ignore_index=True, sort=False)
    namelist = []
    for i in range (0, len(ACC_df)):
        namelist.append('AccumulatedNewCapacity')
    ACC_df['NAME'] = namelist
    ACC_df = ACC_df.drop(['VALUE_x', 'PARAM', 'VALUE_y'], axis=1)
    res_df = pd.concat([res_df, ACC_df], ignore_index=True, sort=False)

    #AnnualTechnologyEmission
    df_merge = pd.merge(roa, ear_f, on=['MODE_OF_OPERATION', 'TECHNOLOGY', 'YEAR'])
    df_merge = pd.merge(df_merge, ys_f, on=['TIMESLICE', 'YEAR'])
    df_EBT = df_merge
    df_EBT['VALUE_r'] = df_EBT['VALUE'] * df_EBT['VALUE_x'] * df_EBT['VALUE_y']
    df_EBT = df_EBT.drop(['VALUE_x', 'VALUE', 'VALUE_y', 'EMISSION_x'], axis=1)
    df_EBT.rename(columns = {'VALUE_r':'VALUE', 'EMISSION_y': 'EMISSION' }, inplace = True)
    df2 = df_EBT.groupby(['YEAR', 'TECHNOLOGY', 'NAME', 'EMISSION']).sum()
    df2=df2.reset_index()
    namelist = []
    for i in range(0, len(df2)):
        namelist.append('AnnualTechnologyEmission')
    df2['NAME'] = namelist
    res_df = pd.concat([res_df, df2], ignore_index=True, sort=False)

    #DiscountedTechnologyEmissionsPenalty
    #if len(ep_f) != 0:
    #    ate = res_df[res_df['NAME']=='AnnualTechnologyEmission'].copy()
    #    df_merge = pd.merge(ate, ep_f, on=['EMISSION', 'YEAR'])
    #    df_merge = pd.merge(df_merge, dr_f, on=['TECHNOLOGY'])
    #    df_DEP = df_merge
    #    df_DEP['VALUE_r'] = df_DEP['VALUE_x'] * df_DEP['VALUE_y'] * ( 1 / (1 + df_DEP['VALUE'])**(df_DEP['YEAR'] - min(df_DEP['YEAR'])))
    #    df_DEP = df_DEP.drop(['VALUE_x', 'VALUE', 'VALUE_y'], axis=1)
    #    df_DEP.rename(columns = {'VALUE_r':'VALUE' }, inplace = True)
    #    namelist = []
    #    for i in range(0, len(df_DEP)):
    #        namelist.append('DiscountedTechnologyEmissionsPenalty')
    #    df_DEP['NAME'] = namelist
    #    res_df = pd.concat([res_df, df_DEP], ignore_index=True, sort=False)

    #TotalCapacityAnnual

    # Extract Residual Capacity and New Capacity data
    rescap = df[df['PARAM']=='ResidualCapacity'][['TECHNOLOGY', 'YEAR', 'VALUE', 'REGION']].copy()
    rescap['YEAR'] = rescap['YEAR'].astype(float)

    all_years = pd.DataFrame({'YEAR': sets_df['YEAR']})
    all_years['YEAR'] = all_years['YEAR'].astype(float)

    # Step 3: Use a Cartesian product to create rows for every year for every technology
    full_df = pd.DataFrame()

    techs = rescap['TECHNOLOGY'].unique()
    for tech in techs:
        tech_df = all_years.copy()
        tech_df['TECHNOLOGY'] = tech
        tech_df['PARAM'] = 'ResidualCapacity'
        tech_df['REGION'] = sets_df['REGION'][0]


    # Merge with the original df to fill in missing years with 0
        merged_df = pd.merge(tech_df, rescap[rescap['TECHNOLOGY'] == tech], how='left', on=['YEAR', 'TECHNOLOGY', 'REGION'])
        
        # Fill missing 'VALUE' entries with 0
        merged_df['VALUE'] = merged_df['VALUE'].fillna(0)
        
        # Append to full DataFrame
        full_df = pd.concat([full_df, merged_df])

    # Step 4: Reset index and print the final DataFrame
    full_df.reset_index(drop=True, inplace=True)

    # Step 4: Repalce fulldf with rescap
    rescap = full_df

    techlistres = []
    vallistres = []
    yearlistres = []
    reglistres = []
    for j in  sets_df['TECHNOLOGY']:
        if j!= 'nan':
            if j not in rescap['TECHNOLOGY'].unique():
                for i in sets_df['YEAR']:
                    if i!= 'nan':
                        techlistres.append(j)
                        vallistres.append(defaults_df[defaults_df['PARAM'] == 'ResidualCapacity']['VALUE'].item())
                        reglistres.append(sets_df['REGION'][0])
                        yearlistres.append(int(float(i)))
    rescap_new = pd.DataFrame()
    rescap_new['REGION'] = reglistres
    rescap_new['VALUE'] = vallistres
    rescap_new['TECHNOLOGY'] = techlistres   
    rescap_new['YEAR'] = yearlistres
    rescap_new['YEAR'] = rescap_new['YEAR'].astype(float)
    rescap_new['YEAR'] = rescap_new['YEAR'].astype(int)
    rescap = pd.concat([rescap, rescap_new], axis=0)
    newcap = res_df[res_df['NAME'] == 'AccumulatedNewCapacity'][['TECHNOLOGY', 'YEAR', 'VALUE']].copy()
    newcap['YEAR'] = newcap['YEAR'].astype(int)
    #merge
    df_merge = pd.merge(rescap, newcap, on=['TECHNOLOGY', 'YEAR'])
    #Calculate totCapAnn
    df_merge['VALUE'] = df_merge['VALUE_x'] + df_merge['VALUE_y']
    df_merge['NAME'] = 'TotalCapacityAnnual'
    #Remove columns
    df_merge = df_merge.drop(['VALUE_x', 'VALUE_y',], axis=1)
    res_df = pd.concat([res_df, df_merge], ignore_index=True, sort=False)


    #DiscountedCapitalInvestment
    capcost = df[df['PARAM']=='CapitalCost'][['TECHNOLOGY', 'YEAR', 'VALUE']]
    newcap = res_df[res_df['NAME'] == 'NewCapacity'][['TECHNOLOGY', 'YEAR', 'VALUE']]
    newcap['YEAR']=newcap['YEAR'].astype(int)
    
    df_merge = pd.merge(capcost, newcap, on=['TECHNOLOGY', 'YEAR'])
    df_merge['YEAR']=df_merge['YEAR'].astype(int)
    
    dr_f = discount_factor(df=df, sets_df=sets_df, defaults_df=defaults_df)[0]
    df_merge = pd.merge(df_merge, dr_f, on=['TECHNOLOGY', 'YEAR'])
    
    df_merge['VALUE_r'] = df_merge['VALUE_x'] * df_merge['VALUE_y'] * df_merge['VALUE'] 
    df_merge = df_merge.drop(['VALUE_x', 'VALUE', 'VALUE_y'], axis=1)
    df_merge.rename(columns = {'VALUE_r':'VALUE' }, inplace = True)
    namelist = []
    for i in range(0, len(df_merge)):
        namelist.append('DiscountedCapitalInvestment')
    df_merge['NAME'] = namelist
    res_df = pd.concat([res_df, df_merge], ignore_index=True, sort=False)

    #AnnualFixedOperatingCost
    fixcost = df[df['PARAM']=='FixedCost']
    techlistfix = []
    vallistfix = []
    yearlistfix = []
    reglistfix = []
    for j in  sets_df['TECHNOLOGY']:
        if j!= 'nan':
            if j not in fixcost['TECHNOLOGY'].unique():
                for i in sets_df['YEAR']:
                    if i!= 'nan':
                        techlistfix.append(j)
                        vallistfix.append(defaults_df[defaults_df['PARAM'] == 'FixedCost']['VALUE'].item())
                        reglistfix.append(sets_df['REGION'][0])
                        yearlistfix.append(int(float(i)))
    fix_new = pd.DataFrame()
    fix_new['REGION'] = reglistfix
    fix_new['VALUE'] = vallistfix
    fix_new['TECHNOLOGY'] = techlistfix    
    fix_new['YEAR'] = yearlistfix
    fix_new['YEAR'] = fix_new['YEAR'].astype(float)
    fix_new['YEAR'] = fix_new['YEAR'].astype(int)
    fixcost = fixcost[['TECHNOLOGY', 'VALUE', 'YEAR', 'REGION']].copy()
    fixcost = pd.concat([fixcost, fix_new], axis=0)
    newcap = res_df[res_df['NAME'] == 'TotalCapacityAnnual']
    df_merge = pd.merge(fixcost, newcap, on=['TECHNOLOGY', 'YEAR'])
    df_merge['YEAR'] = df_merge['YEAR'].astype(int)
    df_merge['VALUE_r'] = df_merge['VALUE_x'] * df_merge['VALUE_y']
    df_merge = df_merge.drop(['VALUE_x', 'VALUE_y'], axis=1)
    df_merge.rename(columns = {'VALUE_r':'VALUE' }, inplace = True)
    namelist = []
    for i in range(0, len(df_merge)):
        namelist.append('AnnualFixedOperatingCost')
    df_merge['NAME'] = namelist
    res_df = pd.concat([res_df, df_merge], ignore_index=True, sort=False)
    


    #AnnualVariableOperatingCost
    varcost = df[df['PARAM']=='VariableCost']
    if len(varcost['TIMESLICE'].unique()) == 1 and varcost['TIMESLICE'].unique()[0] == '<NA>':
        varcost = varcost[['MODE_OF_OPERATION', 'TECHNOLOGY', 'YEAR', 'VALUE', 'REGION']].copy()
        techlistvar = []
        vallistvar = []
        yearlistvar = []
        reglistvar = []
        moolistvar = []
        for j in  sets_df['TECHNOLOGY']:
            if j!= 'nan':
                if j not in rescap['TECHNOLOGY'].unique():
                    for k in sets_df['MODE_OF_OPERATION']:
                        if k!= 'nan':
                            for i in sets_df['YEAR']:
                                if i!= 'nan':
                                    techlistvar.append(j)
                                    vallistvar.append(defaults_df[defaults_df['PARAM'] == 'VariableCost']['VALUE'].item())
                                    reglistvar.append(sets_df['REGION'][0])
                                    yearlistvar.append(int(float(i)))
                                    moolistvar.append(int(float(i)))
        varcost_new = pd.DataFrame()
        varcost_new['REGION'] = reglistvar
        varcost_new['VALUE'] = vallistvar
        varcost_new['TECHNOLOGY'] = techlistvar   
        varcost_new['YEAR'] = yearlistvar
        varcost_new['MODE_OF_OPERATION'] = moolistvar
        varcost_new['YEAR'] = varcost_new['YEAR'].astype(float)
        varcost_new['YEAR'] = varcost_new['YEAR'].astype(int)
        varcost = pd.concat([varcost, varcost_new], axis=0)
        varcost['YEAR'] = varcost['YEAR'].astype(int)
        varcost['MODE_OF_OPERATION'] = varcost['MODE_OF_OPERATION'].astype(int)
        df_merge = pd.merge(roa, varcost, on=['MODE_OF_OPERATION', 'TECHNOLOGY', 'YEAR'])
        df_merge = pd.merge(df_merge, ys_f, on=['TIMESLICE', 'YEAR'])
        df_merge['VALUE_r'] = df_merge['VALUE'] * df_merge['VALUE_x'] * df_merge['VALUE_y']
        df_merge['VALUE_r'] = df_merge['VALUE_r'].astype(float)
        df_merge = df_merge.drop(['VALUE_x', 'VALUE', 'VALUE_y'], axis=1)
        df_merge.rename(columns = {'VALUE_r':'VALUE'}, inplace = True)
        df_merge = df_merge.groupby(['YEAR', 'TECHNOLOGY', 'NAME']).sum()
        df_merge=df_merge.reset_index()
        namelist = []
        for i in range(0, len(df_merge)):
            namelist.append('AnnualVariableOperatingCost')
        df_merge['NAME'] = namelist
    else:
        varcost = varcost[['MODE_OF_OPERATION', 'TECHNOLOGY', 'YEAR', 'VALUE', 'REGION', 'TIMESLICE']].copy()
        techlistvar = []
        vallistvar = []
        yearlistvar = []
        reglistvar = []
        moolistvar = []
        tslistvar = []
        for j in  sets_df['TECHNOLOGY']:
            if j!= 'nan':
                if j not in rescap['TECHNOLOGY'].unique():
                    for k in sets_df['MODE_OF_OPERATION']:
                        if k!= 'nan':
                            for i in sets_df['YEAR']:
                                if i!= 'nan':
                                    for m in sets_df['TIMESLICE']:
                                        if i!= 'nan':
                                            techlistvar.append(j)
                                            vallistvar.append(defaults_df[defaults_df['PARAM'] == 'VariableCost']['VALUE'].item())
                                            reglistvar.append(sets_df['REGION'][0])
                                            yearlistvar.append(int(float(i)))
                                            moolistvar.append(int(float(i)))
                                            tslistvar.append(int(float(m)))
        varcost_new = pd.DataFrame()
        varcost_new['REGION'] = reglistvar
        varcost_new['VALUE'] = vallistvar
        varcost_new['TECHNOLOGY'] = techlistvar   
        varcost_new['YEAR'] = yearlistvar
        varcost_new['MODE_OF_OPERATION'] = moolistvar
        varcost_new['TIMESLICE'] = tslistvar
        varcost_new['YEAR'] = varcost_new['YEAR'].astype(float)
        varcost_new['YEAR'] = varcost_new['YEAR'].astype(int)
        varcost = pd.concat([varcost, varcost_new], axis=0)
        varcost['YEAR'] = varcost['YEAR'].astype(int)
        varcost['TIMESLICE'] = varcost['TIMESLICE'].astype(int)
        varcost['MODE_OF_OPERATION'] = varcost['MODE_OF_OPERATION'].astype(int)
        df_merge = pd.merge(roa, varcost, on=['MODE_OF_OPERATION', 'TECHNOLOGY', 'YEAR','TIMESLICE'])
        df_merge = pd.merge(df_merge, ys_f, on=['TIMESLICE', 'YEAR'])
        df_merge['VALUE_r'] = df_merge['VALUE'] * df_merge['VALUE_x'] * df_merge['VALUE_y']
        df_merge['VALUE_r'] = df_merge['VALUE_r'].astype(float)
        df_merge = df_merge.drop(['VALUE_x', 'VALUE', 'VALUE_y'], axis=1)
        df_merge.rename(columns = {'VALUE_r':'VALUE'}, inplace = True)
        df_merge = df_merge.groupby(['YEAR', 'TECHNOLOGY', 'NAME',]).sum()
        df_merge=df_merge.reset_index()
        namelist = []
        for i in range(0, len(df_merge)):
            namelist.append('AnnualVariableOperatingCost')
        df_merge['NAME'] = namelist
    res_df = pd.concat([res_df, df_merge], ignore_index=True, sort=False)

    #DiscountedOperatingCost
    avc = res_df[res_df['NAME']=='AnnualVariableOperatingCost'].copy()
    avc = avc[['TECHNOLOGY', 'YEAR', 'VALUE']].copy()
    afc = res_df[res_df['NAME']=='AnnualFixedOperatingCost'].copy()
    afc = afc[['TECHNOLOGY', 'YEAR', 'VALUE']].copy()
    df_merge = pd.merge(afc, avc, on=['TECHNOLOGY', 'YEAR'])
    df_merge = pd.merge(df_merge, dr_f, on=['TECHNOLOGY', 'YEAR'])
    df_merge['VALUE_r'] = (df_merge['VALUE_x'] + df_merge['VALUE_y']) * ( 1 / (1 + df_merge['VALUE'])**(df_merge['YEAR'] - min(df_merge['YEAR'])))
    df_merge = df_merge.drop(['VALUE_x', 'VALUE', 'VALUE_y'], axis=1)
    df_merge.rename(columns = {'VALUE_r':'VALUE' }, inplace = True)
    namelist = []
    for i in range(0, len(df_merge)):
        namelist.append('DiscountedOperatingCost')
    df_merge['NAME'] = namelist
    res_df = pd.concat([res_df, df_merge], ignore_index=True, sort=False)

    #TotalTechnologyAnnualActivity
   
    df_merge = pd.merge(roa, omoo_f, on=['MODE_OF_OPERATION', 'TECHNOLOGY', 'YEAR'])
    df_merge = pd.merge(df_merge, ys_f, on=['TIMESLICE', 'YEAR'])
    df_merge['VALUE_r'] = df_merge['VALUE'] * df_merge['VALUE_x'] * df_merge['VALUE_y']
    df_merge['VALUE_r']  = df_merge['VALUE_r'].astype(float)
    df_merge = df_merge.drop(['VALUE_x', 'VALUE', 'VALUE_y'], axis=1)
    df_merge.rename(columns = {'VALUE_r':'VALUE'}, inplace = True)
    df_merge = df_merge.groupby(['YEAR', 'TECHNOLOGY', 'NAME']).sum()
    df_merge=df_merge.reset_index()
    namelist = []
    for i in range(0, len(df_merge)):
        namelist.append('TotalTechnologyAnnualActivity')
    df_merge['NAME'] = namelist
    res_df = pd.concat([res_df, df_merge], ignore_index=True, sort=False)

    #TotalTechnologyModelPeriodActivity
    TTA = res_df[res_df['NAME']=='TotalTechnologyAnnualActivity'].copy()
    TTA['YEAR'] = TTA['YEAR'].astype(str)
    TTA['VALUE'] = TTA['VALUE'].astype(float)
    TMA = TTA.groupby(['TECHNOLOGY', 'NAME']).sum()
    TMA=TMA.reset_index()
    namelist = []
    for i in range(0, len(TMA)):
        namelist.append('TotalTechnologyModelPeriodActivity')
    TMA['NAME'] = namelist
    res_df = pd.concat([res_df, TMA], ignore_index=True, sort=False)

    #DiscountedCapitalInvestmentStorage
    if len(res_df[res_df['NAME']=='NewStorageCapacity'])!= 0:
        
        if len(sets_df['STORAGE']) != 0:
            stolist = CCS['STORAGE'].to_list()
            vallist = CCS['VALUE'].to_list()
            reglist = CCS['REGION'].to_list()
            yearlist = CCS['YEAR'].to_list()
            sets_df1 = sets_df[sets_df['STORAGE']!= 'nan']
            for i in sets_df1['STORAGE']:
                if i not in CCS['STORAGE'].unique():
                    for j in  sets_df['YEAR']:
                        if j!= 'nan':
                            stolist.append(i)
                            vallist.append(defaults_df[defaults_df['PARAM'] == 'CapitalCostStorage']['VALUE'].item())
                            reglist.append(sets_df['REGION'][0])
                            yearlist.append(j)

            CCS_new = pd.DataFrame()
            CCS_new['REGION'] = reglist
            CCS_new['VALUE'] = vallist
            CCS_new['STORAGE'] = stolist    
            CCS_new['YEAR'] = yearlist
            CCS_new['YEAR'] = CCS_new['YEAR'].astype(float)
            df_merge = pd.merge(CCS_new, NSC, on=['STORAGE', 'YEAR'])
            
            stolist = drs_f['STORAGE'].to_list()
            vallist = drs_f['VALUE'].to_list()
            sets_df1 = sets_df[sets_df['STORAGE']!= 'nan']
            for i in sets_df1['STORAGE']:
                    if i not in drs_f['STORAGE'].unique():
                        stolist.append(i)
                        vallist.append(defaults_df[defaults_df['PARAM'] == 'DiscountRateSto']['VALUE'].item())

            drs_fnew = pd.DataFrame()
            drs_fnew['VALUE'] = vallist
            drs_fnew['STORAGE'] = stolist
            df_merge = pd.merge(df_merge, drs_fnew, on=['STORAGE'])
            
            df_merge['YEAR'] = df_merge['YEAR'].astype(int)
            df_merge['VALUE_r'] = df_merge['VALUE_x'] * df_merge['VALUE_y'] * ( 1 / (1 + df_merge['VALUE'])**(df_merge['YEAR'] - min(df_merge['YEAR'])))
            df_merge = df_merge.drop(['VALUE_x', 'VALUE', 'VALUE_y'], axis=1)
            df_merge.rename(columns = {'VALUE_r':'VALUE' }, inplace = True)
            namelist = []
            for i in range(0, len(df_merge)):
                namelist.append('DiscountedCapitalInvestmentStorage')
            df_merge['NAME'] = namelist
            res_df = pd.concat([res_df, df_merge], ignore_index=True, sort=False)

        #ModelPeriodEmissions
        ate = res_df[res_df['NAME']=='AnnualTechnologyEmission'].copy()
        ate['YEAR'] = ate['YEAR'].astype(str)
        ate['VALUE'] = ate['VALUE'].astype(float)
        mpe = ate.groupby(['EMISSION', 'NAME']).sum()
        mpe=mpe.reset_index()
        namelist = []
        for i in range(0, len(mpe)):
            namelist.append('ModelPeriodEmissions')
        mpe['NAME'] = namelist
        res_df = pd.concat([res_df, mpe], ignore_index=True, sort=False)
    else:
        pass
    return res_df
    


