#Import required libraries
import csv
from datetime import date

#Read the required CSV files
with open('restaurants_60601-60606.csv','r') as restaurant:
    reader = csv.reader(restaurant)
    restaurant_list = list(reader)

with open('Food_Inspections.csv','r') as inspection:
    reader = csv.reader(inspection)
    inspection_list = list(reader)

output_list = []

#For each restaurant name in list check with food inspection
for each_restaurant in restaurant_list:
    restaurant_name = each_restaurant[1].strip().lower()
    restaurant_address = each_restaurant[6].strip().lower()

    for each_inspection in inspection_list:
        inspection_name = each_inspection[2].strip().lower()
        inspection_address = each_inspection[6].strip().lower()
        inspection_result = each_inspection[12].strip().lower()
        inspection_date = each_inspection[10].strip()

        if ((inspection_name in restaurant_name) and (inspection_address in restaurant_address) and inspection_result=='out of business'):

            for each_inspection1 in inspection_list:
                inspection_name1 = each_inspection1[2].strip().lower()
                inspection_address1 = each_inspection1[6].strip().lower()
                inspection_result1 = each_inspection1[12].strip().lower()
                inspection_date1 = each_inspection1[10].strip()

                if ((inspection_name1 in restaurant_name) and len(inspection_name1) != 0 and (inspection_address1 in restaurant_address) and inspection_result1.lower() == 'fail'):

                    buffer_date = inspection_date.split('/')
                    closed_year = int(buffer_date[2])
                    closed_month = int(buffer_date[0])
                    closed_day = int(buffer_date[1])
                    closed_date = date(closed_year, closed_month, closed_day)

                    buffer_date1 = inspection_date1.split('/')
                    fail_year = int(buffer_date1[2])
                    fail_month = int(buffer_date1[0])
                    fail_day = int(buffer_date1[1])
                    fail_date = date(fail_year, fail_month, fail_day)

                    if (closed_date > fail_date):
                        delta = closed_date - fail_date
                        delta = str(delta).split(' ')
                        NoOfYearsActive = round((float(delta[0])/364),2)
                        output_list.append([restaurant_name,restaurant_address,inspection_date1,NoOfYearsActive])
                        break
            break

#Open csv file to write
OutputFile = open('ViableBusiness.csv', 'w')
with OutputFile:
    writer = csv.writer(OutputFile)
    writer.writerows([['Restaurant Name','Address','Failed Inspection on','Alive for x years']])
    writer.writerows(output_list)
