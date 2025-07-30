# NASA Power

An unofficial Python client for the NASA Power API.

Documentation of the API found on https://power.larc.nasa.gov/docs/tutorials/service-data-request/api/

## Installation

```
python -m pip install nasa-power
```

## Usage

Currently only the points API has been implemented. The point method accepts six named parameters (coordinates, parameters, start, end, resolution, and community).

```py
import nasapower

df = nasapower.point(
  coordinates=(52.09, 5.12),
  parameters=['WS50M', 'CLRSKY_SFC_SW_DWN'],
  start=datetime.date(2020, 01, 01),
  end=datetime.date(2020, 12, 31)
)
```

## Licensing

The code in this project is licensed under the [MIT license](https://github.com/RubenVanEldik/nasa-power/blob/main/LICENSE).
