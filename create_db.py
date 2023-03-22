import sqlite3
import pandas as pd

vDataBasePath = "resources/sql_lite.db"
vDataBaseConnection = sqlite3.connect(vDataBasePath)

# https://www.kaggle.com/datasets/shivamb/netflix-shows
vDatasetPath = "resources/netflix_titles.csv"
vDataFrame = pd.read_csv(vDatasetPath)

print(vDataFrame[0:10])
print("Size of the data: ", len(vDataFrame))

vDataFrame.to_sql("TB_NETFLIX_DATA", vDataBaseConnection, if_exists="replace")
print("Database created.")