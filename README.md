# Case Study - Marketplace Target Enrollment 

## The Goal: Identify Facilities that the Markeplace Team can prioritize enrollment



### Tools Used:
-Jupyter Notebooks

-Spyder

-CARTO

### DataSets
1.) Facility Locations

2.) US Counties

3.)Crop Production : USDA NASS 2020 Yield (bu/acre) for Corn and Soybeans

### Data Cleaning
- Missing Values in County ANSI Code
      Column County ANSI from the Crops database has missing values and its identify aas 'OTHER COUNTIES' in the county column and the total value if 6289 bu/acre

     Total dataset values :342,242 bu/acre for all categories (not filtered by corn or soybeans) ~ 1.8% of the total

     --> therefore for this analysis the null were dropped from the data ser ( alternative method could include evenly sprinkling these values across states)
      
- Joining Key Development:
       Crops Prodcutions dataset had FIPS ids for state and county that needed to be formatted and joined to create a new column 'GEOID' to match the counties dataset
       Purpose: Assign each county its designated yield statistic from the crop dataset
 - Column drops and Renaming:
       This was for general cleaning and readability purposes 
  
  
  ### Analysis
  
  - Ranking System Development:
               Quantile ranking system was developed to determine priority. This method 
               
               
  ### Recommendations
  
  
  
  
  ### Next Steps
                  
