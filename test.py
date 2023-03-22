import os
import openai

openai.api_key = "API_KEY" #os.getenv("OPENAI_API_KEY")

vPromptUser = "dime todos los usuarios que tuvieron aumentos en la deudas superiores a 1 millón y su deuda inicial era 0"
print("Prompt user: ", vPromptUser)

vResult = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
        {"role": "system", "content": "Eres un asistente en español que genera consultas Oracle SQL."},
        {"role": "user", "content": """La tabla es FCT_CARTERA_TEMPRANA_AGG, Tabla de hechos para visualización, que guarda los datos por día.
FCT_CARTERA_TEMPRANA_AGG:
Columnas de la tabla: FECHA_INSTALACION,FECHA_CREACION_ORDEN,CREATED_T,FECHA_FIN_PERIODO_ORDEN,FECHA_LIMITE_PAGO_ORDEN,SK_CATEGORIA,SK_DIRECCION,SK_ESTADO_FINANCIERO,SK_ESTADO_PRODUCTO,SK_TIPO_PRODUCTO,SK_CICLO,SK_ESTADO_CORTE,SK_RECUPERADO,SK_CIERRE_COMERCIAL,SK_PLAN_DIFERIDO,CONTRATO,PRODUCTO,NUMERO_PERSONAS_CARGO,ANTIGUEDAD_VIVIENDA,INGRESOS_MENSUALES,GASTOS_MENSUALES,DEUDA_VENCIDA,DEUDA_NO_VENCIDA,DEUDA_CORRIENTE,DEUDA_DIFERIDA,DEUDA_TOTAL,CANTIDAD_REFINANCIACIONES,CANTIDAD_FINANCIACIONES,ICV_60,PREDICTION,PROBABILITY,ICV_DEUDA_60,ICV_60_ZONA,SK_TIPO_VIVIENDA,SK_OCUPACION,SK_NIVEL_ESTUDIOS,SK_ESTADO_CIVIL,SK_SUBSCRIPTION,SK_GENERO,TOTAL_ICV,SK_EMPRESA,EDAD_BASE,ORDEN_CARTERA_TEMPRANA,SK_EDAD,EDAD,PERIODO_ORDEN
Solo da un query Oracle SQL sin comentarios: dime el usuario con la mayor deuda en el mes de marzo.
"""},
        {"role": "assistant", "content": """WITH vwData AS (
    SELECT CONTRATO, CREATED_T, SUM(DEUDA_TOTAL) DEUDA_TOTAL FROM FCT_CARTERA_TEMPRANA_AGG WHERE EXTRACT(MONTH FROM CREATED_T) = 3 AND EXTRACT(YEAR FROM CREATED_T) = EXTRACT(YEAR FROM SYSDATE) GROUP BY CONTRATO, CREATED_T
)
SELECT d.* FROM vwData d WHERE ROWNUM = 1
"""},
        {"role": "user", "content": vPromptUser}
    ]
)

print("Message:", vResult["choices"][0]["message"]["content"])