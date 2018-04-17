Before running the application make sure you have the following

  python 3.6.x

  librarires/modules needed:
    sys, csv, requests, json, re, time, sklearn, pandas, numpy, matplotlib
      *** Sometimes you might need to reinstall some libraries if you get 'comb' import typeerror ***
 
 
For the task 5 to task 7, the sentiment analysis part , need to prepare the original data set. restaurants_60601-60606.csv and reviews_60601-60606.csv
 
The file tf-idf and predict sentiment label and predict review rating files need to be run in ipython notebook 
the result will be the F-score and precison and some figiures 
 
 
 

Running the application

download/clone from github
  https://github.com/farhan13/CS-418-Project.git

Navigate to following folder/directory on terminal
  ~<path you placed downloaded folder at>/CS-418-Project/app/
  
on terminal run following command and check Commands and Mandatory Optios for further details
  python3 aceApp.py <command>



Commands: 
  -crime_report
    This command requires restaurants_60601-60606.csv file
    This will take 30 minutes to 2 hours depending on geocoding.geo.census.gov
    This command will print out a table to a file named CrimeBusinessYelpData.csv
    This command is Task One
    
  -predict_crime_probability <AddressString> ... <DataPointValue> 
    This command will print out a table to a file named PredictionResults.csv
    This command is Task Two
  
  -graph_crime_age_block
  
  -review_inspection
  
  -sentiment_review_analysis
  
  -restaurant_sentiment_and_review
  
  -predict_review
  
  -business_viability
    
  -liquor_and_crime
     
  -weather_and_crime <AddressString> ... <DataPointValue>
    You will need to request a key from https://www.ncdc.noaa.gov/cdo-web/webservices/v2 and place it line 203 within the getWeatherHistory() in file TaskOneTwoAndTen.py
    This command will print out a table to a file named weatherPredictionResults.csv
    This command is Task Ten



Symbols:
  ... = Previous option can be repeated multiple times
  <>  = Placeholder for options or values



Mandatory Optios: All options are seperated by a space
  AddressString: 
    number:<number value>
    orientation:<E,W,S,N>
    street:<actual street name>
    streetType:<type of street ie ST, Ave, Ct, etc>
    city:<city name>
    state:<state abbreviation>
    zip_code:<5 digit zip code>
    
    Example:
      "number:6001 orientation:S street:Karlov streetType:Ave city:Chicago state:il zip_code:60629" 
  
  DataPointValue:
    datapoints:<positive integer value of max datapoints desired to use from crime data portal>
    
    Example:
      "datapoints:600000"



Optional Options:
