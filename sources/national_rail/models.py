"""
National Rail Pydantic Models
"""
from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel


class LocationDetails(BaseModel):
    """
    Information about an Origin / Destination
    """

    locationName: str
    crs: str
    via: Optional[str]
    futureChangeTo: Optional[str]
    assocIsCancelled: Optional[bool]


class Location(BaseModel):
    """ "
    Locations are in lists
    """

    location: List[LocationDetails]


class Formation(BaseModel):
    """
    Load and Coat information
    Note: Coaches is None for Great Northern
    """

    avgLoading: int
    coaches: Optional[str]


class Service(BaseModel):
    """
    The train services returned
    """

    sta: Optional[str]
    eta: Optional[str]
    std: str
    etd: str
    platform: Optional[str]
    operator: str
    operatorCode: str
    isCircularRoute: Optional[bool]
    isCancelled: Optional[bool]
    filterLocationCancelled: Optional[bool]
    serviceType: str
    length: Optional[str]
    detachFront: Optional[bool]
    isReverseFormation: Optional[bool]
    cancelReason: Optional[str]
    delayReason: Optional[str]
    serviceID: str
    adhocAlerts: Optional[str]
    rsid: str | None
    origin: Location
    destination: Location
    currentOrigins: Optional[Location]
    currentDestinations: Optional[Location]
    formation: Optional[Formation]


class TrainServices(BaseModel):
    """
    Parent key of service list
    """

    service: List[Service]


class DeparturesResponse(BaseModel):
    """
    Model for GetDepartureBoard
    """

    generatedAt: datetime
    locationName: str
    crs: str
    filterLocationName: str
    filtercrs: str
    filterType: Optional[str]
    nrccMessages: Optional[str]
    platformAvailable: bool
    areServicesAvailable: Optional[bool]
    trainServices: TrainServices
    busServices: Optional[str]
    ferryServices: Optional[str]
