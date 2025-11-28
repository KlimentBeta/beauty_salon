import pandas as pd
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import Database

db = Database()

def init_data_clientservice(df_client_service):
    initial_client_service = []

    for index, row in df_client_service.iterrows():
        client_service_data = {}
        client_id = get_client_id(row['Клиент'])
        service_id = get_service_id(row['Услуга'])
        
        
        if service_id != None and client_id != None:
            client_service_data['ServiceID'] =  service_id
            client_service_data['ClientID'] =  client_id
            client_service_data['StartTime'] =  row['Начало оказания услуги']

            initial_client_service.append(client_service_data)

    return initial_client_service

def get_client_id(client):
    id = db.get_client_id(client)
    return id

def get_service_id(service):
    id = db.get_service_id(service)
    return id

def init_data_client(clientFields, df_client):
    initial_client = []
    
    for index, row in df_client.iterrows():
        client_data = {}
        
        for col_name, value in row.items():
            if col_name in clientFields:
                if col_name.strip() == 'Пол':
                    value = prepare_gender(value)
                    if value == None:
                        value = 'н'

                mapped_field = clientFields[col_name]
                client_data[mapped_field] = value
                    
        initial_client.append(client_data)
    return initial_client

def init_data_service(serviceFields, df_service, images_path='assets/service_photo/'):
    initial_services = []
    
    for index, row in df_service.iterrows():
        service_data = {}
        
        for col_name, value in row.items():
            if col_name == ' Главное изображение':
                value = images_path + value.rsplit('\\', 1)[-1]
            
            if col_name in serviceFields:
                mapped_field = serviceFields[col_name]
                
                if mapped_field == 'DurationInSeconds':
                    value = convert_duration_to_seconds(value)
                
                elif mapped_field == 'Cost':
                    value = convert_price_to_number(value)
                
                elif mapped_field == 'Discount':
                    value = convert_discount(value)
                
                service_data[mapped_field] = value
        
        initial_services.append(service_data)
    
    return initial_services

def convert_discount(discount_str):
    try:
        discount_str = str(discount_str).strip().lower()
        
        if 'нет' in discount_str or discount_str == '' or discount_str == '0':
            return 1.0  # Без скидки
        elif '%' in discount_str:
            discount_percent = int(''.join(filter(str.isdigit, discount_str)))
            return (100 - discount_percent) / 100.0
        else:
            discount_percent = int(''.join(filter(str.isdigit, discount_str)))
            return (100 - discount_percent) / 100.0
    except:
        return 1.0  # По умолчанию без скидки
    
def convert_duration_to_seconds(duration_str):
    try:
        if 'мин' in duration_str:
            minutes = int(''.join(filter(str.isdigit, duration_str)))
            return minutes * 60
        elif 'сек' in duration_str:
            return int(''.join(filter(str.isdigit, duration_str)))
        else:
            return int(duration_str)
    except:
        return 0  # или какое-то значение по умолчанию

def convert_price_to_number(price_str):
    try:
        clean_price = ''.join(filter(lambda x: x.isdigit() or x == '.', str(price_str)))
        return float(clean_price) if clean_price else 0.0
    except:
        return 0.0

def prepare_gender(gender):
    if len(gender.strip()) > 1:
        if 'муж' in gender:
            return 'м'
        elif 'жен' in gender: 
            return 'ж'
        else:
            return None

def main():
    file_path = "./data/service.csv"
    df_service = pd.read_csv(file_path, sep=";")
    service_fields = {"Наименование услуги": 'Title', " Стоимость": 'Cost', " Длительность": 'DurationInSeconds', "skip": 'Description', " Действующая скидка": 'Discount', " Главное изображение": 'MainImagePath'}

    init_service = init_data_service(service_fields, df_service)
    db.initialize_table("Service", init_service)

    file_path2 = "./data/Client.txt"
    df_client = pd.read_csv(file_path2, sep=",")

    init_gender = [{'Code': 'м', 'Name': 'мужской'}, {'Code': 'ж', 'Name': 'женский'}, {'Code': 'н', 'Name': 'нет'}]
    db.initialize_table("Gender", init_gender)

    client_fields = {"Фамилия": 'LastName', " Имя": 'FirstName', " Отчество": 'Patronymic', " Пол": 'GenderCode', " Телефон": 'Phone', " Дата рождения": 'Birthday', " Email":'Email'," Дата регистрации": 'RegistrationDate'}
    init_client = init_data_client(client_fields, df_client)    
    db.initialize_table("Client", init_client)

    file_path3 = './data/serviceclient.xlsx'
    df_client_service = pd.read_excel(file_path3)
    init_client_service = init_data_clientservice(df_client_service)
    db.initialize_table("ClientService", init_client_service)

if __name__ == "__main__":
    main()

