"""
    Clase abstracta para definir una base de datos
"""

from creditpulse.bases_externas.schema import PersonType, CountryCode, GeneralDatabase
from creditpulse.requests.request_manager import RequestActionManager
from abc import ABC, abstractmethod


class Database(RequestActionManager, ABC):

    @abstractmethod
    def create_check(self, identificacion: str,
                     person_type: PersonType,
                     autorizacion_datos: bool = False,
                     pais: CountryCode = CountryCode.COLOMBIA
                     ) -> GeneralDatabase:
        """
        Implementacion de
        :param identificacion:
        :param person_type:
        :param autorizacion_datos:
        :param pais:
        :return:
        """

    @abstractmethod
    def get_name(self) -> str:
        """
        Da el nombre de la actual base de datos
        :return:
        """

    @abstractmethod
    def to_general(self) -> GeneralDatabase:
        """
        Traduce base de datos a general
        :return:
        """
