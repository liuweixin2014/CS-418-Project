import csv
import requests
import json
import re
import time as sleep

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
        # 1.5 city block radius in meters is 301 rounded up where 1 block is 1/8 a mile
        radiusInMeters = '301'
        #getting json format
        baseUrl = 'https://data.cityofchicago.org/resource/6zsd-86xi.json'
        select = '$select=primary_type,location_description,arrest,year'
        where = '$where=within_circle(location, ' + lattitude + ', ' + longitude + ', ' + radiusInMeters + ') AND year>2013'
        orderby = '$order=year DESC,primary_type ASC'
        url = baseUrl + '?' + select + '&' + where + '&' + orderby

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
