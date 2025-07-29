import logging
import re
from datetime import datetime

from dateutil.relativedelta import relativedelta

from vlcishared.db.postgresql import PostgresConnector
from vlcishared.gestion_fechas.fechas_utils import transformar_a_tz_config
from vlcishared.gestion_fechas.gestion_fechas_excepciones import ETLNoRegistradaError
from vlcishared.gestion_fechas.proceso_etl import ProcesoETL


class GestionFechasRepositorio:
    """
    Repositorio para acceder a funciones SQL relacionadas con la gestión de fechas para ETLs.
    """

    def __init__(self, etl_nombre: str):
        """
        Inicializa el repositorio y guarda el nombre de la ETL.

        Args:
            etl_nombre (str): Nombre de la ETL.

        Raises:
            Exception: Si falla la conexión o carga del proceso ETL.
        """
        self.log = logging.getLogger(__name__)
        try:
            self.conector_db = PostgresConnector.instance()
        except Exception as e:
            self.log.error("GestionFechas requiere que PostgresConnector esté inicializado previamente.")
            raise e
        self.etl_nombre = etl_nombre
        self.proceso_etl = None

    def obtener_datos_etl(self) -> ProcesoETL:
        """
        Obtiene los datos de gestión de fechas de la ETL.

        Args:
            etl_nombre (str): Nombre de la ETL.

        Returns:
            ProcesoETL: Datos de la ETL.

        Raises:
            ValueError: Si la ETL no existe.
        """
        self.log.info(f"Obteniendo datos de gestión de fechas de la ETL '{self.etl_nombre}' desde la base de datos.")

        resultado = self.conector_db.execute_query(
            """SELECT etl_id, etl_nombre, estado, frecuencia::text AS frecuencia_text, "offset"::text as offset_text, fen, fen_inicio, fen_fin
            FROM vlci2.t_ref_gestion_fechas_etls WHERE etl_nombre = :etl_nombre""",
            {"etl_nombre": self.etl_nombre},
        )

        fila = resultado.mappings().first()

        if not fila:
            raise ETLNoRegistradaError(self.etl_nombre)

        self.proceso_etl = ProcesoETL(
            etl_id=fila["etl_id"],
            etl_nombre=fila["etl_nombre"],
            frecuencia=self._parsear_intervalo_postgres(fila["frecuencia_text"]),
            offset=self._parsear_intervalo_postgres(fila["offset_text"]),
            fen=transformar_a_tz_config(fila["fen"]),
            fen_inicio=transformar_a_tz_config(fila["fen_inicio"]),
            fen_fin=transformar_a_tz_config(fila["fen_fin"]),
            estado=fila["estado"],
        )

        return self.proceso_etl

    def actualizar_estado_etl(self, nuevo_estado: str) -> None:
        """
        Actualiza el estado de gestión de fechas de la ETL.

        Args:
            nuevo_estado (str): El nuevo estado ("OK", "EN PROCESO", "ERROR").
        """
        self.log.info(f"Actualizando el estado de la ETL '{self.etl_nombre}' a '{nuevo_estado}' en la base de datos.")
        self.conector_db.execute_query(
            "UPDATE vlci2.t_ref_gestion_fechas_etls SET estado = :estado WHERE etl_id = :etl_id",
            {
                "estado": nuevo_estado,
                "etl_id": self.proceso_etl.etl_id,
            },
        )

    def actualizar_fecha_etl(self, campo: str, nueva_fecha: datetime) -> None:
        """
        Actualiza un campo de fecha de la ETL.

        Args:
            campo (str): Nombre del campo de fecha.
            nueva_fecha (datetime): Nueva fecha a establecer.

        Raises:
            ValueError: Si el campo no es válido.
        """
        if campo not in ["fen", "fen_inicio", "fen_fin"]:
            raise ValueError(f"Campo con nombre {campo} no corresponde a un campo de fecha.")

        self.log.info(f"Actualizando el campo '{campo}' de la ETL '{self.etl_nombre}' a '{nueva_fecha}' en la base de datos.")
        self.conector_db.execute_query(
            f"UPDATE vlci2.t_ref_gestion_fechas_etls SET {campo} = :nueva_fecha WHERE etl_id = :etl_id",
            {
                "nueva_fecha": nueva_fecha,
                "etl_id": self.proceso_etl.etl_id,
            },
        )

    def _parsear_intervalo_postgres(self, intervalo_str):
        if not intervalo_str:
            return relativedelta()

        years = months = days = hours = minutes = seconds = 0

        match_year = re.search(r"(\d+)\s+years?", intervalo_str)
        if match_year:
            years = int(match_year.group(1))

        match_month = re.search(r"(\d+)\s+mons?", intervalo_str)
        if match_month:
            months = int(match_month.group(1))

        match_day = re.search(r"(\d+)\s+days?", intervalo_str)
        if match_day:
            days = int(match_day.group(1))

        match_time = re.search(r"(\d+):(\d+):(\d+)", intervalo_str)
        if match_time:
            hours = int(match_time.group(1))
            minutes = int(match_time.group(2))
            seconds = int(match_time.group(3))

        return relativedelta(
            years=years,
            months=months,
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
        )
