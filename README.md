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
  
  
  ### Data Analysis
  
  - Ranking System Development:
      Quantile ranking system was developed to determine priority. 
               
       This method is based on a normal distribution. first step constited of checking for the distribution of the total ( corn +soybeans) yield Bu/acre. As seen in the graph below the distribution is little bit skewed.However, the dataset is large enough to assume normal distribution for the purposes of this study (~1800 data points)
            ![image](https://user-images.githubusercontent.com/74034683/129844154-e272c82c-2ab4-4121-ad8a-ebf9007bac25.png)
            
   Next, the percetile threshold were chosen to provide a clear distinction between each group based on the number of standard deviations away from the mean
   ![image](https://user-images.githubusercontent.com/74034683/129844622-61deb81f-293e-4894-8b35-16cd5aa744fe.png)
   
   The ranking was chosen as follows:
   
   90th perntile - high priority ~+1 Standard Deviation

   50th percentile - medium priority - median

   25th percentile- low priority - less than 1 standard diviation
   
   ### Spatial Analysis
   - Facilities in high yield counties development:
           Spatial join was used to determine which facilities were located in which county. The rank of the county was then used to determine the rank of the facility
           for example: if a facility was in a high priority county the facility was then designated as high priority
   
        
               
  ### Recommendations
  
  
  
  
  ### Next Steps
                  
