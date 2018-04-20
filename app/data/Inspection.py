#Import required libraries
import sys
import csv
import requests
import json
import re

class TaskFour:

    def __init__(self, variable):

        #Commented out the sleep command



        #Commented out address modification steps
        def getBusinessInspectionHistory9(name, address):
            address = address.upper()
            name = name.upper().replace('\'', '_').replace('&', '_')

            baseUrl = 'https://data.cityofchicago.org/resource/xqx5-8hwx.json'
            select = '$select=legal_name,doing_business_as_name,Inspection'
            where = '$where=address like ' + "'%25" + address + "%25'" + ' AND (legal_name like ' + "'%25" + name + "%25' " +'OR doing_business_as_name like ' + "'%25" + name + "%25'" + ')'
            orderby = '$order=inpection DESC'
            url = baseUrl + '?' + select + '&' + where + '&' + orderby

            myurl = url.encode('utf-8')
            response = requests.get(myurl)

            if response.status_code != 200:
                print(url, '\nthis url encountered url encoding problem')



            InspectDict = json.loads(response.text)
            return InspectDict



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
            InspectionHistory = getInspectionHistory(restaurant_name,required_restaurant_address)


                        break




        for key in dict:
            value = dict[key]
            numberOfBusiness = len(dict[key])

            failed_count = 0
            pass_count = 0
            conditional_count = 0
            if (crimeHistory):

                for crime in crimeHistory:
                    crime_count += 1
                    if (crime['arrest'] == True):
                        arrest_count += 1
                output_list.append([name,address,review_average,pass_count,conditional_count,failed_count])


        # Open csv file to write
        OutputFile = open('../results/FoodInspection.csv', 'w')
        with OutputFile:
            writer = csv.writer(OutputFile)
            writer.writerows([['Restaurant Name', 'Address', 'Average Yelp Review', '#Pass', '#Conditional', '#Failed Inspection']])
            writer.writerows(output_list)
