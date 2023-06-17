"""
National Rail SOAP API
"""
from pydantic import ValidationError
import structlog

from zeep import Client, xsd
from zeep.exceptions import Fault
from zeep.helpers import serialize_object
from zeep.plugins import HistoryPlugin

from .models import DeparturesResponse

log = structlog.get_logger()


class NationalRail:
    """
    Class to fetch stuff from National Rail's API
    """

    WSDL = "http://lite.realtime.nationalrail.co.uk/OpenLDBWS/wsdl.aspx?ver=2017-10-01"
    header = xsd.Element(
        "{http://thalesgroup.com/RTTI/2013-11-28/Token/types}AccessToken",
        xsd.ComplexType(
            [
                xsd.Element(
                    "{http://thalesgroup.com/RTTI/2013-11-28/Token/types}TokenValue",
                    xsd.String(),
                ),
            ]
        ),
    )

    def __init__(self, token):
        self.header_value = self.header(TokenValue=token)
        self.client = Client(wsdl=self.WSDL, plugins=[HistoryPlugin()])

    def get_departures(self, num_rows, at_station, to_station):
        """
        Gets Departures from a station based on From and to

        Args:
            num_rows: Number of Results
            at_station: 3 Letter Station CRS Station Code
            to_station: 3 Letter Station CRS Station Code

        Returns:
            DeparturesResponse
        """

        try:
            log.info(
                "Getting National Rail Departures",
                rows=num_rows,
                at_station=at_station,
                to_station=to_station,
            )
            response = self.client.service.GetDepartureBoard(
                numRows=num_rows,
                crs=at_station,
                filterCrs=to_station,
                _soapheaders=[self.header_value],
            )
            try:
                return DeparturesResponse(**serialize_object(response))
            except ValidationError as model_error:
                log.error("Failed Valdation", response=response)
                raise model_error
        except Fault as error:
            log.error(
                "Error getting departure information from National Rail",
                service="departureBoard",
                exc_info=True,
            )
            raise error

    def check_response_errors(self, departures):
        """
        Check response errors
        """
