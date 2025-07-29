"""
Definicion de tipos de datos para base de datos externas
"""

from datetime import datetime
from typing import Literal
from enum import Enum

from pydantic import BaseModel, Field


class CountryCode(str, Enum):
    """Supported country codes for checks"""
    ALL = "ALL"  # International Lists
    BRAZIL = "BR"  # Brazil
    COLOMBIA = "CO"  # Colombia
    CHILE = "CL"  # Chile
    COSTA_RICA = "CR"  # Costa Rica
    MEXICO = "MX"  # Mexico
    PERU = "PE"  # Peru


class PersonType(str, Enum):
    """Supported country codes for checks"""
    PERSONA = "person"  # Used to perform a background check on a person.
    VEHICULO = "vehicle"  # Used to perform a background check on a driver and their vehicle
    COMPANIA = "company"  # Used to perform a background check on a company


class CheckStatus(str, Enum):
    """Status values for checks"""
    NOT_STARTED = "not_started"  # The check is enqueued and the data collection has not started yet
    IN_PROGRESS = "in_progress"  # Data is being collected but some data sources may have finished already
    DELAYED = "delayed"  # One or more data sources are taking a long time to query the data. Most data sources will have already finished
    COMPLETED = "completed"  # The check finished and 70% or more of the data sources did not end in error status
    ERROR = "error"  # The check finished and more than 30% of the data sources ended in error status


class TruoraCheck(BaseModel):
    """
    Definicion para Check de truora
    """
    check_id: str = Field(..., description="Unique identifier for the check")
    country: CountryCode = Field(
        ...,
        description="""
            Country code - 
            ALL for International Lists, 
            BR for Brazil, 
            CO for Colombia, 
            CL for Chile, 
            CR for Costa Rica, 
            MX for Mexico, 
            PE for Peru
        """
    )
    creation_date: datetime = Field(..., description="When the check was created")
    name_score: int = Field(..., description="Score for name matching")
    id_score: int = Field(..., description="Score for ID matching")
    score: int = Field(..., description="Overall check score")
    status: CheckStatus = Field(..., description="Current status of the check")
    update_date: datetime = Field(..., description="When the check was last updated")
    billing_hub: str = Field(..., description="Billing hub identifier")
    national_id: str = Field(..., description="National ID number being checked")
    type: Literal["person"] = Field(..., description="Type of check (person, business, etc.)")


class TruoraCheckData(BaseModel):
    """
    Definicion para la respuesta de truora
    """
    check: TruoraCheck = Field(..., description="Check details")
    details: str = Field(..., description="API endpoint for detailed check information")
    self: str = Field(..., description="API endpoint for this check resource")


class GeneralDatabase(BaseModel):
    score: int = Field(..., description="Overall check score")
    creation_date: datetime = Field(..., description="When the check was created")
    national_id: str = Field(..., description="National ID number being checked")