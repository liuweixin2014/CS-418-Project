import csv
import requests
import json
import re
import time as sleep
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier


class TaskTen:

    crimeData = None
    crimeClassifier = None
    addressToPredict = None
    addressCoordinates = None
    monthlyAvg = None

    #cunstructor
    def __init__(self,variables):
        addressArray, dataPoints = self.splitAddressArrayFromDataPoints(variables)
        self.addressToPredict = self.createAddressOneLine(addressArray)
        self.crimeData = self.getCrimeHistory(dataPoints)

    def getCoordinateList(self):

        coordinatesArray = []

        for address in self.addressToPredict:
            tempDict = self.getCensusBlock(address)

            if len(tempDict['result']['addressMatches']) > 0:
                latitude = tempDict['result']['addressMatches'][0]['coordinates']['y']
                longitude = tempDict['result']['addressMatches'][0]['coordinates']['x']
                blockIndex = self.getBlockIndex(tempDict['result']['addressMatches'][0]['geographies'].keys())
                block = tempDict['result']['addressMatches'][0]['geographies'][blockIndex][0]['BASENAME']

                tempArrayMay = [float(longitude), float(latitude), 5, address, block]
                tempArrayJune = [float(longitude), float(latitude), 6, address, block]
                tempArrayJuly = [float(longitude), float(latitude), 7, address, block]
                tempArrayAugust = [float(longitude), float(latitude), 8, address, block]

                coordinatesArray.append(tempArrayMay)
                coordinatesArray.append(tempArrayJune)
                coordinatesArray.append(tempArrayJuly)
                coordinatesArray.append(tempArrayAugust)
        return coordinatesArray

    def splitAddressArrayFromDataPoints(self, variables):
        addressUnparsed = None
        datapointUnparsed = None
        count = 0
        index = 0
        for var in variables:
            if 'datapoints:' in var:
                index = count
            count += 1
        datapoint = self.getValofData(variables.pop(index))
        addressUnparsed = variables
        return addressUnparsed, datapoint

    def getValofData(self, datapointUnparsed):
        name, value = datapointUnparsed.split(':')

        return value

    def createAddressOneLine(self, addressArray):
        addresses = []
        for address in addressArray:
            number, orientation, street, streetType, city, state, zip_code = address.split(' ')
            #check its only a number
            number = number.split(':')[1]

            #remove . or turn to abbreviation only
            orientation = orientation.split(':')[1]
            orientation = orientation.replace('.', '')
            orientation = self.abbreviatedOrientation(orientation)

            street = street.split(':')[1]

            #remove any .
            streetType = streetType.split(':')[1]
            streetType = streetType.replace('.', '')

            city = city.split(':')[1]

            #remove any periods
            state = state.split(':')[1]
            state = state.replace('.', '')

            zip_code = zip_code.split(':')[1]
            newAddress = number + ' ' + orientation + ' ' + street + ' ' + streetType + ', ' + city + ', ' + state + ', ' + zip_code
            addresses.append(newAddress)

        return addresses

    def abbreviatedOrientation(self, orientation):

        if 'east' == orientation.lower():
            return 'e'
        elif 'west' == orientation.lower():
            return 'w'
        elif 'north' == orientation.lower():
            return 'n'
        elif 'south' == orientation.lower():
            return 's'
        return orientation

    def getBlockIndex(self, list):

        theRealKey = ''
        for key in list:
            if '2010 Census Blocks' == key:
                theRealKey = key
            elif 'Census Blocks' == key:
                theRealKey = key
        return theRealKey

    def getCensusBlock(self, address):
        print('getting census block')

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
            censusBlockDict = self.getCensusBlock(address)
        elif 'org.springframework.dao.DataRetrievalFailureException' in response.text:
            #if 200 status but content is corrupt or incomplete repeat
            sleep.sleep(6)
            censusBlockDict = self.getCensusBlock(address)
        else:
            #if everything is perfect then continue
            censusBlockDict = json.loads(response.text)

        #using 2010 database but switch to current one to get coordinates and other info since old data doesnt have this address
        if len(censusBlockDict['result']['addressMatches']) == 0:
            censusBlockDict = self.helperToGetCensusBlock(address)


        return censusBlockDict

    def helperToGetCensusBlock(self, address):
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
                censusBlockHelperDict = self.helperToGetCensusBlock(address)
        elif 'org.springframework.dao.DataRetrievalFailureException' in response.text:
            #if 200 status but content is corrupt or incomplete repeat
            sleep.sleep(7)
            censusBlockHelperDict = self.helperToGetCensusBlock(address)
        else:
            #if everything is perfect then continue
            censusBlockHelperDict = json.loads(response.text)

        return censusBlockHelperDict

    def getCrimeHistory(self, datapoints):
        print('getting crime history')

        #getting json format
        baseUrl = 'https://data.cityofchicago.org/resource/6zsd-86xi.json'
        #primary type is the classifier
        #this is not used arrest,beat,district,
        select = '$select=description,date,latitude,longitude'
        #date between \'\' and \'\' AND
        where = '$where=date IS NOT NULL AND latitude IS NOT NULL AND longitude IS NOT NULL AND district IS NOT NULL AND primary_type like \'%25ROBBERY%25\' AND year>2015'
        orderby = '$order=year DESC,id DESC,description ASC'
        limit = '$limit=' + datapoints
        offset = '$offset=0'
        url = baseUrl + '?' + select + '&' + where + '&' + orderby + '&' + limit + '&' + offset

        response = requests.get(url)

        if response.status_code != 200:
            print(url, '\nthis url encountered url encoding problem')

        crimeDict = json.loads(response.text)
        return crimeDict

    def getWeatherHistory(self):
        print('getting weather history')

        header = {'token': 'dYucmeoWuLMPXUulkTyIvsHqqUvfrLTf'}

        baseurl = 'https://www.ncdc.noaa.gov/cdo-web/api/v2/'
        endpoint = 'data?'
        datasetID = 'datasetid=GHCND'
        datatypeid = 'datatypeid=TAVG'
        stationid = 'stationid=GHCND:USW00094846'
        startDate = 'startdate=2017-04-08'
        endDate = 'enddate=2018-04-07'
        units = 'units=standard'
        limit= 'limit=1000'
        offset = 'offset=0'
        attributes = 'includemetadata=false'

        url = baseurl + endpoint + datasetID + '&' + datatypeid + '&' + stationid + '&' + startDate + '&' + endDate + '&' + units + '&' + attributes + '&'+ limit
        response = requests.get(url, headers=header)

        if response.status_code != 200:
            print(url, '\nthis url encountered url encoding problem')

        weatherHistoryDict = json.loads(response.text)

        weatherHistoryDict = weatherHistoryDict['results']
        #value = temperature
        #date = date split at t for date[0]
        # split - for month [1]

        monthlyAverage = {}

        for x in range(12):
            valuesOfMonth = {}
            valuesOfMonth['count'] = 0
            valuesOfMonth['avg'] = 0
            valuesOfMonth['temp sum'] = 0
            monthlyAverage[x+1] = valuesOfMonth

        for day in weatherHistoryDict:

            dateVal,timeVal = day['date'].split('T')
            yearVal,monthVal,dayVal = dateVal.split('-')
            tempValue = day['value']

            monthVal = int(monthVal)
            month = monthlyAverage[monthVal]

            month['count'] = month['count'] + 1
            month['temp sum'] = month['temp sum'] + tempValue
            month['avg'] = int(month['temp sum']/month['count'])

        self.monthlyAvg = monthlyAverage
        return weatherHistoryDict

    def buildCrimeAndWeatherTable(self):
        newCrimeTableAttributes = []
        newCrimeTableClassifier = []

        weatherData = self.getWeatherHistory()

        for crime in self.crimeData:
            longitude = crime['longitude']
            latitude = crime['latitude']

            date,time = crime['date'].split('T')
            yyyy,mm,dd = date.split('-')
            classifier = crime['description'] + 'monthAvg:' + str(self.monthlyAvg[int(mm)]['avg'])

            data = [float(longitude), float(latitude), float(mm)]

            newCrimeTableAttributes.append(data)
            newCrimeTableClassifier.append(classifier)

        self.addressCoordinates = self.getCoordinateList()
        self.crimeData = newCrimeTableAttributes
        self.crimeClassifier = newCrimeTableClassifier

    def fitAndPredict(self):

        header = ['Census Block', 'Month', 'TAVG', 'Type Of Robbery', 'Probability']

        predictionDict = {}
        dictCount = 0

        predictThis = [sublist[:3] for sublist in self.addressCoordinates]

        print('Beginning LR prediction')
        logReg = LogisticRegression()
        logReg.fit(self.crimeData, self.crimeClassifier)

        y_predict = logReg.predict(predictThis)
        y_predictProb = logReg.predict_proba(predictThis)

        for x in range(len(self.addressCoordinates)):

            block = self.addressCoordinates[x][4]
            month = self.addressCoordinates[x][2]
            description,avgTemp = y_predict[x].split('monthAvg:')
            probabilityValue = y_predictProb[x].max()

            valueList = [block, month, avgTemp, description, probabilityValue]

            predictionDict[dictCount] = dict(zip(header, valueList))
            dictCount += 1
        print('Finished LR Prediction')

        print('Writing data to file predictionResults.csv')
        newCSV = open('weatherPredictionResults.csv', 'w')
        csvWriter = csv.DictWriter(newCSV, header)
        csvWriter.writeheader()
        csvWriter.writerows(predictionDict.values())
        newCSV.close()


