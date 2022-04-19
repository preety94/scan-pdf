import re
import pdfplumber
#import psycopg2
import openpyxl
#import datetime as dt
# import pandas as pd
# import os, shutil
# from base64 import b64decode
# from itertools import chain
# Developed Functions
from pdf_parser import data_extractor_numbers,data_extractor_alphanumeric,data_extractor_string
#from datetime import datetime


from aws_ocr_main import main_call
import sys



from PIL import Image
import os
# Resize Image
def resize_image(image_path):
    if os.path.getsize(image_path)>10000000:
        foo = Image.open(image_path)
        foo = foo.resize((800,800),Image.ANTIALIAS)
        foo.save(image_path,quality=95)

sys.path.append(r"C:\Users\Preety\AppData\Roaming\Python\Python310\site-packages\aws_lib_")


#Save Data in Excel
from openpyxl import load_workbook
#wb=openpyxl.Workbook()
#sh=wb.active
#li = ['Vendor_Name','Invoice_Number', 'Invoice_Date', 'Po_Number','Po_Date', 'Lohia_Pan_Number', 'Gstin_client', 'Gstin_Lohia', 'Item_code','Hsn_Sac_code', 'Quantity', 'Rate_per_unit', 'Total_value', 'Grand_Total','Vehicle_Number']
#sh.append(li)
#wb.save("Lohia_vaibhav.xlsx")

import psycopg2
conn = psycopg2.connect(database='Lohia', user='postgres',password='preety',host='localhost',port='5432')
cursor = conn.cursor()


def Trigger(input_path):
    print(input_path)
    output_path = r"C:\Users\Preety\Desktop\sequelstring\extraction\text"
    text = ''
    os.chdir(output_path)
    main_call(input_path)

    text = ''
    for file in os.listdir(output_path):
        if file.endswith('text.txt'):
            file_path = f'{output_path}\\{file}'
            with open(file_path, encoding='utf-8') as f:
                lines = f.read()
               # print(lines)
                text = text + '\n-------------------New page----------------------\n' + lines

    for file in os.listdir(r"C:\Users\Preety\Desktop\sequelstring\extraction\text"):
        os.remove(r"C:\Users\Preety\Desktop\sequelstring\extraction\text\\" + file)

    return text


