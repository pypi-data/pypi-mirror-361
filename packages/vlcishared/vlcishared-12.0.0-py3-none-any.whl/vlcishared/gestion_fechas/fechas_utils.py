import pytz

from vlcishared.env_variables.config import get_config


def transformar_a_tz_config(fecha):
    if not fecha:
        return None

    zona_horaria = pytz.timezone(get_config("TIMEZONE"))

    if fecha.tzinfo is None:
        return zona_horaria.localize(fecha)
    else:
        return fecha.astimezone(zona_horaria)
