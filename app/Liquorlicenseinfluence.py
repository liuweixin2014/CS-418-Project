#Import required libraries
import sys
import csv
import requests
import json
import re

class TaskNine:

    def __init__(self, variable):
        
        #Commented out the sleep command
        def getCensusBlock9(address):
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
                #sleep.sleep(3)
                censusBlockDict = getCensusBlock9(address)
            else:
                #if everything is perfect then continue
                censusBlockDict = json.loads(response.text)

            return censusBlockDict



        def getCrimeHistory9(lat, long):
            print('getting crime history')

            # need to get lattitude and longitude from other database
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


            crimeDict = json.loads(response.text)
            return crimeDict


        #Commented out address modification steps
        def getBusinessLicenseHistory9(name, address):
            print('getting business license history')
            #oldAddress = address
            #address,state = address.split(',')
            #address = getTrimmedAddress(address)
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


            #turn data to dict representation
            licenseDict = json.loads(response.text)

            return licenseDict



        #Read the required CSV files
        with open(variable,'r') as restaurant:
            reader = csv.reader(restaurant)
            restaurant_list = list(reader)

        #Initialise an output list and an output dictionary
        output_list = []
        dict = {}

        #For each restaurant in the list, get the restaurant name and the address
        for each_restaurant in restaurant_list[1:]:
            restaurant_name = each_restaurant[1].lower()
            restaurant_address = each_restaurant[6].lower()
            name_first = restaurant_address.split(',')[0]
            result = re.match(r'^[\d]+$', name_first[0])
            #Steps to retrieve required restaurant address
            if (len(name_first.split(' ')) > 2 and result):

                if (len(name_first.split(' ')) == 3):
                    required_restaurant_address = name_first.split(' ')[0] + ' ' + name_first.split(' ')[1] + ' ' + name_first.split(' ')[2]
                elif (name_first.split(' ')[3][0] != '(' or not name_first.split(' ')[3]):
                    required_restaurant_address = name_first.split(' ')[0] + ' ' + name_first.split(' ')[1] + ' ' + name_first.split(' ')[2] + ' ' + name_first.split(' ')[3]
                else:
                    required_restaurant_address = name_first.split(' ')[0] + ' ' + name_first.split(' ')[1] + ' ' + name_first.split(' ')[2]

                required_restaurant_address = required_restaurant_address.replace('.','')

            else:
                for i,each in enumerate(name_first.split(' ')):

                    if (re.match(r'^[\d]+$', each) and len(name_first.split(' ')) > 2):

                        if (len(name_first.split(' ')) - i > 3):
                            required_restaurant_address = each + ' '+ name_first.split(' ')[i+1] + ' '+ name_first.split(' ')[i+2] + ' '+ name_first.split(' ')[i+3]
                            break
                        else:
                            required_restaurant_address = each + ' '+ name_first.split(' ')[i + 1] + ' '+ name_first.split(' ')[i + 1]
                            break

                    required_restaurant_address = ''

            #Retrieve the business License History
            businessLicenseHistory = getBusinessLicenseHistory9(restaurant_name,required_restaurant_address)

            if (businessLicenseHistory):
                for each in businessLicenseHistory:
                    flag = 0
                    for key in each:
                        #Check if business has liquor license
                        if(key == 'business_activity'):

                            if ('LIQUOR' in each['business_activity'].upper()):
                                output_list.append([restaurant_name,required_restaurant_address,each['business_activity']])
                                blockDetails = getCensusBlock9(required_restaurant_address+' chicago IL')
                                if (blockDetails['result']['addressMatches']):
                                    blockNumber = blockDetails['result']['addressMatches'][0]['geographies']['Census Blocks'][0]['BLOCK']
                                    latitude = blockDetails['result']['addressMatches'][0]['geographies']['Census Blocks'][0]['CENTLAT']
                                    longitude = blockDetails['result']['addressMatches'][0]['geographies']['Census Blocks'][0]['CENTLON']

                                    #Store the block number and its latitute and longitude details in a dictionary
                                    key = blockNumber
                                    if key not in dict:
                                        dict[key] = []
                                    dict[key].append((latitude,longitude))
                                flag = 1
                                break
                    if (flag ==1):
                        break

        #To retrieve the crime data using lat and long and keep trying till it returns crime data for the block
        def getCoordinates(value,numberOfBusiness):
            for i in range(0,numberOfBusiness):
                lat,lon = value[i]
                crimeHistory = getCrimeHistory9(lat, lon)
                if (crimeHistory):
                    return crimeHistory

            return ''

        #For each census block in dictionary retrieve the crime data for that block
        #Since crime data covers 1.5 city block radius, consider only 1 lat and long value for a census block to avoid overlap
        # crime data has upper limit of 1000
        for key in dict:
            value = dict[key]
            numberOfBusiness = len(dict[key])
            crimeHistory = getCoordinates(value,numberOfBusiness)
            crime_count = 0
            arrest_count = 0
            if (crimeHistory):

                for crime in crimeHistory:
                    crime_count += 1
                    if (crime['arrest'] == True):
                        arrest_count += 1
                output_list.append([key,numberOfBusiness,crime_count,arrest_count])


        # Open csv file to write
        OutputFile = open('LiquorLicense.csv', 'w')
        with OutputFile:
            writer = csv.writer(OutputFile)
            writer.writerows([['Census Block', '#Businesses with liquor licenses', '#Crimes', '#Arrests']])
            writer.writerows(output_list)

