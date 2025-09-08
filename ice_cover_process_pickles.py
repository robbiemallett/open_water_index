import pandas as pd
import numpy as np
import pickle
import calendar

ice_cover_dir = '/home/romal7177/arctex/ice_cover/'

open_water_thresholds = np.arange(0.1,1,0.1)

frames = {}

for site in ['austfonna','flade']:
    radii = np.arange(100,1000,100)
    
    for radius in radii:
    
        list_of_dfs = []
    
        df = pickle.load(open(f'{ice_cover_dir}{radius}/cover_all_{site}.p','rb'))
        df['doy'] = [x.timetuple().tm_yday for x in df['dt']]
    
        max_cover = np.nanmax(df['cover'])
        
        df['norm'] = df['cover']/max_cover
    
        df.sort_values('dt',inplace=True)
    
        frames[radius] = df
    
    years = np.arange(2003,2024)
    
    data = {}
    
    for radius in radii:
        
        df = frames[radius]
        
        for thresh in open_water_thresholds:
        
            open_water_days = []
    
            for year in years:

                # do all year
    
                df_yr = df[df['year']==year]
    
                df_yr = df_yr[df_yr['norm']<thresh]

                all_days_OW = df_yr.shape[0]

                # do DJF
                
                df_yr = df[df['year']==year]

                if calendar.isleap(year): feb_days=29
                else: feb_days=28
                
                df_yr = df_yr[(df_yr['doy']<=31+feb_days)]
    
                df_yr = df_yr[df_yr['norm']<thresh]
                
                days0 =  df_yr.shape[0]
                
                df_yr = df[df['year']==year-1]
                
                df_yr = df_yr[(df_yr['doy']>=365-31)]
    
                df_yr = df_yr[df_yr['norm']<thresh]
                
                days1 =  df_yr.shape[0]
                
                DJF_days_OW = days0+days1
    
                open_water_days.append( {'year':year,'all_days_OW':all_days_OW,'DJF_days_OW':DJF_days_OW })
    
    
            data[f'{int(radius)}_{int(100*np.round(1-thresh,decimals=1))}']=pd.DataFrame(open_water_days)
    
    
    for key,df in data.items():
    
        df.to_hdf(f'{ice_cover_dir}outputs/{site}_Cover.h5',key=f'rad_thresh_{key}pc',mode='a')
