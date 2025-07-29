from datetime import datetime

from dateutil.relativedelta import relativedelta


class GestionFechasValidador:
    @staticmethod
    def validar_estado(estado):
        if estado not in {"EN PROCESO", "OK", "ERROR"}:
            raise Exception(f"El estado de la ETL tiene un valor no válido: '{estado}'.")

    @staticmethod
    def validar_fecha(fecha, campo_fecha):
        if not fecha or not isinstance(fecha, datetime):
            raise Exception(f"La ETL no posee un valor válido en '{campo_fecha}': {fecha} ({type(fecha).__name__})")

    @staticmethod
    def validar_intervalo(intervalo, campo_intervalo):
        if not intervalo or not isinstance(intervalo, relativedelta):
            raise Exception(f"La ETL no posee un valor válido en '{campo_intervalo}': {intervalo} ({type(intervalo).__name__})")
