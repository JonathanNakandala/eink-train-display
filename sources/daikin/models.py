"""`
Daikin API models
"""
import urllib.parse
from pydantic import BaseModel, Field, validator


def decode_url_string(string: str) -> str:
    """
    The name string is returned as a url escaped string
    """
    return urllib.parse.unquote(string)


class BasicInfo(BaseModel):
    """
    GET /common/basic_info
    """

    ret: str = Field(..., description="Return Status")
    type: str = Field(..., description="Type")
    reg: str = Field(..., description="Region")
    dst: str = Field(..., description="DST")
    ver: str = Field(..., description="Version")
    rev: str = Field(..., description="Revision")
    pow: str = Field(..., description="Power")
    err: str = Field(..., description="Error")
    location: str = Field(..., description="Location")
    name: str = Field(..., description="Name")
    icon: str = Field(..., description="Icon")
    method: str = Field(..., description="Method")
    port: str = Field(..., description="Port")
    id: str = Field(..., description="ID")
    pw: str = Field(..., description="Password")
    lpw_flag: str = Field(..., description="Password Flag")
    adp_kind: str = Field(..., description="Adaptor Kind")
    pv: str = Field(..., description="PV")
    cpv: str = Field(..., description="CPV")
    cpv_minor: str = Field(..., description="CPV Minor")
    led: str = Field(..., description="LED")
    en_setzone: str = Field(..., description="Setzone Enabled")
    mac: str = Field(..., description="MAC Address")
    adp_mode: str = Field(..., description="Adaptor Mode")
    en_hol: str = Field(..., description="Holiday Enabled")
    ssid1: str = Field(..., description="SSID 1")
    radio1: str = Field(..., description="Radio 1")
    ssid: str = Field(..., description="SSID")
    grp_name: str = Field(..., description="Group Name")
    en_grp: str = Field(..., description="Group Enabled")

    _decode_url_string: classmethod = validator("name", pre=True, allow_reuse=True)(
        decode_url_string
    )


class SensorInfo(BaseModel):
    """
    GET /aircon/get_sensor_info
    """

    ret: str = Field(..., description="Return Status")
    htemp: float = Field(..., description="Inside Temperature")
    hhum: int = Field(..., description="Inside Humidity")
    otemp: float = Field(..., description="Outside Temperature")
    err: int = Field(..., description="Error")
    cmpfreq: int = Field(..., description="compressor frequency")


class DaikinInfoTemp(BaseModel):
    """
    Temperatures
    """

    indoor: float
    outdoor: float


class DaikinInfo(BaseModel):
    """
    Collected Information
    """

    name: str = Field(..., description="Unit Name")
    temperature: DaikinInfoTemp
    humidity: int


def parse_string_to_data(string_data: str):
    """
    Parsing the string response
    The room names uses url escaping and needs to be decoded
    """
    data_dict = dict(kv.split("=") for kv in string_data.split(","))
    return data_dict
