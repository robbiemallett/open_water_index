from netCDF4 import Dataset
import pandas as pd
import numpy as np
import os
import datetime
import tqdm
from ll_xy import lonlat_to_xy
import pickle

sic_dir = '/Data/romal7177/ResearchData/IFT/EarthObservation/SatelliteAltimetry/OSISAF Sea Ice Concentration'
year=2003
f = 'ice_conc_nh_ease2-250_cdr-v2p0_200303101200.nc'

d = Dataset(f'{sic_dir}/{year}/{f}')

lons = np.array(d['lon'])
lats = np.array(d['lat'])
xgrid,ygrid=lonlat_to_xy(lons,lats,hemisphere='n')

icecaplocs = {'austfonna':(24.017,79.833),'flade':(-15.70,81.29)}
#https://journals.sagepub.com/doi/pdf/10.1191/0959683605hl820rp
#https://nbi.ku.dk/english/theses/masters-theses/andreas-lemark/A_Lemark_Speciale.pdf

for loc in ['flade','austfonna']:

    print(loc)

    for threshold in np.arange(100,1000,100):

        thresh_code = str(threshold)
        dist_thresh=threshold*1000
        print(thresh_code)
        
        aust_x,aust_y = lonlat_to_xy(np.array(icecaplocs[loc][0]),np.array(icecaplocs[loc][1]),hemisphere='n')
        
        distances_to_austfonna = np.sqrt((xgrid-aust_x)**2+(ygrid-aust_y)**2)

        list_of_dicts = []
        for year in tqdm.trange(2003,2024):
            print(year)
            files = sorted(os.listdir(f'{sic_dir}/{year}'))
            
            
            for f in tqdm.tqdm(files):
                datestr = f.split('_')[-1][-15:-7]
                year = int(datestr[:4])
                month = int(datestr[4:6])
                day = int(datestr[6:8])
                dt = datetime.date(year,month,day)
                
                with Dataset(f'{sic_dir}/{year}/{f}') as d:
        
                    sic = np.array(d['ice_conc'])[0]/100
                    sic[sic<0]=np.nan
                    sic_nearby = sic.copy()
                    sic_nearby[distances_to_austfonna>dist_thresh]=np.nan
        
                    total_sic = np.nansum(sic_nearby)
        
                    dic = {'cover':total_sic,'year':year,'month':month,'day':day,'dt':dt}
        
                    list_of_dicts.append(dic)
                
        df = pd.DataFrame(list_of_dicts)
            
        pickle.dump(df,open(f'ice_cover/{thresh_code}/cover_all_{loc}.p','wb'))
