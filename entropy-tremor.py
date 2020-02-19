# Steps to Calculate the Entropy of Parkinsonian Rest Tremors
    # Assuming imported files have the columns Time,AccelX,AccelY,AccelZ,RotateX,RotateY,RotateZ only

## 0. Import Relevant Libraries

import pandas as pd
from scipy.stats import zscore # normalize data. Not used.
import scipy.signal as signal
import matplotlib.pyplot as plt
import numpy as np
import sampen
import glob
import os

from sampen import sampen2
    # https://github.com/bergantine/sampen/

import sys
sys.path.insert(0, 'C:\\Users\\albei\\OneDrive\\Desktop\\entropy\\entropy\\') # replace ith directory to EntroPy
from entropy import *
    # https://github.com/raphaelvallat/entropy


## 1. Rename and Convert Files

### Choose Global Variables
prepost = "post"  # pre or post
entropy = "samen" # samen or appen


all_butter = glob.glob(os.path.join(path, "*_butter.xlsx"))  # make a list of paths
shape = len(all_butter)
entropies = {} # initialize dictionary

path = "input\\" + prepost
all_csv = glob.glob(os.path.join(path, "*.csv"))  # make a list of paths
shape = len(all_csv)

def convert(all_csv):
    ''' Converts csv to xlsx
    
    Converts and renames files. Filename must be in format of "DDMMYYY_####_[identifier_here].csv"
    '''
    i = 0
    for file in all_csv:
        csv_file = file.split(sep='\\')[2][14:-4] # get file's name without extension
        dir_path = os.path.dirname(os.path.realpath(file)) # get the csv file's current directory
        xlsx_file = dir_path + "\\"+ csv_file + ".xlsx" # save csv file in current directory
        pd.read_csv(file, delimiter= ",").to_excel(xlsx_file, index=False)
        i = i + 1
        print("||",i, "/", shape, " FINISHED! || ", csv_file)
    print("All files converted and saved in ", path)

convert(all_csv)

## 2. Butterworth Filtering
all_xlsx = glob.glob(os.path.join(path, "*.xlsx"))  # make a list of paths
shape = len(all_xlsx)

def butter_filter(all_xlsx):
    ''' Butters up raw data through 4th order filter with 30hz cutoff frequency
    
    Pass all data through butter filter. Paper by Gil, et al (2010) said they passed it 
    through 4th order butter filter with 30hz cutoff frequency
    '''
    i = 0
    for file in all_xlsx:
        # Setup
        i = i+1
        df = pd.read_excel(file)
        cols = df.columns[1:] # all columns except time
        butter_dic = {}
        butter_dic['Time'] = df['Time']
        
        # Design the Buterworth filter
        N  = 4    # Filter order
        Wn = 0.3 # Cutoff frequency
        B, A = signal.butter(N, Wn, output='ba')

        # Second, apply the filter
        for col in cols:    
            tremor = np.array(df[col]) # butter only takes arrays
            tremor_f = signal.filtfilt(B,A, tremor)
            butter_dic[col] = list(tremor_f) # turn it back to list then add to dictionary
        new_file = file.split(sep='.')[0] + '_butter.xlsx' # rename file
        butter_df = pd.DataFrame.from_dict(butter_dic).reset_index()
        butter_df.to_excel(new_file)
        print("||", i, '/', shape, " FINISHED! || ", new_file.split(sep='\\')[2])
    
    print("Finished! All butter saved to", path)

butter_filter(all_xlsx)
## 3a. Calculate Sample Entropy

def calc_vector(row):
    '''
    Calculate the acceleration vector from x,y,z coordinates. Using total acceleration equation.
    '''
    vector = np.sqrt(row['AccelX']**2 + row['AccelY']**2 + row['AccelZ']**2)
    return vector

def sampen_vec_calc(all_butter):
    ''' Calculates the sample entropy for acceleration vectors only. No zscore.
    
    Function to calculate entropy for all files in a list, 
    save it as a dictionary, convert to a dataframe, and format it for easy reading.
    Designed for KinesiaONE tremor raw data
    
    sampen_calc(file_list)
    '''
    i = 0
    output = "samen_tremor_" + prepost + ".xlsx"
    for file in all_butter:
        i = i + 1
        df = pd.read_excel(file)
        file = file.split(sep='\\')[2].split(sep=".")[0] # get the filename
        cols = df.columns
        df['vector'] = df.apply(calc_vector,axis=1) # calculate the acceleration magnitude
        samen = sampen.sampen2(df['vector']) # calculates sample entropy
        entropies[file] = [samen[2][1]]
        print("||", i, '/', shape, " FINISHED! || ", file)
    df_samen = pd.DataFrame.from_dict(entropies) # convert dictionary to dataframe
    df_samen = df_samen.reset_index() # reset index to be normal
    samen = df_samen.pivot_table(columns="index").loc[:,:'RotateZ'] # remove entropy for time, pivot table
    samen.to_excel(output) # save to excel
    print("All entropies saved to ", output)
    return samen

