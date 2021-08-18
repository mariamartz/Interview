# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import geopandas as gpd
import json 
from functools import reduce
from shapely.geometry import box
from shapely.geometry import Point, LineString, Polygon
import os

from cartoframes.viz import *
from cartoframes.auth import Credentials
from cartoframes.auth import set_default_credentials
from cartoframes import to_carto
#Carto credentials for map viz
credentials={
    'username':'mariana11martz11',
    'api_key':'9177a76bf3f8cb4f8a4aa76785b40665eed8f1fd'}

with open("Data/creds.json", "w") as outfile:
    json.dump(credentials, outfile)
set_default_credentials('Data/creds.json')
#Set the file path of the folder - this way it multiple files are in here , easy iteration
rootFolder = os.path.dirname(__file__)

#File imports
fp = rootFolder + '/Data/tl_2020_us_county.shp'
counties= gpd.read_file(fp)           #Import the shp file - all counties in the US
crops= pd.read_csv(rootFolder +'/Data/25C7E4A4-7C7C-393E-B094-CDFBEAD3AB83.csv')  # import file from USDA with corn and soybean yield data
facilities = pd.read_csv(rootFolder +'/Data/indigo_case_study_500_random_buyers.csv')
#Data cleaning 


def clean_shape(df):
    """
    

    Parameters
    ----------
    df : dataframe
        raw crops data from USDA NASS.

    Returns
    -------
    df : dataframe
        cleaned crops data for analysis.

    """
    
    
    df = df.copy()
    
    # Crops File 
    # Column County ANSI had "OTHER COUNTIES" with NA values- these were dopped for the purpose of this studyokay 
    df = .dropna(subset=['County ANSI'])

    #create GEOID in Crop File in the matching format as the counties file 
    df['County ANSI'] = df['County ANSI'].astype(int)
    df['County ANSI'] = np.where(df['County ANSI']<10,
                                    '00' + df['County ANSI'].astype(str),
                                    np.where(df['County ANSI']<100,
                                             '0' + df['County ANSI'].astype(str),
                                             df['County ANSI'].astype(str)))

    df['State ANSI'] = df['State ANSI'].astype(int)
    df['State ANSI']=np.where(df['State ANSI']<10,
                                    '0' + df['State ANSI'].astype(str),
                                                df['State ANSI'].astype(str))
    # create new GEOID column to the df dataframe
    df['GEOID']=df['State ANSI'].astype(str)+ df['County ANSI'].astype(str)

    #Transform the df dataframe to show the values needed as each column
    df = pd.pivot_table(df, values='Value', index=['GEOID','County','State'], columns=['Data Item'])
    df = df.drop(columns=['CORN, GRAIN, IRRIGATED - YIELD, MEASURED IN BU / ACRE',
                              'CORN, GRAIN, NON-IRRIGATED - YIELD, MEASURED IN BU / ACRE',
                             'CORN, SILAGE - YIELD, MEASURED IN TONS / ACRE','SOYBEANS, IRRIGATED - YIELD, MEASURED IN BU / ACRE',
                              'SOYBEANS, NON-IRRIGATED - YIELD, MEASURED IN BU / ACRE'])
    Name_replace={'CORN, GRAIN - YIELD, MEASURED IN BU / ACRE':'Corn_Yield_Bu_Acre',
                 'SOYBEANS - YIELD, MEASURED IN BU / ACRE':'Soybeans_Yield_Bu_Acre'}
    df = df.rename(columns=Name_replace)

    #create a total grain Bu_Acre column (soybeans+corn)
    df['total_Bu_Acre']=df['Corn_Yield_Bu_Acre']+ df['Soybeans_Yield_Bu_Acre']
    
    
    
    
    
    return df


crops = clean_shape(crops)






#Geocode facilities --> make points
facilities_shp= gpd.GeoDataFrame(facilities, geometry=gpd.points_from_xy(facilities.longitude, facilities.latitude),crs='EPSG:4269')
#Export to shp file for spatial Join
facilities_shp.to_file('data/facilities.shp')







# Analysis 

#Create a ranking system for Corn, Soybeans and Total columns


#90th perntile - high priority

#50th percentile - medium priority

#25th percentile- low priority
crops['QRanking_Corn'] = np.where(crops['Corn_Yield_Bu_Acre'] >= crops['Corn_Yield_Bu_Acre'].quantile(0.9), 
                           'High Priority',
                          np.where(crops['Corn_Yield_Bu_Acre'] >= crops['Corn_Yield_Bu_Acre'].quantile(0.5), 
                           'Medium Priority',
                                   'Low Priority'))

