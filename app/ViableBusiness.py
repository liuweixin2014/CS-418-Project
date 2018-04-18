#Import required libraries
import csv
from datetime import date
import re
import json
import requests

class TaskEight:

    def __init__(self, variable):
        
        #Read the required CSV files
        with open(variable,'r') as restaurant:
            reader = csv.reader(restaurant)
            restaurant_list = list(reader)

        output_list = []

        def getFoodInspectionHistory8(name, address):
            print('getting food inspection history')
            # oldAddress = address
            # address, city, state, zipcode = address.split(',')
            # address = getTrimmedAddress(address)
            address = address.upper()
            # remove characters that will encounter problems in the requests parser and replace with wildcard character
            name = name.upper().replace('\'', '_').replace('&', '_')

            baseUrl = 'https://data.cityofchicago.org/resource/cwig-ma7x.json'
            select = '$select=aka_name,dba_name,facility_type,risk,inspection_date,inspection_type,results,violations'
            where = '$where=address like ' + "'%25" + address + "%25'" + ' AND (aka_name like ' + "'%25" + name + "%25' " + 'OR dba_name like ' + "'%25" + name + "%25'" + ')'
            orderby = '$order=inspection_date DESC'
            url = baseUrl + '?' + select + '&' + where + '&' + orderby

            myurl = url.encode('utf-8')
            response = requests.get(myurl)

            if response.status_code != 200:
                print(url, '\nthis url encountered url encoding problem')
                foodInspectionDict = []
                return foodInspectionDict


            # turn data to dict representation
            foodInspectionDict = json.loads(response.text)
            return foodInspectionDict

        #For each restaurant name in list check with food inspection
        for each_restaurant in restaurant_list[1:]:
            restaurant_name = each_restaurant[1].strip().lower()
            restaurant_address = each_restaurant[6].strip().lower()
            name_first = restaurant_address.split(',')[0]
            result = re.match(r'^[\d]+$', name_first[0])

            # Steps to retrieve required restaurant address
            if (len(name_first.split(' ')) > 2 and result):

                if (len(name_first.split(' ')) == 3):
                    required_restaurant_address = name_first.split(' ')[0] + ' ' + name_first.split(' ')[1] + ' ' + \
                                                  name_first.split(' ')[2]
                elif (name_first.split(' ')[3][0] != '(' or not name_first.split(' ')[3]):
                    required_restaurant_address = name_first.split(' ')[0] + ' ' + name_first.split(' ')[1] + ' ' + \
                                                  name_first.split(' ')[2] + ' ' + name_first.split(' ')[3]
                else:
                    required_restaurant_address = name_first.split(' ')[0] + ' ' + name_first.split(' ')[1] + ' ' + \
                                                  name_first.split(' ')[2]

                required_restaurant_address = required_restaurant_address.replace('.', '')

            else:
                for i, each in enumerate(name_first.split(' ')):

                    if (re.match(r'^[\d]+$', each) and len(name_first.split(' ')) > 2):

                        if (len(name_first.split(' ')) - i > 3):
                            required_restaurant_address = each + ' ' + name_first.split(' ')[i + 1] + ' ' + \
                                                          name_first.split(' ')[i + 2] + ' ' + name_first.split(' ')[i + 3]
                            break
                        else:
                            required_restaurant_address = each + ' ' + name_first.split(' ')[i + 1] + ' ' + \
                                                          name_first.split(' ')[i + 1]
                            break

                    required_restaurant_address = ''

            foodInspectionHistory = getFoodInspectionHistory8(restaurant_name,required_restaurant_address)
            for inspection in foodInspectionHistory:

                if (inspection['results'].upper() == 'OUT OF BUSINESS'):
                    out_Date = inspection['inspection_date'][0:10]
                    out_Year = int(out_Date[0:4])
                    out_Month = int(out_Date[5:7])
                    out_Day = int(out_Date[8:10])
                    out_of_business_date = date(out_Year, out_Month, out_Day)

                    for each in foodInspectionHistory:
                        if (each['results'].upper() == 'FAIL'):
                            fail_Date = each['inspection_date'][0:10]
                            fail_Year = int(fail_Date[0:4])
                            fail_Month = int(fail_Date[5:7])
                            fail_Day = int(fail_Date[8:10])
                            fail_date = date(int(fail_Year), int(fail_Month), int(fail_Day))

                            if (out_of_business_date > fail_date):
                                delta = out_of_business_date - fail_date
                                delta = str(delta).split(' ')
                                NoOfYearsActive = round((float(delta[0])/364),2)
                                output_list.append([restaurant_name,restaurant_address,fail_date,NoOfYearsActive])
                                break
                    break


        #Open csv file to write
        OutputFile = open('ViableBusiness.csv', 'w')
        with OutputFile:
            writer = csv.writer(OutputFile)
            writer.writerows([['Restaurant Name','Address','Failed Inspection on','Alive for x years']])
            writer.writerows(output_list)
