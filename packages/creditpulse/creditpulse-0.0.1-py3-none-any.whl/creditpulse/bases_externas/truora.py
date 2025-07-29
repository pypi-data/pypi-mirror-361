"""
    Request manager ara base de datos externa truora
"""
import json
import os
import logging
from typing import Optional

import requests
from creditpulse.requests.request_manager import RequestManager
from creditpulse.bases_externas.schema import TruoraCheckData, CountryCode, PersonType, CheckStatus, GeneralDatabase
from creditpulse.common.error_messages import (
    AutorizacionDatosPersonales,
    TruoraApiKeyRequired,
    TruoraGeneralError
)

from creditpulse.bases_externas.database import Database

# https://www.postman.com/truora-api-docs/truora-api-docs/collection/iwmyaus/truora-collection
TRUORA_API_VERSIONS = '/v1'
TRUORA_BASE_URL = 'https://api.checks.truora.com' + TRUORA_API_VERSIONS
CHECK_URL = TRUORA_BASE_URL + '/checks'
CHECK_URL_DETAILS = TRUORA_BASE_URL + '/checks/{}/details'
CHECK_SETTINGS_URL = ' https://api.checks.truora.com/v1/settings'

settings_data = {
    'names_matching_type': 'exact',
    'retries': True,
    'max_duration': '3m'
}


class Truora(Database):
    """

    Clase principal para consultar base de datos externa truora
    """

    def get_name(self) -> str:
        return 'truora'

    def _get_check(self, check_id: str):
        return self.session.post(CHECK_URL + "/" + check_id)

    def on_execute(self) -> requests.Response:
        return self._get_check(self.tcheck.check.check_id)

    def success_callback(self, response: requests.Response) -> None:
        self.logger.info("Consulta a Base De datos ha sido finalizada")
        response_json = response.json()
        self.tcheck = TruoraCheckData(**response_json)
        self.status = self.tcheck.check.status

    def error_callback(self, response: requests.Response) -> None:
        response_json = response.json()
        inter_check: TruoraCheckData = TruoraCheckData(**response_json)

        if inter_check.check.status == CheckStatus.DELAYED:
            self.logger.warning("Consulta base de datos ha sido delayed")

        self.status = inter_check.check.status

    def is_request_successful(self, response: requests.Response) -> bool:
        """

        :param response:
        :return:
        """
        if response.status_code in [200, 203]:
            response_json = response.json()
            try:
                t_checker: TruoraCheckData = TruoraCheckData(**response_json)
                return t_checker.check.status == CheckStatus.COMPLETED
            except (KeyError, TypeError):
                return False
        return False

    def __init__(self):
        """

        """

        self.api_key = os.environ.get('TRUORA_API_TOKEN')

        if self.api_key is None:
            raise TruoraApiKeyRequired()

        self.session = requests.session()

        self.session.headers.update({
            "Truora-API-Key": self.api_key,
            'Accept': 'application/json'
        })

        self.request_manager = RequestManager(
            manager=self,
            max_retries=10
        )

        self.tcheck: Optional[TruoraCheckData] = None

        self.logger = logging.getLogger(__name__)

        self.status: CheckStatus = CheckStatus.NOT_STARTED

    def create_check(self,
                     identificacion: str,
                     person_type: PersonType,
                     autorizacion_datos: bool = False,
                     pais: CountryCode = CountryCode.COLOMBIA
                     ):
        """
        Funcion principal para consulatr base de datos externa tuora

        :param identificacion:
        :param person_type:
        :param autorizacion_datos:
        :param pais:
        :return:
        """
        if not autorizacion_datos:
            raise AutorizacionDatosPersonales()

        settings_response = self.session.post(CHECK_SETTINGS_URL, data=settings_data)
        response_json = settings_response.json()

        if settings_response.status_code not in [200, 201, 202, 203]:
            self.logger.error(f"Error al crear consulta base de datos externa: {response_json['message']}")
            raise TruoraGeneralError(f"Error al crear consulta base de datos externa: {response_json['message']}")

        form_data = {
            'national_id': identificacion,
            'country': pais,
            'type': person_type,
            'user_authorized': autorizacion_datos,
            'force_creation': True
        }

        response = self.session.post(CHECK_URL, data=form_data)
        response_json = response.json()

        if response.status_code not in [200, 201, 202, 203]:
            self.logger.error(f"Error al crear consulta base de datos externa: {response_json['message']}")
            raise TruoraGeneralError(f"Error al crear consulta base de datos externa: {response_json['message']}")

        self.tcheck = TruoraCheckData(**response_json)

        if self.tcheck is None:
            raise TruoraGeneralError('Check de truora no fue creado')

        self.request_manager.start()

        open('file.txt', "w+").write(json.dumps(self.get_check_details(self.tcheck.check.check_id)))

        return self.to_general()

    def get_check(self, check_id: str) -> TruoraCheckData:
        """

        :param check_id:
        :return:
        """
        response = self._get_check(check_id=check_id)
        if response.status_code not in range(200, 203):
            self.logger.error(response.text)
            raise TruoraGeneralError(response.text)

        response_json = response.json()
        return TruoraCheckData(**response_json)

    def get_check_details(self, check_id: str):
        """

        :param check_id:
        :return:
        """
        response = self.session.post(CHECK_URL_DETAILS.format(check_id))
        if response.status_code not in range(200, 203):
            self.logger.error(response.text)
            raise TruoraGeneralError(response.text)

        return response.json()

    def to_general(self) -> GeneralDatabase:
        """
        Traduce truora a general
        :return:
        """
        return GeneralDatabase(
            score=self.tcheck.check.score,
            creation_date=self.tcheck.check.creation_date,
            national_id=self.tcheck.check.national_id
        )
