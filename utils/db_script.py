import pandas as pd

import sys, os, json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import Database


# file_path = "./data/serviceclient.xlsx"
# df = pd.read_excel(file_path)
# first_col = df[df.columns[0]]

def init_data_client(clientFields, df_client):
    initial_client = []
    
    for index, row in df_client.iterrows():
        client_data = {}
        
        for col_name, value in row.items():

            
            if col_name in clientFields:
                mapped_field = clientFields[col_name]
                
                # Преобразуем DurationInSeconds в числа
                if mapped_field == 'DurationInSeconds':
                    value = convert_duration_to_seconds(value)
                
                # Преобразуем цену в числа (убираем валюту)
                elif mapped_field == 'Cost':
                    value = convert_price_to_number(value)
                
                # Преобразуем скидку в множитель
                elif mapped_field == 'Discount':
                    value = convert_discount(value)
                
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
                
                # Преобразуем DurationInSeconds в числа
                if mapped_field == 'DurationInSeconds':
                    value = convert_duration_to_seconds(value)
                
                # Преобразуем цену в числа (убираем валюту)
                elif mapped_field == 'Cost':
                    value = convert_price_to_number(value)
                
                # Преобразуем скидку в множитель
                elif mapped_field == 'Discount':
                    value = convert_discount(value)
                
                service_data[mapped_field] = value
        
        initial_services.append(service_data)
    
    return initial_services

def convert_discount(discount_str):
    """Преобразует строку скидки в числовой множитель"""
    try:
        discount_str = str(discount_str).strip().lower()
        
        if 'нет' in discount_str or discount_str == '' or discount_str == '0':
            return 1.0  # Без скидки
        elif '%' in discount_str:
            # "25%" -> 0.75 (цена умножается на 0.75)
            discount_percent = int(''.join(filter(str.isdigit, discount_str)))
            return (100 - discount_percent) / 100.0
        else:
            # Если просто число, считаем это процентом
            discount_percent = int(''.join(filter(str.isdigit, discount_str)))
            return (100 - discount_percent) / 100.0
    except:
        return 1.0  # По умолчанию без скидки
    
def convert_duration_to_seconds(duration_str):
    """Преобразует строку длительности в секунды"""
    try:
        if 'мин' in duration_str:
            # "45 мин." -> 45 * 60 = 2700 секунд
            minutes = int(''.join(filter(str.isdigit, duration_str)))
            return minutes * 60
        elif 'сек' in duration_str:
            # "1200 сек." -> 1200 секунд
            return int(''.join(filter(str.isdigit, duration_str)))
        else:
            # Если просто число, считаем что это секунды
            return int(duration_str)
    except:
        return 0  # или какое-то значение по умолчанию

def convert_price_to_number(price_str):
    """Преобразует строку цены в число"""
    try:
        # Убираем всё кроме цифр и точки
        clean_price = ''.join(filter(lambda x: x.isdigit() or x == '.', str(price_str)))
        return float(clean_price) if clean_price else 0.0
    except:
        return 0.0


def main():
    db = Database()

    file_path = "./data/service.csv"
    df_service = pd.read_csv(file_path, sep=";")
    serviceFields = {"Наименование услуги": 'Title', " Стоимость": 'Cost', " Длительность": 'DurationInSeconds', "skip": 'Description', " Действующая скидка": 'Discount', " Главное изображение": 'MainImagePath'}

    init_service = init_data_service(serviceFields, df_service)
    # db.initialize_table("Service", init_service)

    file_path2 = "./data/Client.txt"
    df = pd.read_csv(file_path2, sep=",")
    
    # names = df["Фамилия"]
    # images = df[" Имя"]
    durations1 = df["Фамилия Имя Отчество"]
    durations2 = df[" Пол"]
    durations3 = df[" Телефон"]
    durations4 = df[" Дата рождения"]
    prices = df[" Email"]
    discounts = df[" Дата регистрации"]
    print(durations1)



if __name__ == "__main__":
    main()

