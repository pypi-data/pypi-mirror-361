import unittest

from creditpulse.bases_externas.truora import Truora
from creditpulse.bases_externas.schema import CountryCode, PersonType


class TestTruoraCheck(unittest.TestCase):

    def test_simple_request(self):
        client = Truora()
        client.create_check(
            identificacion='1053778047',
            person_type=PersonType.PERSONA,
            pais=CountryCode.COLOMBIA,
            autorizacion_datos=True
        )
