import sys
import csv
import requests
import json
import re
import time as sleep
from TaskOneTwoAndTen import TaskOne
from TaskOneTwoAndTen import TaskTwo
from TaskOneTwoAndTen import TaskTen

#websites
#
#https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.pdf
#https://www.census.gov/data/developers/data-sets.html
#
#https://dev.socrata.com/docs/endpoints.html
#https://data.cityofchicago.org/Public-Safety/Crimes-2001-to-present/ijzp-q8t2
#https://data.cityofchicago.org/Health-Human-Services/Food-Inspections/4ijn-s7e5
#https://data.cityofchicago.org/Community-Economic-Development/Business-Licenses/r5kz-chrr
#
#https://www.ncdc.noaa.gov/cdo-web/webservices/v2
#token is needed for weather calls


#get all crime data within 1.5 block radius and from 2014 to present
def getCrimeHistory(lat, long):
    print('getting crime history')

    #need to get lattitude and longitude from other database
    lattitude = lat
    longitude = long
    # 1.5 city block radius in meters is 301 rounded up where 1 block is 1/8 a mile
    radiusInMeters = '301'
    baseUrl = 'https://data.cityofchicago.org/resource/6zsd-86xi.json'
    select = '$select=primary_type,description,location_description,arrest,year'
    where = '$where=within_circle(location, ' + lattitude + ', ' + longitude + ', ' + radiusInMeters + ') AND year>2013'
    orderby = '$order=year DESC,primary_type ASC'
    url = baseUrl + '?' + select + '&' + where + '&' + orderby

    response = requests.get(url)

    if response.status_code != 200:
        print(url, '\nthis url encountered url encoding problem')
    '''elif 'need to figure out what to put here to trigger this' in response.text:
        #if 200 status but content is corrupt or incomplete repeat
        sleep.sleep(3)
        crimeDict = getCrimeHistory(lat,long)
    else:
        #if everything is perfect then continue
        crimeDict = json.loads(response.text)'''

    crimeDict = json.loads(response.text)
    return crimeDict


#trim address by removing extra stuff
def getModifiedAddress(address):
    address = address.split(' ')

    count = 0
    
    number = ''
    orientation = ''
    name = ''
    city = ''
    state = ''
    
    for x in address:
        x = x.replace('.', '')
        if count == 0:
            result = re.match(r'^[\d]+$', x)
            if result is None:
                result = ''
            else:
                result = result.string
            if x in result:
                number = x
                count += 1
        elif count == 1:
            if x.lower() == 'n' or x.lower() == 's' or x.lower() == 'e' or x.lower() == 'w':
                orientation = x
                count += 1
        elif count == 2:
            name = x
            count += 1
        elif 'lake' == name.lower() and 'shore' in x.lower() and count == 3:
            name = name + ' ' + x
        elif 'la' == name.lower() and 'salle' in x.lower() and count == 3:
            name = name + ' ' + x
        elif 'wacker' == name.lower() and 'dr' in x.lower() and count == 3:
            name = name + ' ' + x
        elif 'chicago,' in x.lower():
            city = x
            count += 1
        elif count == 4:
            state = x
            count += 1
        elif count == 5:
            zip_code = x
            count += 1
    trimAddress = number + ' ' + orientation + ' ' + name + ' ' + city + ' ' + state
    return trimAddress


#trim address by removing extra stuff
def getTrimmedAddress(address):
    address = address.split(' ')


    count = 0
    for x in address:
        if count == 0:
            number = x
            count += 1
        elif count == 1:
            orientation = x
            count += 1
        elif count == 2:
            name = x
            count += 1

    trimedAddress = number + ' ' + orientation + ' ' + name
    return trimedAddress


def getBusinessLicenseHistory(name, address):
    print('getting business license history')
    oldAddress = address
    address,city,state,zipcode = address.split(',')
    address = getTrimmedAddress(address)
    address = address.upper()
    #remove characters that will encounter problems in the requests parser and replace with wildcard character
    name = name.upper().replace('\'', '_').replace('&', '_')

    baseUrl = 'https://data.cityofchicago.org/resource/xqx5-8hwx.json'
    select = '$select=legal_name,doing_business_as_name,license_code,license_description,business_activity_id,business_activity'
    where = '$where=address like ' + "'%25" + address + "%25'" + ' AND (legal_name like ' + "'%25" + name + "%25' " +'OR doing_business_as_name like ' + "'%25" + name + "%25'" + ')'
    orderby = '$order=license_start_date DESC'
    url = baseUrl + '?' + select + '&' + where + '&' + orderby

    myurl = url.encode('utf-8')
    response = requests.get(myurl)

    if response.status_code != 200:
        print(url, '\nthis url encountered url encoding problem')
    '''elif 'need to figure out what to put here to trigger this' in response.text:
        #if 200 status but content is corrupt or incomplete repeat
        sleep.sleep(3)
        licenseDict = getBusinessLicenseHistory(name, oldAddress)
    else:
        #if everything is perfect then continue
        licenseDict = json.loads(response.text)'''

    #turn data to dict representation
    licenseDict = json.loads(response.text)

    return licenseDict


