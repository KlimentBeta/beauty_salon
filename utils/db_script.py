import pandas as pd


file_path = "./data/data.xlsx"
df = pd.read_excel(file_path)
first_col = df[df.columns[0]]

file_path = "./data/service.csv"
df = pd.read_csv(file_path, sep=";")

names = df["Наименование услуги"]
images = df[" Главное изображение"]
durations = df[" Длительность"]
prices = df[" Стоимость"]
discounts = df[" Действующая скидка"]

print(discounts)
