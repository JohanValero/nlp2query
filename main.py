import os
import openai
import tkinter as tk
import sqlite3
import pandas as pd

openai.api_key = os.getenv("OPENAI_API_KEY")
vDATABASE_PATH = "resources/sql_lite.db"
vDataBaseConnection = sqlite3.connect(vDATABASE_PATH)

def action_1(iEvent):
    vPrompt = vTextInput.get("1.0", "end-1c")
    vSqlGenerated = nlp2sql(vPrompt)
    print("\n")
    print("\tPrompt user: ", vPrompt)
    print("\tSQL generated: ", vSqlGenerated)
    print("\n")
    try:
        vDataFrame = pd.read_sql_query(vSqlGenerated, con = vDataBaseConnection)
        print(vDataFrame[0:10])
    except Exception as ex:
        print("Exception: ", ex)

def nlp2sql(iPromptUser):
    vResult = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "Tu eres un bot que genera querys de SQLLite usando una entrada de texto en Español"},
                {"role": "user", "content": """Tu tabla es TB_NETFLIX_DATA (show_id,type,title,director,cast,country,date_added,release_year,rating,duration,listed_in,description), dime todos los filmes que tegan un director nulo"""},
                {"role": "assistant", "content": "SELECT * FROM TB_NETFLIX_DATA WHERE director IS NULL"},
                {"role": "user", "content": iPromptUser}
            ]
        )
    return vResult["choices"][0]["message"]["content"]

vWindow = tk.Tk()
vTextInput = tk.Text()
vActionButton = tk.Button(text = "Generate SQL")
vActionButton.bind("<Button-1>", action_1)
vTextInput.pack()
vActionButton.pack()
vWindow.mainloop()