def getFoodInspectionHistory(name, address):
    print('getting food inspection history')
    oldAddress = address
    address,city,state,zipcode = address.split(',')
    address = getTrimmedAddress(address)
    address = address.upper()
    #remove characters that will encounter problems in the requests parser and replace with wildcard character
    name = name.upper().replace('\'', '_').replace('&', '_')

    baseUrl = 'https://data.cityofchicago.org/resource/cwig-ma7x.json'
    select = '$select=aka_name,dba_name,facility_type,risk,inspection_date,inspection_type,results,violations'
    where = '$where=address like ' + "'%25" + address + "%25'" + ' AND (aka_name like ' + "'%25" + name + "%25' " +'OR dba_name like ' + "'%25" + name + "%25'" + ')'
    orderby = '$order=inspection_date DESC'
    url = baseUrl + '?' + select + '&' + where + '&' + orderby

    myurl = url.encode('utf-8')
    response = requests.get(myurl)

    if response.status_code != 200:
        print(url, '\nthis url encountered url encoding problem')
    '''elif 'need to figure out what to put here to trigger this' in response.text:
        #if 200 status but content is corrupt or incomplete repeat
        sleep.sleep(3)
        foodInspectionDict = getFoodInspectionHistory(name, oldAddress)
    else:
        #if everything is perfect then continue
        foodInspectionDict = json.loads(response.text)'''

    #turn data to dict representation
    foodInspectionDict = json.loads(response.text)
    return foodInspectionDict


def getWeatherHistory():
    print('getting weather history')

    header = {'token': 'dYucmeoWuLMPXUulkTyIvsHqqUvfrLTf'}

    #https://www.ncdc.noaa.gov/cdo-web/api/v2/data?datasetid=GHCND&datatypeid=TAVG&TMAX&TMIN&PRCP&SNOW&SNWD&AWND&stationid=GHCND:USW00094846&startdate=2014-01-01&enddate=2018-04-07&limit=1000&offset=0
    baseurl = 'https://www.ncdc.noaa.gov/cdo-web/api/v2/'
    endpoint = 'data?'
    datasetID = 'datasetid=GHCND'
    datatypeid = 'datatypeid=TAVG'     #&datatypeid=TMAX&datatypeid=TMIN&datatypeid=PRCP&datatypeid=SNOW&datatypeid=SNWD&datatypeid=AWND'
    stationid = 'stationid=GHCND:USW00094846'
    startDate = 'startdate=2017-04-10'
    endDate = 'enddate=2018-04-07'
    limit= 'limit=1000'
    offset = 'offset=0'
    attributes = 'includemetadata=false'

    #url = baseurl + endpoint + datasetID + '&' + datatypeid + '&' + stationid + '&' + startDate + '&' + endDate + '&' + limit + '&' + offset
    url = baseurl + endpoint + datasetID + '&' + datatypeid + '&' + stationid + '&' + startDate + '&' + endDate + '&' + attributes + '&'+ limit
    response = requests.get(url, headers=header)

    if response.status_code != 200:
        print(url, '\nthis url encountered url encoding problem')
    '''elif 'need to figure out what to put here to trigger this' in response.text:
        #if 200 status but content is corrupt or incomplete repeat
        sleep.sleep(3)
        weatherHistoryDict = getWeatherHistory()
    else:
        #if everything is perfect then continue
        weatherHistoryDict = json.loads(response.text)'''

    weatherHistoryDict = json.loads(response.text)

    return weatherHistoryDict


