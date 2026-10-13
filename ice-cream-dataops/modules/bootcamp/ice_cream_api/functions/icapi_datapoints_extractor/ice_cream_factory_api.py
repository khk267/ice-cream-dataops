from typing import Dict, Union

import json
from requests import Response, Session, adapters


class IceCreamFactoryAPI:
    """Class for Ice Cream Factory API."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.adapter = adapters.HTTPAdapter(max_retries=3)
        self.session = Session()
        self.session.mount("https://", self.adapter)

    def get_response(
        self,
        headers: Dict[str, str],
        url_suffix: str,
        params: Dict[str, Union[str, int, float]] | None = None,
    ) -> Response:
        """
        Get response from API.

        Args:
            headers: Request headers.
            url_suffix: String to add to the base URL.
            params: Query parameters.
        """
        response = self.session.get(
            f"{self.base_url}/{url_suffix}",
            headers=headers,
            timeout=40,
            params=params or {},
        )
        response.raise_for_status()
        return response

    def get_datapoints(
        self,
        timeseries_ext_id: str,
        start: Union[str, int, float],
        end: Union[str, int, float],
    ):
        """
        Get datapoints for a time series external ID.

        This can also return datapoints for an associated time series.
        """
        params = {
            "start": start,
            "end": end,
            "external_id": timeseries_ext_id,
        }

        response = self.get_response(
            headers={},
            url_suffix="datapoints/oee",
            params=params,
        )

        response_dict = json.loads(response.content)

        return [
            {
                "instance_id": ts,
                "datapoints": [
                    {
                        "timestamp": datapoint[0] * 1000,
                        "value": datapoint[1],
                    }
                    for datapoint in datapoints
                ],
            }
            for ts, datapoints in response_dict.items()
            if len(datapoints) > 1
        ]