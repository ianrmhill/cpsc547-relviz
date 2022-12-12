from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import numpy as np
import pandas as pd

def seperate_ts(ms, set_idx = False):
    """
    ms (Dataframe)
    set_idx (bool): if true, create a "t_idx" labeling each respective elements
    """
    t_series = {"circuit #": [],
                "device #": [],
                "lot #": [],
                "sample #":[],
                "aggtype":[],
                "t_idx":[] } 
    t_idx = 0
    if set_idx:
        ms["t_idx"] = np.ones(len(ms))
    
    # treat t_id key to individual time series; filter by them get 1 time series
    for t_id in ms["sample #"].unique():
        cond1 = t_id == ms["sample #"]
        df_ori = ms[cond1]
        for aggtype in df_ori.aggtype.unique():
            cond2 = df_ori.aggtype == aggtype
            if set_idx:
                ms.loc[cond1 & cond2, "t_idx"] = t_idx 
            else:
                df = df_ori[cond2]
                assert df.time.unique().shape[0] == len(df)

                t_series["circuit #"].append(df["circuit #"].iloc[0])
                t_series["device #"].append(df["device #"].iloc[0])
                t_series["lot #"].append(df["lot #"].iloc[0])
                t_series["sample #"].append(df["sample #"].iloc[0])
                t_series["aggtype"].append(df["aggtype"].iloc[0])
                t_series["t_idx"].append(t_idx)

                if t_series.get("measured") is None:
                    t_series['measured'] = df['measured'].to_numpy()[None]
                else:
                    t_series["measured"] = np.concatenate([t_series["measured"], df["measured"].to_numpy()[None]])            
            t_idx += 1
    if set_idx:
        return
    return t_series

def create_table(ms):
    t_series = seperate_ts(ms)

    t_np = t_series["measured"] # get the time series; shape = (n_time_series, n_points_per_series)
    t_np = np.concatenate([t_np, np.diff(t_np)], axis = -1) # add difference as features

    # create 2d position for each time series
    pca = PCA(2)
    pca.fit(t_np)
    t_xy = pca.transform(t_np)

    # create class for each time series
    kmeans = KMeans(n_clusters=5).fit(t_xy)
    t_cs = kmeans.predict(t_xy)

    # create structured table for altair
    del t_series["measured"]
    t_series["x"] = []
    t_series["y"] = []
    t_series["k_class"] = []

    for pos, kc in zip(t_xy, t_cs):
        x, y = pos 
        t_series["x"].append(x)
        t_series["y"].append(y)
        t_series["k_class"].append(kc)
    
    return pd.DataFrame(t_series)
