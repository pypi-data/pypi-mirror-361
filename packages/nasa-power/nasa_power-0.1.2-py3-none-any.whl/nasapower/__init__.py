import datetime
import numpy as np
import pandas as pd

RESOLUTIONS = ["hourly", "daily", "monthly", "climatology"]
COMMUNITIES = ["RE", "SB", "AG"]


def point(
    *, coordinates, parameters, start, end, resolution="hourly", community="RE",
):
    # Validate and parse the coordinates
    if pd.api.types.is_list_like(coordinates):
        if len(coordinates) != 2:
            raise ValueError("Coordinate list should have 2 values")
        latitude, longitude = coordinates
    if isinstance(coordinates, dict):
        if "lat" not in coordinates:
            raise ValueError("Coordinates does not contain a 'lat' key")
        if "lon" not in coordinates.index:
            raise ValueError("Coordinates does not contain a 'lon' key")
        latitude = coordinates["lat"]
        longitude = coordinates["lon"]
    if isinstance(coordinates, pd.core.series.Series):
        if "lat" not in coordinates.index:
            raise ValueError("Coordinates does not have 'lat' in index")
        if "lat" not in coordinates.index:
            raise ValueError("Coordinates does not have 'lat' in index")
        latitude = coordinates["lat"]
        longitude = coordinates["lon"]
    if not isinstance(latitude, int) and not isinstance(latitude, float):
        raise TypeError("Latitude should be an integer or float")
    if not isinstance(longitude, int) and not isinstance(longitude, float):
        raise TypeError("Longitude should be an integer or float")
    if not isinstance(latitude, (int, float, str, np.number)):
        raise TypeError("Latitude should be a number")
    if not isinstance(longitude, (int, float, str, np.number)):
        raise TypeError("Longitude should be a number")
    if latitude < -90 or latitude > 90:
        raise ValueError("Latitude should be between -90 and 90")
    if longitude < 0 or longitude > 360:
        raise ValueError("Longitude should be between 0 and 360")

    # Validate the community
    if community not in COMMUNITIES:
        raise ValueError(f"Community should be one of {COMMUNITIES}")

    # Validate the parameters
    if not isinstance(parameters, list):
        raise TypeError("Parameters should be a list")

    # Validate the resolution
    if resolution not in RESOLUTIONS:
        raise TypeError(f"Resolution should be one of {RESOLUTIONS}")

    # Validate the start and end date
    if resolution in ["hourly", "daily"]:
        if not isinstance(start, (datetime.datetime, datetime.date)):
            raise TypeError("Start should be a datetime or date")
        if not isinstance(end, (datetime.datetime, datetime.date)):
            raise TypeError("End should be a datetime or date")
        if start < datetime.date(1982, 1, 1) or start > datetime.date.today():
            raise ValueError("Start should be between 1982 and today")
        if end < datetime.date(1982, 1, 1) or end > datetime.date.today():
            raise ValueError("End should be between 1982 and today")
        if start > end:
            raise ValueError("Start must be before end")
    else:
        if not isinstance(start, int):
            raise TypeError("Start should be an integer")
        if not isinstance(start, int):
            raise TypeError("End should be an integer")
        if start < 1982 or start > 2020:
            raise ValueError("Start should be between 1982 and 2020")
        if end < 1982 or end > 2020:
            raise ValueError("End should be between 1982 and 2020")
        if start > end:
            raise ValueError("Start must be before end")

    # Retrieve the data
    try:
        url = f"https://power.larc.nasa.gov/api/temporal/{resolution}/point"
        params = {
            "parameters": ",".join(parameters),
            "longitude": longitude,
            "latitude": latitude,
            "start": start.strftime("%Y%m%d"),
            "end": end.strftime("%Y%m%d"),
            "community": community,
            "format": "JSON",
        }
        response = requests.get(url=url, params=params, verify=True, timeout=60)
        content = json.loads(response.content.decode("utf-8"))
    except:
        raise Exception(f"Could not fetch the data")

    # Check if there are any error messages
    if len(content.get("messages", [])) > 0:
        raise Exception(content["messages"][0])

    # Check if there are any other error messages
    details = content.get("detail", [])
    if len(details):
        raise Exception(details[0].get("msg"))

    # Transform the data into a DataFrame
    data = pd.DataFrame(content["properties"]["parameter"])
    data.index = pd.to_datetime(data.index, format="%Y%m%d%H")

    # Return the data
    return data