def getCensusBlock(address):
    print('getting census block')

    #https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress?address=1505+S+Michigan+Chicago%2C+IL+60605&benchmark=Public_AR_Census2010&vintage=Census2010_Census2010
    baseURL = 'https://geocoding.geo.census.gov/geocoder/'
    returnType = 'geographies/'
    searchType = 'onelineaddress?'
    benchmark = 'benchmark=Public_AR_Census2010'
    vintage = 'vintage=Census2010_Census2010'
    addressSearch = 'address=' + address.replace(' ', '+')
    formatType = 'format=json'

    url = baseURL + returnType + searchType + addressSearch + '&' + benchmark + '&' + vintage + '&' + formatType
    response = requests.get(url)
    if response.status_code != 200:
        print('encountered an input error')
    elif 'org.springframework.dao.DataRetrievalFailureException' in response.text:
        #if 200 status but content is corrupt or incomplete repeat
        sleep.sleep(3)
        censusBlockDict = getCensusBlock(address)
    else:
        #if everything is perfect then continue
        censusBlockDict = json.loads(response.text)
    
    #using 2010 database but switch to current one to get coordinates and other info since old data doesnt have this address
    if len(censusBlockDict['result']['addressMatches']) == 0:
        censusBlockDict = helperToGetCensusBlock(address)
        
    return censusBlockDict


def helperToGetCensusBlock(address):
    print('census block call with different database')

    baseURL = 'https://geocoding.geo.census.gov/geocoder/'
    returnType = 'geographies/'
    searchType = 'onelineaddress?'
    benchmark = 'benchmark=Public_AR_Current'
    vintage = 'vintage=Current_Current'
    addressSearch = 'address=' + address.replace(' ', '+')
    formatType = 'format=json'

    url = baseURL + returnType + searchType + addressSearch + '&' + benchmark + '&' + vintage + '&' + formatType
    response = requests.get(url)
    if response.status_code != 200:
        print('encountered an input error')
        if response.status_code == 500:
            censusBlockHelperDict = helperToGetCensusBlock(address)
    elif 'org.springframework.dao.DataRetrievalFailureException' in response.text:
        #if 200 status but content is corrupt or incomplete repeat
        sleep.sleep(3)
        censusBlockHelperDict = helperToGetCensusBlock(address)
    else:
        #if everything is perfect then continue
        censusBlockHelperDict = json.loads(response.text)

    return censusBlockHelperDict


def getCensusDataByBlock():
    print('getting census data by block')
    return []


def getBlockIndex(list):

    theRealKey = ''
    for key in list:
        if '2010 Census Blocks' == key:
            theRealKey = key
        elif 'Census Blocks' == key:
            theRealKey = key
    return theRealKey


def templateFunction():
    #file to retrieve restaurant data from yelp csv file
    restaurantYelp = csv.reader(open('restaurants_60601-60606.csv', 'r'))


    #get weather data
    #TODO
    #weatherHistory = getWeatherHistory()

    yelpRestaurantDictionary = {}
    header = {}
    index = 0
    businessCount = 1

    #this loop turns csv data to a dictionary
    for line in restaurantYelp:
        if header == {}:
            header = line
        else:
            yelpRestaurantDictionary[index] = dict(zip(header, line))
            index += 1

    refinedData = []

    #following loop gets any data needed for each restaurant
    for restaurantInfo in yelpRestaurantDictionary.values():

        #get data from databases we might need
        if 'education' in restaurantInfo['categories'].lower() or 'restaurant' in restaurantInfo['categories'].lower() or 'grocery' in restaurantInfo['categories'].lower() or '':
            
            print('Count:', businessCount, ' id:', restaurantInfo['restaurantID'])
            #pull addrerss from yelp info
            address = restaurantInfo['address']

            #get census block info
            censusBlock = getCensusBlock(getModifiedAddress(address))

            #check if data is retrieved
            if len(censusBlock['result']['addressMatches']) > 0:
                #this will be needed for food inspections and business license
                address = censusBlock['result']['addressMatches'][0]['matchedAddress']

                #this is needed for crime
                lat = str(censusBlock['result']['addressMatches'][0]['coordinates']['y'])
                long = str(censusBlock['result']['addressMatches'][0]['coordinates']['x'])

                #this will be needed for census data
                #censusStateNo = censusBlock['result']['addressMatches'][0]['geographies'][][][]
                censusTractNo = censusBlock['result']['addressMatches'][0]['geographies']['Census Tracts'][0]['BASENAME']
                #determie what data we are using and use proper key for census block
                blockIndex = getBlockIndex(censusBlock['result']['addressMatches'][0]['geographies'].keys())
                censusBlockNo = censusBlock['result']['addressMatches'][0]['geographies'][blockIndex][0]['BASENAME']

                #this will be needed for food inspections and business license
                name = restaurantInfo['name']

                #get crime history from 1.5 mile radius and after 2014
                crimeHistory = getCrimeHistory(lat, long)

                #get all business licences related to the address and name
                businessLicenseHistory = getBusinessLicenseHistory(name, address)

                #geet all food inspections related to the address and name
                foodInspectionHistory = getFoodInspectionHistory(name, address)

                #get census block data
                #censusDataByBlock = getCensusDataByBlock(censusTractNo, censusBlockNo)

                #merge data here for your purpose

                #add to other list if you need for observation for prediction
                #refinedData.add(your variable for refined data)
                #sleep.sleep(5)
                businessCount += 1
            else:
                #should not reach here but if you do handle variables in above 'if' portion
                address = address.upper()
                print('need to see census response')

    print('done')