def extract_all(file_name):
    txt1 = Trigger(file_name)
    text1 = ' '.join(txt1.split('\n'))
    #print(text1)
    #print('--------------')
    data_dict = {}
    l = ['(', ')', '.', '/', '-']

    # do your all fields extraction here
    data_dict['Vendor_Name'] = re.search(r'INVOICE\s+([A-Za-z\s+].*IES).*GSTIN', text1).group(1)
    print("Vendor_Name :- ", data_dict['Vendor_Name'])

    #Vendor_Name = data_extractor_alphanumeric(text1,'TAX INVOICE',1,data_dict,'email','Vendor_Name',l,'([A-Za-z\s+].*IES)',0)
    #print("========Vendor_Name===========")
    #print(Vendor_Name)


    Invoice_Number = data_extractor_alphanumeric(text1," Invoice No : ",1,data_dict,'Invoice Date : ','Invoice_Number',l,'[A-Z\-]+\d{3}',0)
    print("========Invoice_Number==============")
    print(Invoice_Number)
    Invoice_Date = data_extractor_alphanumeric(text1,'Invoice Date :',1,data_dict,'POS :' ," Invoice_Date ",l,"\d{2}\/\d{2}\/\d{4}",0)

    print("=======Invoice_Date==============")
    print(Invoice_Date)

    Po_Date = data_extractor_alphanumeric(text1,'PO No : ',1,data_dict,'Billed To : ','Po_Date',l,'\d{2}\/\d{2}\/\d{4}',0)
    if Po_Date == 0:
        data_dict['Po_Date']='N/A'
    print("=======Po_Date==============")
    print(Po_Date)
    #print('Po_DATE :-',Po_Date)
    Po_Number = data_extractor_alphanumeric(text1,'PO No :',1,data_dict,'Billed To :','Po_Number',l,'\d{10}',0)
    if Po_Number == 0:
        data_dict['Po_Number'] ='N/A'
    print("**********Po_Number************")
    print(Po_Number)
    #Vehicle_Number=re.search(r'(?si)( Despatched through Destination).*?(Terms of Delivery)',text).group()

    #Vehicle_Number = data_extractor_alphanumeric(text1,'E-Mail ',1,data_dict,'Buyer’s Order No. ','Vehicle_Number',l,'',0)

    #if Vehicle_Number == 0:
        #data_dict['Vehicle_Number']='N/A'
    #print("*********Vehicle_Number************")
    #print(Vehicle_Number)
    Lohia_Pan_Number =  data_extractor_alphanumeric(text1,'Shipped To',1,data_dict,'LOHIA CORP.LIMITED','Lohia_Pan_Number',l,'[A-Z]+\d+[0-9]+[A-Z]',0)
    print("===========Lohia_Pan_Number====================")
    print(Lohia_Pan_Number)

    Gstin_Lohia =  data_extractor_alphanumeric(text1,'Shipped To',1,data_dict,'LOHIA CORP.LIMITED','Gstin_Lohia ',l,'[A-Z0-9]{15}',0)
    #if Gstin_Lohia == 0:
       # Gstin_Lohia = '09AAACL2470J1ZG'
        #data_dict['Gstin_Lohia'] = "09AAACL2470J1ZG"
    if Gstin_Lohia==0:
         Gstin_Lohia =  data_extractor_alphanumeric(text1,'GSTIN :',1,data_dict,'LOHIA CORP.LIMITED','Gstin_Lohia ',l,'[A-Z0-9]{15}',0)

    print("===========Gstin_Lohia===================")
    print(Gstin_Lohia)
    Gstin_client = data_extractor_alphanumeric(text1,'GSTIN' ,1,data_dict,'email ','Gstin_client',l,'[A-Z0-9]{15}',0)
    #if Gstin_client == 0:
        #Gstin_client = 'O9AACFS9741G1ZW'
        #data_dict['Gstin_client'] = "O9AACFS9741G1ZW"

    print("=========Gstin_client========")
    print(Gstin_client)
    data_dict['Vehicle_Number'] = "N/A"
    data_dict['Grand_Total'] = re.search(r'Total\s+[0-9\.]+\s+[0-9\.]+\s+([0-9\.\,]+)', text1).group(1)
    print('Grand_Total :- ', data_dict['Grand_Total'])

    data = re.search(r'(?si)(Amount).*?(CGST)', text1).group()
    data = re.sub(r'\(NO OF BOX = \d+, \d+\*\d+', '', data)
    lines2 = re.findall("\d{10}", data)
    list1 = []

    #text=re.search(r'(?si)(ORIGINAL FOR RECIPIENT).*?Amount Chargeable',text1).group()
    #text_line=re.search(r'(?si)(Description).*?(Amount in words:)',text1).group()
    #print(text_line)
    #lines = re.findall(r"(?m)\d{10}\D+\s+\d{8}\s+[0-9\.]+\s+\D+\s+[0-9\,\.]+\s+[0-9\.]+\s+[0-9\.\%]+\s+[0-9\.]+|\d{10}\D+\s+\d{8}\D+[0-9\,]+\s[0-9\*]+\s+[0-9\.]+\s+\D+\s+[0-9\,\.]+\s+[0-9\.]+\s+[0-9\.\%]+\s+[0-9\.]+|\d{10}\D+\s+\d{8}\s+[0-9\.]+\D+\s+[0-9\.]+\s+[0-9\.]+\D+\d+\,\s+[0-9\*]+\s+[0-9\.\%]+\s+[0-9\.]+|\d{10}\D+\d{1}\s+\d{8}\s+[0-9\.]+\D+\s+[0-9\,\.]+\s+[0-9\.]+\s+[0-9\.\%]+\s+[0-9\.]+|\d{10}\D+\s+\d{8}\s+[0-9\.]+\s+\D+\s+[0-9\,\.]+\s+[0-9\.]+\s+[0-9\.]+\s+\%\s+[0-9\.]+|\d{8}\s+[0-9\.]+\s+\D+\s+[0-9\,\.]+\s+[0-9\.]+\s+[0-9\.\%]+\s+[0-9\.]+\s+\W\d{10}|\d{10}\W+\d{1}\s+[0-9]+\s+[0-9\.]+\s+\D+\s+[0-9\.]+\s+[0-9\.]+\s+\D+\d{2}\,\s+[0-9\*]+\s+[0-9\.\%]+\s+[0-9\.]+|\d{10}\D+\s+[0-9\.]+\s+\d{1}\s+\d{8}\s+[0-9\.]+\s+\D+\s+[0-9\.]+\s+[0-9\.]+\s+[0-9\.\%]+",text1)

    for linee in lines2:
        linee = linee.split()
        # print(linee)
        item = linee[0]
        list1.append(item)
    line_item = re.findall(r'(?m)\d{8}\s+\d+\.\d+\D+[0-9\,\.]+\s+[0-9\,\.]+\s+\d+\.\d+\D+[0-9\.\,]+|\d{8}\s+\D+\d+\,\s+\d+\D+\d+\s+[0-9\.\,]+\D+[0-9\,\.]+\s+[0-9\,\.]+\s+\d+\.\d+\D+[0-9\,\.]+|\d{8}\s+\d+\.\d+\D+[0-9\,\.]+\s+[0-9\,\.]+\D+\d+\,\s+\d+\D+\d+\s+\d+\.\d+\D+[0-9\.\,]+|\d{8}\s+\d+\.\d+\D+\w+\D+[0-9\.\,]+\s+\d+\.\d+\D+[0-9\.\,]+',data)

    for i in range(len(line_item)):
        # print(i)
        # line = i.strip('\n')
        #print(linee)
        line = line_item[i].split()
        print(line)
        data_dict['Hsn_Sac_code'] = line[0]
        print('Hsn_Sac_code :- ', data_dict['Hsn_Sac_code'])

        data_dict['Quantity'] = line[1]
        print('Quantity :- ', data_dict['Quantity'])
        data_dict['Rate_per_unit'] = line[3]
        print('Rate_per_Unit :- ', data_dict['Rate_per_unit'])
        data_dict['Total_value'] = line[-1]
        print('Total_value :- ', data_dict['Total_value'])

        try:
            data_dict['Item_code'] = list1[i]
        except:
            data_dict['Item_code'] = 'N/A'
        print('Item_code :- ', data_dict['Item_code'])


        