## 3b. Calculate Approximate Entropy using EntroPy
    '''
    * perm_entropy(x, order=3, normalize=True)                 # Permutation entropy
    * spectral_entropy(x, 100, method='welch', normalize=True) # Spectral entropy
    * svd_entropy(x, order=3, delay=1, normalize=True)         # Singular value decomposition entropy
    * app_entropy(x, order=2, metric='chebyshev')              # Approximate entropy
    * sample_entropy(x, order=2, metric='chebyshev')           # Sample entropy
    * lziv_complexity('01111000011001', normalize=True)        # Lempel-Ziv complexity
    '''

def appen_vec_calc(all_butter):
    ''' Calculates the approximate entropy for acceleration vectors only. No zscore.
    
    Function to calculate entropy for all files in a list, 
    save it as a dictionary, convert to a dataframe, and format it for easy reading.
    Designed for KinesiaONE tremor raw data
    
    appen_calc(file_list)
    '''
    i = 0
    output = "appen_tremor_" + prepost + ".xlsx"
    for file in all_butter:
        i = i + 1
        df = pd.read_excel(file)
        file = file.split(sep='\\')[2].split(sep=".")[0] # get the filename
        cols = df.columns
        df['vector'] = df.apply(calc_vector,axis=1) # calculate the acceleration magnitude
        appen = app_entropy(np.array(df['vector']), order=2, metric='chebyshev') # calculates sample entropy
        entropies[file] = [appen]
        print("||", i, '/', shape, " FINISHED! || ", file)
    df_appen = pd.DataFrame.from_dict(entropies) # convert dictionary to dataframe
    df_appen = df_appen.reset_index() # reset index to be normal
    appen = df_appen.pivot_table(columns="index").loc[:,:'RotateZ'] # remove entropy for time, pivot table
    appen.to_excel(output) # save to excel
    print("All entropies saved to ", output)
    return appen

if entropy == "appen":
    if prepost == "post":
        print("Analyzing post data")
        post_ap = appen_vec_calc(all_butter)
    elif prepost =="pre":
        print("Analyzing pre data")
        pre_ap = appen_vec_calc(all_butter)
    else:
        print("Error. Check prepost assignment")
elif entropy == "samen":
    if prepost == "post":
        print("Analyzing post data")
        post_sam = sampen_vec_calc(all_butter)
    elif prepost =="pre":
        print("Analyzing pre data")
        pre_sam = sampen_vec_calc(all_butter)
    else:
        print("Error. Check prepost assignment")

# Approximate Entropy Export
df_pre = pre_ap.copy()
df_pre = df_pre.reset_index()
df_pre.columns = ['participant','appen_pre']

df_post = post_ap.copy()
df_post = df_post.reset_index()
df_post.columns = ['participant','appen_post']

df_both = pd.merge(df_pre, df_post, on="participant")
df_both['appen_diff'] = df_both['appen_post']-df_both['appen_pre']

df_kin = pd.read_csv('kinesia_scores.csv')

appen_score = pd.merge(df_both, df_kin, left_on="participant", right_on="BDNF")
appen_score = appen_score.drop(["BDNF","PreFreq","PostFreq"], axis=1)
appen_score["score_diff"] = appen_score['Postscore']-appen_score['Prescore']
appen_score = appen_score.sort_values(by="score_diff",ascending=True)
appen_score.to_excel("tremor_appen.xlsx")

# Sample Entropy Export
df_pre = pre_sam.copy()
df_pre = df_pre.reset_index()
df_pre.columns = ['participant','samen_pre']

df_post = post_sam.copy()
df_post = df_post.reset_index()
df_post.columns = ['participant','samen_post']

df_both = pd.merge(df_pre, df_post, on="participant")
df_both['samen_diff'] = df_both['samen_post']-df_both['samen_pre']

df_kin = pd.read_csv('kinesia_scores.csv')

samen_score = pd.merge(df_both, df_kin, left_on="participant", right_on="BDNF")
samen_score = samen_score.drop(["BDNF","PreFreq","PostFreq"], axis=1)
samen_score["score_diff"] = samen_score['Postscore']-samen_score['Prescore']
samen_score = samen_score.sort_values(by="score_diff",ascending=True)
samen_score.to_excel("tremor_samen.xlsx")