class TaskTwo:

    crimeData = None
    crimeClassifier = None
    addressToPredict = None
    addressCoordinates = None

    #cunstructor
    def __init__(self,variables):
        addressArray, dataPoints = self.splitAddressArrayFromDataPoints(variables)
        self.addressToPredict = self.createAddressOneLine(addressArray)
        self.crimeData = self.getCrimeHistory(dataPoints)

    def getCoordinateList(self):

        coordinatesArray = []

        for address in self.addressToPredict:
            tempDict = self.getCensusBlock(address)

            if len(tempDict['result']['addressMatches']) > 0:
                latitude = tempDict['result']['addressMatches'][0]['coordinates']['y']
                longitude = tempDict['result']['addressMatches'][0]['coordinates']['x']
                tempArray = [float(longitude), float(latitude), address]
                coordinatesArray.append(tempArray)
        return coordinatesArray

    def splitAddressArrayFromDataPoints(self, variables):
        addressUnparsed = None
        datapointUnparsed = None
        count = 0
        index = 0
        for var in variables:
            if 'datapoints:' in var:
                index = count
            count += 1
        datapoint = self.getValofData(variables.pop(index))
        addressUnparsed = variables
        return addressUnparsed, datapoint

    def getValofData(self, datapointUnparsed):
        name, value = datapointUnparsed.split(':')

        return value

    def createAddressOneLine(self, addressArray):
        addresses = []
        for address in addressArray:
            number, orientation, street, streetType, city, state, zip_code = address.split(' ')
            #check its only a number
            number = number.split(':')[1]

            #remove . or turn to abbreviation only
            orientation = orientation.split(':')[1]
            orientation = orientation.replace('.', '')
            orientation = self.abbreviatedOrientation(orientation)

            street = street.split(':')[1]

            #remove any .
            streetType = streetType.split(':')[1]
            streetType = streetType.replace('.', '')

            city = city.split(':')[1]

            #remove any periods
            state = state.split(':')[1]
            state = state.replace('.', '')

            zip_code = zip_code.split(':')[1]
            newAddress = number + ' ' + orientation + ' ' + street + ' ' + streetType + ', ' + city + ', ' + state + ', ' + zip_code
            addresses.append(newAddress)

        return addresses

    def abbreviatedOrientation(self, orientation):

        if 'east' == orientation.lower():
            return 'e'
        elif 'west' == orientation.lower():
            return 'w'
        elif 'north' == orientation.lower():
            return 'n'
        elif 'south' == orientation.lower():
            return 's'
        return orientation

    def getBlockIndex(self, list):

        theRealKey = ''
        for key in list:
            if '2010 Census Blocks' == key:
                theRealKey = key
            elif 'Census Blocks' == key:
                theRealKey = key
        return theRealKey

    def turnBooleanToBinary(self, boolValue):
        if boolValue:
            return 1.0
        return 0.0

    def getCensusBlock(self, address):
        print('getting census block')

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
            censusBlockDict = self.getCensusBlock(address)
        elif 'org.springframework.dao.DataRetrievalFailureException' in response.text:
            #if 200 status but content is corrupt or incomplete repeat
            sleep.sleep(6)
            censusBlockDict = self.getCensusBlock(address)
        else:
            #if everything is perfect then continue
            censusBlockDict = json.loads(response.text)

        #using 2010 database but switch to current one to get coordinates and other info since old data doesnt have this address
        if len(censusBlockDict['result']['addressMatches']) == 0:
            censusBlockDict = self.helperToGetCensusBlock(address)


        return censusBlockDict

    def helperToGetCensusBlock(self, address):
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
                censusBlockHelperDict = self.helperToGetCensusBlock(address)
        elif 'org.springframework.dao.DataRetrievalFailureException' in response.text:
            #if 200 status but content is corrupt or incomplete repeat
            sleep.sleep(7)
            censusBlockHelperDict = self.helperToGetCensusBlock(address)
        else:
            #if everything is perfect then continue
            censusBlockHelperDict = json.loads(response.text)

        return censusBlockHelperDict

    def getCrimeHistory(self, datapoints):
        print('getting crime history')

        #getting json format
        baseUrl = 'https://data.cityofchicago.org/resource/6zsd-86xi.json'
        #primary type is the classifier
        #this is not used arrest,beat,district,
        select = '$select=primary_type,latitude,longitude'
        where = '$where=latitude IS NOT NULL AND longitude IS NOT NULL AND district IS NOT NULL AND year>2015'
        orderby = '$order=year DESC,id DESC,primary_type ASC'
        limit = '$limit=' + datapoints
        offset = '$offset=0'
        url = baseUrl + '?' + select + '&' + where + '&' + orderby + '&' + limit + '&' + offset

        response = requests.get(url)

        if response.status_code != 200:
            print(url, '\nthis url encountered url encoding problem')

        crimeDict = json.loads(response.text)
        return crimeDict

    def buildCrimeTable(self):
        newCrimeTableAttributes = []
        newCrimeTableClassifier = []

        for crime in self.crimeData:
            longitude = crime['longitude']
            latitude = crime['latitude']
            classifier = crime['primary_type']

            data = [float(longitude), float(latitude)]

            newCrimeTableAttributes.append(data)
            newCrimeTableClassifier.append(classifier)

        self.addressCoordinates = self.getCoordinateList()
        self.crimeData = newCrimeTableAttributes
        self.crimeClassifier = newCrimeTableClassifier

    def fitAndPredict(self):

        header = ['Address', 'CrimeType', 'Technique', 'Probability']

        predictionDict = {}
        dictCount = 0


        predictThis = [sublist[:2] for sublist in self.addressCoordinates]

        print('Beginning DT prediction')
        decisionTree = DecisionTreeClassifier(max_depth=8)
        decisionTree.fit(self.crimeData, self.crimeClassifier)

        y_predict = decisionTree.predict(predictThis)
        y_predictProb = decisionTree.predict_proba(predictThis)

        for x in range(len(self.addressCoordinates)):
            addressValue = self.addressCoordinates[x][2]
            crimeTypeValue = y_predict[x]
            techniqueValue = 'Decision Tree'
            probabilityValue = y_predictProb[x].max()

            valueList = [addressValue, crimeTypeValue, techniqueValue,probabilityValue]

            predictionDict[dictCount] = dict(zip(header, valueList))
            dictCount += 1
        print('Finished DT Prediction')

        print('Beginning RF prediction')
        randomForest = RandomForestClassifier(max_depth=7)
        randomForest.fit(self.crimeData, self.crimeClassifier)

        y_predict = randomForest.predict(predictThis)
        y_predictProb = randomForest.predict_proba(predictThis)

        for x in range(len(self.addressCoordinates)):

            addressValue = self.addressCoordinates[x][2]
            crimeTypeValue = y_predict[x]
            techniqueValue = 'Random Forest'
            probabilityValue = y_predictProb[x].max()

            valueList = [addressValue, crimeTypeValue, techniqueValue,probabilityValue]

            predictionDict[dictCount] = dict(zip(header, valueList))
            dictCount += 1
        print('Finished RF Prediction')

        print('Beginning LR prediction')
        logReg = LogisticRegression()
        logReg.fit(self.crimeData, self.crimeClassifier)

        y_predict = logReg.predict(predictThis)
        y_predictProb = logReg.predict_proba(predictThis)

        for x in range(len(self.addressCoordinates)):

            addressValue = self.addressCoordinates[x][2]
            crimeTypeValue = y_predict[x]
            techniqueValue = 'Logistic Regression'
            probabilityValue = y_predictProb[x].max()

            valueList = [addressValue, crimeTypeValue, techniqueValue,probabilityValue]

            predictionDict[dictCount] = dict(zip(header, valueList))
            dictCount += 1
        print('Finished LR Prediction')

        print('Writing data to file predictionResults.csv')
        newCSV = open('predictionResults.csv', 'w')
        csvWriter = csv.DictWriter(newCSV, header)
        csvWriter.writeheader()
        csvWriter.writerows(predictionDict.values())
        newCSV.close()