crops['QRanking_Soy'] = np.where(crops['Soybeans_Yield_Bu_Acre'] >= crops['Soybeans_Yield_Bu_Acre'].quantile(0.9), 
                           'High Priority',
                          np.where(crops['Soybeans_Yield_Bu_Acre'] >= crops['Soybeans_Yield_Bu_Acre'].quantile(0.5), 
                           'Medium Priority',
                                   'Low Priority'))

crops['QRanking_Total'] = np.where(crops['total_Bu_Acre'] >= crops['total_Bu_Acre'].quantile(0.9), 
                           'High Priority',
                          np.where(crops['total_Bu_Acre'] >= crops['total_Bu_Acre'].quantile(0.5), 
                           'Medium Priority',
                                   'Low Priority'))

#JOINS - Attribute Joins
#counties shp file to crops dataframe 
CropsValue = counties.merge(crops, on='GEOID', how='right')
CropsValue.to_file('data/CropsValue.shp') # made to shp file for mapping viz

#JOINS - Spatil Joins
facilities_shp = gpd.read_file('data/facilities.shp')
FacilitiesCounties=gpd.sjoin(facilities_shp, CropsValue, how='left', op='within')

#Spatial Analysis pt1
p = FacilitiesCounties.groupby(['QRanking_Total','GEOID'])['id'].count().reset_index()
HP_Total = p[p['QRanking_Total']=='High Priority'].sort_values(by=['id'], ascending=False)
HP_Total = HP_Total.rename(columns={"id":"Count_of_high_Priority_QRT"})

MP_Total = p[p['QRanking_Total']=='Medium Priority'].sort_values(by=['id'], ascending=False)
MP_Total = MP_Total.rename(columns={"id":"Count_of_Medium_Priority_QRT"})

lP_Total = p[p['QRanking_Total']=='Low Priority'].sort_values(by=['id'], ascending=False)
lP_Total = lP_Total.rename(columns={"id":"Count_of_Low_Priority_QRT"})

All =[MP_Total, lP_Total, HP_Total]
joined = reduce(lambda left, right: pd.merge(left,right, on='GEOID', how='outer'),All)
joined= joined.drop(columns=['QRanking_Total_y','QRanking_Total'])
Count_Faci_Prio=counties.merge(joined, on='GEOID', how='right')

Phase1 = ['17143','17179','17125','17107','17147','17019','17137','17113','17021']
Phase1_counties = counties[counties['GEOID'].isin(Phase1)]
phase1 = gpd.overlay(Phase1_counties,Phase1_counties, how='union')

#Mapping - this onyl needs to be ran once 
#Send datasets to CARTO 
#to_carto(FacilitiesCounties, 'facilitiescounties', if_exists='replace')
#to_carto(Count_Faci_Prio, 'Count_Faci_Prio', if_exists='replace')
#to_carto(CropsValue, 'crops_value', if_exists='replace')
#to_carto(phase1,'phase1',if_exists='replace')

#createmap
Enrollment_Priority_Map = Map([
          Layer('phase1', title='Phase 1 Area'),
          Layer('count_faci_prio',
                 style=color_bins_style('count_of_high_priority_qrt',
                                         bins=4,
                                         breaks=[0,2,3,4],
                                         palette='cb_blues'),
                 title='Total High Priority Facilities per County'),
          Layer('crops_value',
                 style=color_bins_style('total_bu_acre',
                                        breaks=[200,249.86],
                                        palette='mint'),
                 legends=color_bins_legend(title='Total Yield Bu/Acre*',
                                           description= '*includes soybeans and corn',
                                           footer='Data: USDA NASS 2020')),
           Layer('facilitiescounties', 
                 size_category_style('qranking_total',
                                     cat=['High Priority', 'Medium Priority', 'Low Priority'],
                                     size_range=[25,15,3],
                                     color=('#43f4b6')),
                 legends=size_category_legend(title='Priority Category'),
                 popup_hover=[popup_element('id','Facility ID'),
                              popup_element('namelsad','County Name'),
                              popup_element('qranking_total','Priority Ranking'),
                              popup_element('geoid','GEOID')],
                 widgets=[basic_widget(title='Priority Enrollment Locations',
                                       description='Faicilites Are prioritize based on yield production totals of corn and soybens',
                                       footer='Indigo Case Study'),
                          category_widget('qranking_total',
                                          title='Priority Category',
                                          description='Select to Filter the priority category'),
                          basic_widget(title= 'Phase 1 Area Enrollment',
                                       description= 'Click to turn off layers and see Phase 1 Area and designated facilities',
                                       footer= 'The recommended high priority cluster location that the marketplace team should focus on'),
                          basic_widget(footer = 'To Explore how priority categories and Phase 1 Are are defined: <a href="https://github.com/mariamartz/Interview">Github</a>')],
                 title = 'Total Grain Yield Facility Priority')], 
    layer_selector = True)


Enrollment_Priority_Map.publish('Enrollment_Priority_Map', password=None, if_exists='replace')

