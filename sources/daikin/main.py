"""
Example usage of daikinapi module

use e.g. with "python example.py 192.168.1.3"
"""


import httpx
from sources.daikin.models import (
    BasicInfo,
    DaikinInfoTemp,
    SensorInfo,
    DaikinInfo,
    parse_string_to_data,
)


class DaikinClient:
    """
    A simple HTTP client for sending GET and POST requests.

    Attributes:
        base_url (str): The base URL for the API.
        headers (dict): Optional headers to include in the request.
        client (httpx.Client): The HTTP client.

    """

    def __init__(self, base_url: str, headers: dict = None):
        """
        The constructor for HTTPClient class.

        Args:
            base_url (str): The base URL for the API.
            headers (dict): Optional headers to include in the request.

        """
        self.base_url = f"http://{base_url}"
        self.headers = headers or {}
        self.client = httpx.Client(base_url=self.base_url, headers=self.headers)

    def get(self, endpoint: str, params: dict = None) -> str:
        """
        Sends a GET request to the specified endpoint.

        Args:
            endpoint (str): The endpoint to send the request to.
            params (dict): Optional query parameters for the request.

        Returns:
            dict: The JSON response from the server.

        """
        response = self.client.get(endpoint, params=params)
        response.raise_for_status()
        parsed_data = parse_string_to_data(response.text)
        return parsed_data

    def post(self, endpoint: str, data: dict = None) -> dict:
        """
        Sends a POST request to the specified endpoint.

        Args:
            endpoint (str): The endpoint to send the request to.
            data (dict): The data to include in the body of the request.

        Returns:
            dict: The JSON response from the server.

        """
        response = self.client.post(endpoint, json=data)
        response.raise_for_status()
        return response.text

    def get_basic_info(self) -> BasicInfo:
        """
        Basic Info about Daikin

        Returns:
            BasicInfo: The parsed response
        Raises:
            (TypeError, ValueError)

        """
        response = self.get("/common/basic_info")
        return BasicInfo.parse_obj(response)

    def get_sensor_info(self) -> SensorInfo:
        """
        GET request to the /aircon/get_sensor_info

        Returns:
            SensorInfo: The parsed response

        """
        response = self.get("/aircon/get_sensor_info")
        return SensorInfo.parse_obj(response)

    def get_daikin_info(self) -> DaikinInfo:
        """
        Get Parsed Info
        """
        basic = self.get_basic_info()
        sensor = self.get_sensor_info()
        return DaikinInfo(
            name=basic.name,
            temperature=DaikinInfoTemp(indoor=sensor.htemp, outdoor=sensor.otemp),
            humidity=sensor.hhum,
        )

    def close(self):
        """
        Closes the HTTP client.

        """
        self.client.close()