class TaskOne:
    #dict that hold valid yelp data
    yelpData = None
    #file name
    OutPutData = None


    #constructor
    def __init__(self, yelpDataFile):
        self.yelpData = self.trimYelpData(yelpDataFile)

    #get yelp data for grocery,school, and restaurants
    #incoming value is a string value that has the document name in csv format
    def trimYelpData(self, yelpDataFile):
        #file to retrieve restaurant data from yelp csv file
        yelpCSVFile = open(yelpDataFile, 'r')
        restaurantYelp = csv.reader(yelpCSVFile)

        yelpRestaurantDictionary = {}
        header = {}
        index = 0
        businessCount = 1

        #this loop turns csv data to a dictionary
        for line in restaurantYelp:
            if header == {}:
                header = line
            else:
                #get data from databases we might need
                restaurantInfo = dict(zip(header, line))
                if 'education' in restaurantInfo['categories'].lower() or 'restaurant' in restaurantInfo['categories'].lower() or 'grocery' in restaurantInfo['categories'].lower():
                    yelpRestaurantDictionary[index] = restaurantInfo
                    index += 1
        yelpCSVFile.close()
        return yelpRestaurantDictionary

    #trim address by removing extra stuff
    def getModifiedAddress(self, address):
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
                modifiedX = x.replace('', '')
                result = re.match(r'^[\d]+$', modifiedX)
                if result is None:
                    result = ''
                else:
                    result = result.string
                if x in result:
                    number = x
                    count += 1
            elif count == 1:
                if x.lower() == 'n' or x.lower() == 's' or x.lower() == 'e' or x.lower() == 'w' or x.lower() == 'north' or x.lower() == 'south' or x.lower() == 'east' or x.lower() == 'west':
                    orientation = x
                    count += 1
            elif count == 2:
                name = x
                count += 1
            elif 'lake' == name.lower() and 'shore' in x.lower() and count == 3:
                name = name + ' ' + x
            elif 'la' == name.lower() and 'salle' in x.lower() and count == 3:
                name = name + ' ' + x
            elif 'wacker' == name.lower() and 'dr' == x.lower() and count == 3:
                name = name + ' ' + x
            elif 'van' == name.lower() and 'buren' == x.lower() and count == 3:
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

    def getSearchStringForCrimeDescription(self, string):

        if 'grocery' in string.lower():
            return 'grocery'
        elif 'restaurant' in string.lower():
            return 'restaurant'
        elif 'education' in string.lower():
            return 'school'
        return ''

    #trim address by removing extra stuff
    def getTrimmedAddress(self, address):
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

    def getCensusBlock(self, address):
        print('getting census block')

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
            censusBlockDict = self.getCensusBlock(address)
        elif 'org.springframework.dao.DataRetrievalFailureException' in response.text:
            #if 200 status but content is corrupt or incomplete repeat
            sleep.sleep(6)
            censusBlockDict = self.getCensusBlock(address)
        else:
            #if everything is perfect then continue
            censusBlockDict = json.loads(response.text)

        #using 2010 database but switch to current one to get coordinates and other info since old data doesnt have this address
        if len(censusBlockDict['result']['addressMatches']) == 0:
            censusBlockDict = self.helperToGetCensusBlock(address)

        return censusBlockDict

    def helperToGetCensusBlock(self, address):
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
                censusBlockHelperDict = self.helperToGetCensusBlock(address)
        elif 'org.springframework.dao.DataRetrievalFailureException' in response.text:
            #if 200 status but content is corrupt or incomplete repeat
            sleep.sleep(7)
            censusBlockHelperDict = self.helperToGetCensusBlock(address)
        else:
            #if everything is perfect then continue
            censusBlockHelperDict = json.loads(response.text)

        return censusBlockHelperDict

    def getCrimeHistory(self, lat, lng):
        print('getting crime history')

        #need to get lattitude and longitude from other database
        lattitude = lat
        longitude = lng
        # 3 city block radius in meters is 602 rounded up where 1 block is 1/8 a mile
        radiusInMeters = '602'
        #getting json format
        baseUrl = 'https://data.cityofchicago.org/resource/6zsd-86xi.json'
        select = '$select=primary_type,location_description,arrest,year'
        where = '$where=location_description IS NOT NULL AND within_circle(location, ' + lattitude + ', ' + longitude + ', ' + radiusInMeters + ') AND year>2013'
        orderby = '$order=year DESC,primary_type ASC'
        limit = '$limit=50000'
        offset = '$offset=0'
        url = baseUrl + '?' + select + '&' + where + '&' + orderby + '&' + limit + '&' + offset

        response = requests.get(url)

        if response.status_code != 200:
            print(url, '\nthis url encountered url encoding problem')
        '''elif 'need to figure out what to put here to trigger this' in response.text:
            #if 200 status but content is corrupt or incomplete repeat
            sleep.sleep(3)
            crimeDict = getCrimeHistory(lat,lng)
        else:
            #if everything is perfect then continue
            crimeDict = json.loads(response.text)'''

        crimeDict = json.loads(response.text)
        return crimeDict

    def getBusinessLicenseHistory(self, name, address):
        print('getting business license history')
        oldAddress = address
        address,city,state,zipcode = address.split(',')
        address = self.getTrimmedAddress(address)
        address = address.upper()
        #remove characters that will encounter problems in the requests parser and replace with wildcard character
        name = name.upper().replace('\'', '_').replace('&', '_')

        baseUrl = 'https://data.cityofchicago.org/resource/xqx5-8hwx.json'
        select = '$select=license_start_date,expiration_date,business_activity'
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

    def splitDate(self, date):
        return date.split('/')

    def yearIsValid(self, start, end, year):

        if start == '' or end =='' or year == '':
            return False

        startMM, startDD, startYYYY = self.splitDate(start)
        endMM, endDD, endYYYY = self.splitDate(end)

        if startYYYY <= year <= endYYYY:
            return True
        return False

    def seeIfBusinessHasTobacco(self, year, businessLicenses):

        for license in businessLicenses:
            if 'business_activity' not in license:
                license['business_activity'] = ''
            if 'license_start_date' not in license:
                license['license_start_date'] = ''
            if 'expiration_date' not in license:
                license['expiration_date'] = ''

            if 'tobacco' in license['business_activity']:
                if self.yearIsValid(license['license_start_date'], license['expiration_date'], year):
                    return True
        return False

    def seeIfBusinessHasLiquor(self, year, businessLicenses):

        for license in businessLicenses:

            if 'business_activity' not in license:
                license['business_activity'] = ''
            if 'license_start_date' not in license:
                license['license_start_date'] = ''
            if 'expiration_date' not in license:
                license['expiration_date'] = ''

            if 'liquor' in license['business_activity']:
                if self.yearIsValid(license['license_start_date'], license['expiration_date'], year):
                    return True
        return False

    def alreadyExist(self, dictHolder, crime, businessType):
        for csvLine in dictHolder.values():
            if crime['year'] == csvLine['Year'] and crime['primary_type'] == csvLine['CrimeType']:
                #update crime arrest and onpremises
                csvLine['#Crime'] = csvLine['#Crime'] + 1
                if crime['arrest']:
                    csvLine['#Arrests'] = csvLine['#Arrests'] + 1
                if self.getSearchStringForCrimeDescription(businessType) in crime['location_description']:
                    csvLine['location_description'] = csvLine['location_description'] + 1
                return True

        return False

    def buildTable(self):
        self.OutPutData = 'CrimeBusinessYelpData.csv'
        headerAndDictKeys = ['Year', 'BusinessType', 'BusinessName', 'Address', 'HasTobaccoLicense', 'HasLiquorLicense', 'CrimeType', '#Crime', '#Arrests', '#OnPremises']

        #create doc to store data in
        newCSV = open(self.OutPutData, 'w')
        csvWriter = csv.DictWriter(newCSV, headerAndDictKeys)
        csvWriter.writeheader()

        if self.yelpData is None:
            return
        else:

            tempDictHolder = {}
            #counter = 0

            for restaurantInfo in self.yelpData.values():

                if tempDictHolder != {}:
                    for line in tempDictHolder.values():
                        csvWriter.writerow(line)

                tempDictHolder = {}
                counter = 0
                #get data from databases we might need
                businessType = ''
                if 'education' in restaurantInfo['categories'].lower():
                    businessType = 'education'
                elif'restaurant' in restaurantInfo['categories'].lower():
                    businessType = 'restaurant'
                elif'grocery' in restaurantInfo['categories'].lower():
                    businessType = 'grocery'

                #pull addrerss from yelp info
                address = restaurantInfo['address']

                #get census block info
                censusBlock = self.getCensusBlock(self.getModifiedAddress(address))

                #check if data is retrieved
                if len(censusBlock['result']['addressMatches']) > 0:
                    #this will be needed for food inspections and business license
                    address = censusBlock['result']['addressMatches'][0]['matchedAddress']

                    #this is needed for crime
                    lat = str(censusBlock['result']['addressMatches'][0]['coordinates']['y'])
                    lng = str(censusBlock['result']['addressMatches'][0]['coordinates']['x'])

                    #this will be needed for food inspections and business license
                    name = restaurantInfo['name']

                    #get crime history from 1.5 mile radius and after 2014
                    crimeHistory = self.getCrimeHistory(lat, lng)

                    #get all business licences related to the address and name
                    businessLicenseHistory = self.getBusinessLicenseHistory(name, address)

                    #for loop iterating through temp data checking if crime yr and crime type are alredy in if not add/create
                    for crime in crimeHistory:
                        if 'primary_type' not in crime:
                            crime['primary_type'] = ''
                        if 'location_description' not in crime:
                            crime['location_description'] = ''
                        if 'arrest' not in crime:
                            crime['arrest'] = False
                        if 'year' not in crime:
                            crime['year'] = ''

                        if tempDictHolder == {}:
                            line = [crime['year'], businessType, restaurantInfo['name'], restaurantInfo['address'], None, None, crime['primary_type'], 0, 0, 0]
                            dataHolder = dict(zip(headerAndDictKeys, line))

                            dataHolder['HasTobaccoLicense'] = self.seeIfBusinessHasTobacco(crime['year'], businessLicenseHistory)
                            dataHolder['HasLiquorLicense'] = self.seeIfBusinessHasLiquor(crime['year'], businessLicenseHistory)
                            dataHolder['#Crime'] = dataHolder['#Crime'] + 1

                            if crime['arrest']:
                                dataHolder['#Arrests'] = dataHolder['#Arrests'] + 1
                            if self.getSearchStringForCrimeDescription(businessType) in crime['location_description']:
                                dataHolder['location_description'] = dataHolder['location_description'] + 1

                            tempDictHolder[counter] = dataHolder
                            counter += 1
                        else:

                            if not self.alreadyExist(tempDictHolder, crime, businessType):
                                line = [crime['year'], businessType, restaurantInfo['name'], restaurantInfo['address'], None, None, crime['primary_type'], 0, 0, 0]
                                dataHolder = dict(zip(headerAndDictKeys, line))

                                dataHolder['HasTobaccoLicense'] = self.seeIfBusinessHasTobacco(crime['year'], businessLicenseHistory)
                                dataHolder['HasLiquorLicense'] = self.seeIfBusinessHasLiquor(crime['year'], businessLicenseHistory)
                                dataHolder['#Crime'] = dataHolder['#Crime'] + 1

                                if crime['arrest']:
                                    dataHolder['#Arrests'] = dataHolder['#Arrests'] + 1
                                if self.getSearchStringForCrimeDescription(businessType) in crime['location_description']:
                                    dataHolder['location_description'] = dataHolder['location_description'] + 1

                                tempDictHolder[counter] = dataHolder
                                counter += 1

                else:
                    print('Error need to see census response')
                    print('ID:', restaurantInfo['restaurantID'])
