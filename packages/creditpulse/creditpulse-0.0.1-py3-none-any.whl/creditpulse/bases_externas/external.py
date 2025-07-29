"""

External Database Schema standarization
"""

from enum import Enum


from creditpulse.bases_externas.database import Database
from creditpulse.bases_externas.truora import Truora
from creditpulse.bases_externas.schema import CountryCode, PersonType


class BasesDeDatos(str, Enum):
    """Supported country codes for checks"""
    TRUORA = "tr"  # International Lists


class ExternalDatabases:

    def __init__(self, *bases: BasesDeDatos):

        if len(bases) == 0:
            raise Exception('Debe seleccionar al menos una base de datos')

        self.data_bases: [Database] = []

        for base in bases:
            if base == BasesDeDatos.TRUORA:
                self.data_bases.append(Truora())

    def obtain_data(self, identificacion: str, natural: bool = True):
        response = {}

        for base in self.data_bases:
            response[base.get_name()] = base.create_check(
                identificacion=identificacion,
                person_type=PersonType.PERSONA if natural else PersonType.COMPANIA,
                pais=CountryCode.COLOMBIA,
                autorizacion_datos=True
            )

        return response
