import pandas as pd

from glob import glob

#%% Men's Table

ROOT = 'data/2024_07/'
file_list_men = glob('all_time_men*.csv', root_dir=ROOT)

dfs = None
for file in file_list_men:
    df = pd.read_csv(ROOT + file)
    
    if dfs is None:
        dfs = df.assign(event=file.split('_')[-1].split('.')[0])
        continue

    dfs = pd.concat([dfs, df.assign(event=file.split('_')[-1].split('.')[0])])

dfs.to_csv(ROOT + 'all_time_men_all_events.csv', index=False)


#%% Women's Table
file_list_women = glob('all_time_women*.csv', root_dir=ROOT)

dfs = None
for file in file_list_women:
    df = pd.read_csv(ROOT + file)
    
    if dfs is None:
        dfs = df.assign(event=file.split('_')[-1].split('.')[0])
        continue

    dfs = pd.concat([dfs, df.assign(event=file.split('_')[-1].split('.')[0])])

dfs.to_csv(ROOT + 'all_time_women_all_events.csv', index=False)
