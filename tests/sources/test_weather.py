"""
Weather Client Tests
"""
from sources import Weather



def test_get_weather_mock(httpx_mock):
    """
    Test Parsing Mock Data
    """
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    httpx_mock.add_response(
        url=f"{base_url}?id=6690565&units=metric&APPID=dummy-token",
        json={
            "coord": {"lon": -0.1237, "lat": 51.5797},
            "weather": [
                {
                    "id": 801,
                    "main": "Clouds",
                    "description": "few clouds",
                    "icon": "02d",
                }
            ],
            "base": "stations",
            "main": {
                "temp": 24.62,
                "feels_like": 24.23,
                "temp_min": 22.55,
                "temp_max": 26.5,
                "pressure": 1011,
                "humidity": 42,
            },
            "visibility": 10000,
            "wind": {"speed": 7.2, "deg": 90},
            "clouds": {"all": 19},
            "dt": 1686939348,
            "sys": {
                "type": 2,
                "id": 2075535,
                "country": "GB",
                "sunrise": 1686886940,
                "sunset": 1686946798,
            },
            "timezone": 3600,
            "id": 6690565,
            "name": "Crouch End",
            "cod": 200,
        },
    )

    client = Weather.OpenWeather("dummy-token")
    weather = client.get_weather(town_id=6690565, units="metric")

    assert isinstance(weather, Weather.models.WeatherData)
    assert weather.name == "Crouch End"
    assert weather.coord.lon == -0.1237
    assert weather.coord.lat == 51.5797
    assert weather.weather[0].main == "Clouds"
    assert weather.main.temp == 24.62
    assert weather.wind.speed == 7.2
    assert weather.clouds.all == 19
    assert weather.sys.country == "GB"
    assert weather.timezone == 3600


def test_get_air_quality_mock(httpx_mock):
    """
    Test Parsing Mock Data
    """
    base_url = "https://api.openweathermap.org/data/2.5/air_pollution"
    httpx_mock.add_response(
        url=f"{base_url}?lat=51.5797&lon=-0.1237&appid=dummy-token",
        json={
            "coord": {"lon": -0.1237, "lat": 51.5797},
            "list": [
                {
                    "main": {"aqi": 2},
                    "components": {
                        "co": 236.23,
                        "no": 0.2,
                        "no2": 13.68,
                        "o3": 56.91,
                        "so2": 1.42,
                        "pm2_5": 8.98,
                        "pm10": 12.89,
                        "nh3": 1.71,
                    },
                    "dt": 1636928400,
                }
            ],
        },
    )

    client = Weather.OpenWeather("dummy-token")
    air_quality = client.get_air_quality(lat=51.5797, lon=-0.1237)

    assert isinstance(air_quality, Weather.models.AirQualityData)
    assert air_quality.coord.lon == -0.1237
    assert air_quality.coord.lat == 51.5797
    assert air_quality.list[0].main.aqi == 2
    assert air_quality.list[0].components.co == 236.23
