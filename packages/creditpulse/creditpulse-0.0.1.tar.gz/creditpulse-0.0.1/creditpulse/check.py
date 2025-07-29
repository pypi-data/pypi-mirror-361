"""
Clase pincipal para analysis de creditos financieros

"""
import logging

from creditpulse.bases_externas.external import ExternalDatabases, BasesDeDatos
from creditpulse.bases_externas.truora import Truora


class Check:
    """
        Clase que provee interfaz para analysis the personas
    """

    def __init__(self):
        # Module logger
        self.logger = logging.getLogger(__name__)

    def get_data(self, identificacion: str, natural: bool = True):
        """

        :return: Analysis financiero de la persona natural o juridica
        """
        external = ExternalDatabases(BasesDeDatos.TRUORA)

        return external.obtain_data(identificacion=identificacion, natural=natural)