if __name__ == '__main__':

    crimeReport = 'crime_report'
    predictCrimeProbability = 'predict_crime_probability'
    graphCrimeAgeBlock = 'graph_crime_age_block'
    reviewInspection = 'review_inspection'
    sentimentReviewAnalysis = 'sentiment_review_analysis'
    restaurantSentimentAndReview = 'restaurant_sentiment_and_review'
    predictReview = 'predict_review'
    businessViability = 'business_viability'
    liquorAndCrime = 'liquor_and_crime'
    weatherAndCrime = 'weather_and_crime'

    #runtime arguments
    args = sys.argv

    #holds list of arguments
    commands = []

    #holds an argument with variables
    subCommand = []

    #get length of total arguments and variables
    argsLength = len(sys.argv)
    count = 0

    #seperate arguments
    for x in args:
        if '-' in x and subCommand == []:
            subCommand.append(x)
        elif '-' in x and subCommand != []:
            commands.append(subCommand)
            subCommand = []
            subCommand.append(x)
        else:
            subCommand.append(x)

        count += 1
        if count == argsLength:
            commands.append(subCommand)

    #call proper functions based of argument and variables
    for x in commands:
        argument = x.pop(0)
        variables = x
        if crimeReport in argument:
            print('task 1')
            taskOne = TaskOne('restaurants_60601-60606.csv')
            taskOne.buildTable()
            print('done')
        elif predictCrimeProbability in argument:
            print('task 2')
            taskTwo = TaskTwo(variables)
            taskTwo.buildCrimeTable()
            taskTwo.fitAndPredict()
            print('done')
        elif graphCrimeAgeBlock in argument:
            print('task 3')
        elif reviewInspection in argument:
            print('task 4')
        elif sentimentReviewAnalysis in argument:
            print('task 5')
            import pandas as pd 
            import numpy as np
            import matplotlib.pyplot as plt
            from sklearn.feature_extraction.text import TfidfVectorizer 
            from sklearn.feature_extraction.text import CountVectorizer
            from sklearn.model_selection import train_test_split
            from sklearn.utils.random import sample_without_replacement
            from sklearn.utils import resample
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.metrics import f1_score
            from sklearn.metrics import precision_score
            from sklearn.metrics import recall_score
            restaurant=pd.read_csv('restaurants_60601-60606.csv')
            reviews=pd.read_csv("reviews_60601-60606.csv",error_bad_lines=False)
            data0=reviews[['reviewContent','rating']]
            data0['rating'].value_counts()
            data1=resample(data0[data0['rating']==1], n_samples=1550, random_state=0)
            data2=resample(data0[data0['rating']==2], n_samples=1550, random_state=0)
            data3=resample(data0[data0['rating']==3], n_samples=1550, random_state=0)
            data4=resample(data0[data0['rating']==4], n_samples=1550, random_state=0)
            data5=resample(data0[data0['rating']==5], n_samples=1550, random_state=0)
            frames = [data1,data2,data3,data4,data5]
            data0=pd.concat(frames)
            X_train, X_test, y_train, y_test = train_test_split(data0['reviewContent'],data0['rating'], test_size=0.33, random_state=42)
            vectorizer = TfidfVectorizer(stop_words='english')
            vectorizer.fit(X_train)
            vectorizer.vocabulary_
            x= vectorizer.transform(X_train)
            clf = RandomForestClassifier(n_estimators=101)
            clf.fit(x,y_train)
            x_test=vectorizer.transform(X_test)
            print("the predict result is")
            y_predict=clf.predict(x_test)
            print(y_predict)
            print("the f1_socre is ")
            f1_score=f1_score(y_test,y_predict,average='weighted')
            print(f1_score)
            print("the precision is")
            precision_score=precision_score(y_test, y_predict, average='weighted')
            print(precision_score)
            print("the recall is")
            recall_score=recall_score(y_test, y_predict, average='weighted')
            print(recall_score)
        elif restaurantSentimentAndReview in argument:
            print('task 6')
            import pandas as pd 
            import numpy as np
            import matplotlib.pyplot as plt
            from sklearn.feature_extraction.text import TfidfVectorizer 
            from sklearn.feature_extraction.text import CountVectorizer
            from sklearn.model_selection import train_test_split
            from sklearn.utils.random import sample_without_replacement
            from sklearn.utils import resample
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.metrics import f1_score
            from sklearn.metrics import precision_score
            from sklearn.metrics import recall_score
            restaurant=pd.read_csv('restaurants_60601-60606.csv')
            reviews=pd.read_csv("reviews_60601-60606.csv",error_bad_lines=False)
            data0=reviews[['reviewContent','rating']]
            data0['rating'].value_counts()
            data1=resample(data0[data0['rating']==1], n_samples=1550, random_state=0)
            data2=resample(data0[data0['rating']==2], n_samples=1550, random_state=0)
            data3=resample(data0[data0['rating']==3], n_samples=1550, random_state=0)
            data4=resample(data0[data0['rating']==4], n_samples=1550, random_state=0)
            data5=resample(data0[data0['rating']==5], n_samples=1550, random_state=0)
            frames = [data1,data2,data3,data4,data5]
            data0=pd.concat(frames)
            X_train, X_test, y_train, y_test = train_test_split(data0['reviewContent'],data0['rating'], test_size=0.33, random_state=42)
            vectorizer = TfidfVectorizer(stop_words='english')
            vectorizer.fit(X_train)
            vectorizer.vocabulary_
            x= vectorizer.transform(X_train)
            clf = RandomForestClassifier(n_estimators=101)
            clf.fit(x,y_train)
            x_test=vectorizer.transform(X_test)
            print("the predict result is")
            y_predict=clf.predict(x_test)
            print(y_predict)
            print("the f1_socre is ")
            f1_score=f1_score(y_test,y_predict,average='weighted')
            print(f1_score)
            print("the precision is")
            precision_score=precision_score(y_test, y_predict, average='weighted')
            print(precision_score)
            print("the recall is")
            recall_score=recall_score(y_test, y_predict, average='weighted')
            print(recall_score)
        elif predictReview in argument:
            print('task 7')
            import pandas as pd 
            import numpy as np
            import matplotlib.pyplot as plt
            from sklearn.feature_extraction.text import TfidfVectorizer 
            from sklearn.feature_extraction.text import CountVectorizer
            from sklearn.model_selection import train_test_split
            from sklearn.utils.random import sample_without_replacement
            from sklearn.utils import resample
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.metrics import f1_score
            from sklearn.metrics import precision_score
            from sklearn.metrics import recall_score
            restaurant=pd.read_csv('restaurants_60601-60606.csv')
            reviews=pd.read_csv("reviews_60601-60606.csv",error_bad_lines=False)
            restaurant['label'] = np.where(restaurant['rating']>=4,1,0)
            restaurant['label'].value_counts()
            positive=restaurant[restaurant['label']==1]
            positive['rating'].value_counts().plot(kind="bar")
            plt.xlabel("rating")
            plt.ylabel('number of restaurants')
            plt.show()
            reviews['label']=np.where(reviews['rating']>=4,1,0)
            data0=reviews[['reviewContent','label']]
            data0
            p,n=data0['label'].value_counts()
            p_reduce=resample(data0[data0['label']==1], n_samples=n, random_state=0)
            p_reduce
            frames = [p_reduce,data0[data0['label']==0]]
            data1=pd.concat(frames)
            data1
            X_train, X_test, y_train, y_test = train_test_split(data1['reviewContent'],data1['label'], test_size=0.33, random_state=42)
            vectorizer = TfidfVectorizer(min_df=0.05,stop_words='english')
            X_train
            vectorizer.fit(X_train)
            vectorizer.vocabulary_
            x= vectorizer.transform(X_train)
            clf = RandomForestClassifier( n_estimators=100,random_state=0)
            clf.fit(x,y_train)
            x_test=vectorizer.transform(X_test)
            print('the prediction is ')
            y_predict=clf.predict(x_test)
            print(y_predict)
            f1_score=f1_score(y_test,y_predict)
            print("the f1_score is ")
            print(f1_score)
            precision=precision_score(y_test,y_predict)
            print("the precision is")
            print(precision)
            recall_score=recall_score(y_test, y_predict)
            print("the recall is ")
            print(recall_score)
        elif businessViability in argument:
            print('task 8')
        elif liquorAndCrime in argument:
            print('task 9')
        elif weatherAndCrime in argument:
            print('task 10')
            taskTen = TaskTen(variables)
            taskTen.buildCrimeAndWeatherTable()
            taskTen.fitAndPredict()

    print(commands)
