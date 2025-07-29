import calendar
import logging
from datetime import datetime

import pytz

from vlcishared.env_variables.config import get_config
from vlcishared.gestion_fechas.gestion_fechas_excepciones import ETLNoRegistradaError
from vlcishared.gestion_fechas.gestion_fechas_repositorio import GestionFechasRepositorio
from vlcishared.gestion_fechas.gestion_fechas_validador import GestionFechasValidador
from vlcishared.gestion_fechas.proceso_etl import ProcesoETL


class GestionFechasServicio:
    """
    Servicio encargado de la lógica de negocio para la gestión de fechas de ETLs.
    """

    def __init__(self, etl_nombre: str, config: dict[str, str]):
        """
        Inicializa el servicio.

        Args:
            - etl_nombre (str): Nombre de la ETL.
            - config (dict): Configuración adicional (por ejemplo, formato de fecha).
        """
        self.log = logging.getLogger(__name__)
        self.repositorio = GestionFechasRepositorio(etl_nombre)
        self.config = config

    def tiene_gestion_de_fechas(self):
        try:
            self.repositorio.obtener_datos_etl()
            return True
        except ETLNoRegistradaError:
            self.log.info(f"La ETL '{self.repositorio.etl_nombre}' no tiene gestión de fechas.")
            return False
        except Exception as e:
            self.log.info(f"Error al consultar gestión de fechas de la etl: {e}")
            raise

    def es_necesaria_ejecucion(self, campo_fecha: str) -> bool:
        """
        Determina si se deben recuperar datos según el estado y el campo de fecha indicado.

        Args:
            campo_fecha (str): Nombre del atributo de fecha a comparar ('fen', 'fen_fin').

        Returns:
            bool: True si corresponde recuperar datos, False en caso contrario.

        Raises:
            Exception: Si el estado o la fecha son inválidos.
        """
        try:
            proceso_etl = self.repositorio.obtener_datos_etl()
            self.log.info(
                f"Verificando si es necesaria la ejecución para ETL '{proceso_etl.etl_nombre}' con ID: {proceso_etl.etl_id}. Estado: '{proceso_etl.estado}'."
            )
            GestionFechasValidador.validar_estado(proceso_etl.estado)

            if proceso_etl.estado == "EN PROCESO":
                self.log.info("El estado de la ETL es 'EN PROCESO', no se puede ejecutar.")
                return False
            elif proceso_etl.estado == "ERROR":
                return True

            fecha_valor = getattr(proceso_etl, campo_fecha, None)
            GestionFechasValidador.validar_fecha(fecha_valor, campo_fecha)

            zona_horaria_madrid = pytz.timezone(get_config("TIMEZONE"))
            fecha_limite = datetime.now(zona_horaria_madrid)

            if proceso_etl.offset:
                GestionFechasValidador.validar_intervalo(proceso_etl.offset, "offset")
                fecha_limite -= proceso_etl.offset

            # Se evalúa si la frecuencia es mayor o igual a un día: se compara solo la fecha (sin hora)
            if proceso_etl.frecuencia.years >= 1 or proceso_etl.frecuencia.months >= 1 or proceso_etl.frecuencia.days >= 1:
                return fecha_valor.date() < fecha_limite.date()
            else:
                return fecha_valor < fecha_limite

        except Exception as e:
            self.log.exception(f"Error al evaluar necesidad de recuperar datos: {e}")
            raise

    def obtener_fecha_fen_a_procesar(self) -> str:
        """
        Obtiene y formatea la fecha fen para la ejecución de la ETL.

        Returns:
            - str: Fecha formateada.

        Raises:
            - Exception: Si no existe fecha válida.
        """
        try:
            proceso_etl = self.repositorio.proceso_etl
            self.log.info(f"Obteniendo fecha de gestión (fen) para ETL '{proceso_etl.etl_nombre}' con ID: {proceso_etl.etl_id}.")
            GestionFechasValidador.validar_fecha(proceso_etl.fen, "fen")

            return self._formatear_fecha(proceso_etl.fen)

        except Exception as e:
            self.log.exception(f"Error al obtener fecha de gestión: {e}")
            raise

    def obtener_rango_fechas_a_procesar(self) -> dict[str, str]:
        """
        Obtiene y formatea las fechas fen_inicio y fen_fin para la ejecución de la ETL.

        Returns:
            - dict[str, str]: Rango de fechas formateadas.

        Raises:
            - Exception: Si no existen fechas válidas.
        """
        try:
            proceso_etl = self.repositorio.proceso_etl
            self.log.info(f"Obteniendo fechas de gestión (fen_inicio y fen_fin) para ETL '{proceso_etl.etl_nombre}' con ID: {proceso_etl.etl_id}.")
            GestionFechasValidador.validar_fecha(proceso_etl.fen_inicio, "fen_inicio")
            GestionFechasValidador.validar_fecha(proceso_etl.fen_fin, "fen_fin")
            return {
                "fen_inicio": self._formatear_fecha(proceso_etl.fen_inicio),
                "fen_fin": self._formatear_fecha(proceso_etl.fen_fin),
            }
        except Exception as e:
            self.log.exception(f"Error al obtener rango de fechas de gestión: {e}")
            raise

    def actualizar_estado_etl(self, nuevo_estado: str) -> None:
        """
        Actualiza el estado de la ETL.

        Args:
            - nuevo_estado (str): Estado a establecer. Debe ser "OK", "EN PROCESO" o "ERROR".

        Raises:
            - Exception: Si el estado no es válido o falla la actualización.
        """
        try:
            proceso_etl = self.repositorio.proceso_etl
            self.log.info(f"Actualizando estado de ETL '{proceso_etl.etl_nombre}' con ID: {proceso_etl.etl_id} a '{nuevo_estado}'.")

            if nuevo_estado not in {"OK", "EN PROCESO", "ERROR"}:
                raise Exception(f"El estado recibido: '{nuevo_estado}' no es un estado válido.")

            self.repositorio.actualizar_estado_etl(nuevo_estado)
        except Exception as e:
            self.log.exception(f"Error al actualizar estado a '{nuevo_estado}': {e}")
            raise

    def calcular_y_actualizar_siguiente_fen(self) -> None:
        """
        Calcula y actualiza la siguiente fecha de procesamiento según la frecuencia.

        Raises:
            - Exception: Si el estado actual es inválido o faltan fechas.
        """
        try:
            proceso_etl = self.repositorio.proceso_etl
            self.log.info(f"Calculando siguiente fecha fen para ETL '{proceso_etl.etl_nombre}' con ID: {proceso_etl.etl_id}.")

            self._calcular_y_actualizar_fecha(proceso_etl, "fen")
        except Exception as e:
            self.log.exception(f"Error al calcular la siguiente fecha fen: {e}")
            raise

    def calcular_y_actualizar_siguiente_rango(self) -> None:
        """
        Calcula y actualiza la siguiente fecha de procesamiento de los campos fen_inicio y fen_fin según la frecuencia.

        Raises:
            - Exception: Si el estado actual es inválido o faltan fechas.
        """
        try:
            proceso_etl = self.repositorio.proceso_etl
            self.log.info(f"Calculando siguiente rango de fechas para ETL '{proceso_etl.etl_nombre}' con ID: {proceso_etl.etl_id}.")

            self._calcular_y_actualizar_fecha(proceso_etl, "fen_inicio")
            self._calcular_y_actualizar_fecha(proceso_etl, "fen_fin")
        except Exception as e:
            self.log.exception(f"Error al calcular el siguiente rango de fechas: {e}")
            raise

    def _calcular_y_actualizar_fecha(self, proceso_etl: ProcesoETL, campo: str):
        fecha_gestion = getattr(proceso_etl, campo)
        frecuencia = proceso_etl.frecuencia
        GestionFechasValidador.validar_fecha(fecha_gestion, campo)
        GestionFechasValidador.validar_intervalo(frecuencia, "frecuencia")

        # Se elimina la zona horaria (fecha naive) para evitar errores al sumar períodos (días/meses/horas),
        # ya que las operaciones de RelativeDelta no siempre se comportan bien con datetimes con tzinfo.

        fecha_naive = fecha_gestion.replace(tzinfo=None)
        nueva_fecha_naive = fecha_naive + frecuencia

        # Si la fecha original era el último día del mes, se fuerza que la nueva fecha también lo sea,
        # para evitar inconsistencias al sumar meses (ej. sumar 1 mes a 30 de abril da 31 de mayo).
        _, last_day_fecha_gestion = calendar.monthrange(fecha_gestion.year, fecha_gestion.month)
        es_ultimo_dia = fecha_gestion.day == last_day_fecha_gestion

        if es_ultimo_dia:
            _, last_day_nuevo_mes = calendar.monthrange(nueva_fecha_naive.year, nueva_fecha_naive.month)
            nueva_fecha_naive = nueva_fecha_naive.replace(day=last_day_nuevo_mes)

        time_zone = pytz.timezone(get_config("TIMEZONE"))
        nueva_fecha = time_zone.localize(nueva_fecha_naive)

        self.repositorio.actualizar_fecha_etl(campo, nueva_fecha)
        self.log.info(f"Nueva fecha '{campo}' actualizada a: {nueva_fecha}")

    def _formatear_fecha(self, fecha) -> str:
        """
        Formatea un objeto datetime según el formato configurado.

        Args:
            fecha (datetime): Fecha a formatear.

        Returns:
            str: Fecha formateada.

        Raises:
            ValueError: Si la fecha no es un datetime.
        """
        formato = self.config.get("formato_fecha", "%Y-%m-%dT%H:%M:%S%z")
        return fecha.strftime(formato)