#    for line in lines:
#        line= line.split()
#        print(line)
#        Item_code=line[0]
#        Hsn_Sac_code=line[1]
#        Quantity=line[2]
#        Rate_per_unit=line[-2]
#        Total_value=line[-1]
#        data_dict['Vehicle_Number']= 'N/A'
#        data_dict['Item_code']=Item_code
#        data_dict['Hsn_Sac_code']=Hsn_Sac_code
#        data_dict['Quantity']=Quantity
#        data_dict['Rate_per_unit']=Rate_per_unit
#        data_dict['Total_value']=Total_value
 #       print(data_dict)

        query = "insert into lohia2 values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        value = (
        data_dict['Vendor_Name'], data_dict['Invoice_Number'], data_dict[' Invoice_Date '], data_dict['Po_Number'],
        data_dict['Po_Date'], data_dict['Lohia_Pan_Number'], data_dict['Gstin_client'], data_dict['Gstin_Lohia '],
        data_dict['Item_code'], data_dict['Hsn_Sac_code'], data_dict['Quantity'], data_dict['Rate_per_unit'],
        data_dict['Total_value'], data_dict['Grand_Total'], data_dict['Vehicle_Number'])
        cursor.execute(query, value)
        conn.commit()
        print("record inserted")

        

for file in os.listdir(r'C:\Users\Preety\Desktop\sequelstring\extraction\Vaibhav_Both'):  # folder pdf
    extract_all(r"C:\Users\Preety\Desktop\sequelstring\extraction\Vaibhav_Both\\" + file)


