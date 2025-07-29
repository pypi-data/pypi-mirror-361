import logging

from vlcishared.gestion_fechas.gestion_fechas_servicio import GestionFechasServicio


class GestionFechas:
    """
    Clase con métodos orquestadores de gestión de fechas (recuperación automática de las ETLs).
    """

    def __init__(self, etl_nombre: str, tipo: str = "fen", config: dict[str, str] = {"formato_fecha": "%Y-%m-%dT%H:%M:%S%z"}):
        """
        Inicializa la clase orquestadora con el servicio de gestión de fechas.

        Argumentos:
            - etl_nombre (str): Nombre de la ETL.
            - tipo (str): Tipo de fechas manejado en la ETL. Debe ser "fen" o "rango". Valor por defecto "fen".
            - config (dict): Configuración adicional.

        Raises:
            Exception: Si el valor recibido en 'tipo' es incorrecto.
        """
        if tipo != "rango" and tipo != "fen":
            raise ValueError(f"Tipo de gestión de fechas no reconocido: {tipo}")
        self.log = logging.getLogger(__name__)
        self.etl_nombre = etl_nombre
        self.tipo = tipo
        self.servicio = GestionFechasServicio(etl_nombre, config)

    def tiene_gestion_de_fechas(self) -> bool:
        """
        Verifica si existe una ETL con el nombre recibido en la tabla de gestión de fechas.

        Retorna:
            - bool: True si hay que recuperar datos, False en caso contrario.
        """
        self.log.info(f"Evaluando si existe ETL '{self.etl_nombre}' para la gestión de fechas.")
        return self.servicio.tiene_gestion_de_fechas()

    def es_necesaria_ejecucion(self) -> bool:
        """
        Verifica si es necesario recuperar datos según el estado y fecha de la ETL.

        Retorna:
            - bool: True si hay que recuperar datos, False en caso contrario.
        """
        self.log.info(f"Evaluando si se debe ejecutar ETL '{self.etl_nombre}'")
        if self.tipo == "fen":
            return self.servicio.es_necesaria_ejecucion("fen")
        elif self.tipo == "rango":
            return self.servicio.es_necesaria_ejecucion("fen_fin")

    def inicio_gestion_fechas_fen(self) -> str:
        """
        Inicia la gestión de fechas, actualizando estado a 'EN PROCESO' y obteniendo la fecha a procesar.

        Retorna:
            - str: Fecha formateada para la ETL.

        """
        self.log.info(f"Iniciando gestión de fechas FEN para ETL '{self.etl_nombre}'.")
        retorno = self.servicio.obtener_fecha_fen_a_procesar()
        self.servicio.actualizar_estado_etl("EN PROCESO")
        return retorno

    def inicio_gestion_fechas_rango(self) -> dict[str, str]:
        """
        Inicia la gestión de fechas, actualizando estado a 'EN PROCESO' y obteniendo las fechas a procesar.

        Retorna:
            - dict[str, str]: Diccionario con las claves 'fen_inicio' y 'fen_fin', fechas formateadas para la ETL.
        """
        self.log.info(f"Iniciando gestión de fechas rango para ETL '{self.etl_nombre}'.")
        retorno = self.servicio.obtener_rango_fechas_a_procesar()
        self.servicio.actualizar_estado_etl("EN PROCESO")
        return retorno

    def fin_gestion_fechas_OK(self):
        """
        Finaliza el proceso marcando estado 'OK' y avanza la fecha (fen) o rango (fen_inicio y fen_fin) según el tipo indicado.
        """
        self.log.info(f"Fin gestión de fechas OK para ETL '{self.etl_nombre}'.")
        if self.tipo == "fen":
            self.servicio.calcular_y_actualizar_siguiente_fen()
        elif self.tipo == "rango":
            self.servicio.calcular_y_actualizar_siguiente_rango()

        self.servicio.actualizar_estado_etl("OK")

    def fin_gestion_fechas_KO(self) -> None:
        """
        Finaliza el proceso marcando estado 'ERROR' sin avanzar la fecha.
        """
        self.log.info(f"Fin gestión de fechas KO para ETL '{self.etl_nombre}'.")
        self.servicio.actualizar_estado_etl("ERROR")
