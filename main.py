import os
import openai
import tkinter as tk
import sqlite3
import json
import pandas as pd
import re

openai.api_key = os.getenv("OPENAI_API_KEY")
vDATABASE_PATH = "resources/sql_lite.db"
vDataBaseConnection = sqlite3.connect(vDATABASE_PATH)

def action_1(iEvent):
    vPrompt = vTextInput.get("1.0", "end-1c")
    try:
        print("")
        print("Prompt user: ", vPrompt)
        print("Processing...")
        vSqlGenerated = nlp2sql(vPrompt)
        print("\tSQL generated: ", vSqlGenerated)
        print("\n")
        vDataFrame = pd.read_sql_query(vSqlGenerated, con = vDataBaseConnection)
        print(vDataFrame[0:10])
    except Exception as ex:
        print("Exception: ", ex)

def nlp2sql(iPromptUser):
    vResult = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "Tu eres un bot que genera querys de SQLLite en JSON usando una entrada de texto en Español"},
                {"role": "user", "content": """Tu tabla es TB_NETFLIX_DATA (show_id,type,title,director,cast,country,date_added,release_year,rating,duration,listed_in,description), dime todos los filmes que tegan un director nulo. Con la consulta en un JSON."""},
                {"role": "assistant", "content": "{\"sql\": \"SELECT * FROM TB_NETFLIX_DATA WHERE director IS NULL\"}"},
                {"role": "user", "content": iPromptUser + ". Con la consulta en un JSON en el atributo sql."}
            ]
        )
    vJSON = vResult["choices"][0]["message"]["content"]
    try:
        print("\tJSON generated: ", vJSON)
        vSql = json.loads(vJSON)["sql"]
    except Exception as ex:
        print("\tError procesing JSON: ", ex)
        vJSON = re.findall(
                r'\b(?<!\\)([\'"])[^\1]*?\1(?!\1)',
                vJSON
            )[0]
        print("\tNew JSON: ", vJSON)
        vSql = json.loads(vJSON)["sql"]
    return vSql

vWindow = tk.Tk()
vTextInput = tk.Text()
vActionButton = tk.Button(text = "Generate SQL")
vActionButton.bind("<Button-1>", action_1)
vTextInput.pack()
vActionButton.pack()
vWindow.mainloop()