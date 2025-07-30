from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Set

import requests
from cachetools import TTLCache, cached

from vito.sas.air.api_client import RESTclient
from vito.sas.air.sos_client import Observation, Pollutant, Station, POLLUTANT_REVERSE_MAP
from vito.sas.air import logger

# Cache settings
CACHE_TTL = 24 * 60 * 60  # 24 hours in seconds

_station_cache = TTLCache(maxsize=1, ttl=CACHE_TTL)
_pollutants_cache = TTLCache(maxsize=1, ttl=CACHE_TTL)

# https://52north.github.io/sensorweb-server-helgoland/version_2.x/api.html
# https://52north.github.io/sensorweb-server-helgoland/version_1.x/api.html

class SOSClientV1(RESTclient):
    """
    Client for the Sensor Observation Service (SOS) V1 API

    This client provides access to air quality data from stations
    across Europe through the SOS V1 API, compatible with the IRCEL-CELINE service.
    """

    def __init__(self, base_url: Optional[str] = None, session: Optional[requests.Session] = None):
        """
        Initialize the SOS V1 client.

        Args:
            base_url: The base URL of the SOS V1 API. Defaults to "https://geo.irceline.be/sos/api/v1"
            session: The requests session to use. If None, a new session will be created.
        """
        super().__init__(base_url or "https://geo.irceline.be/sos/api/v1", session)
        logger.info(f"Initialized SOSClientV1 with base URL: {self.base_url}")

    def get_observations(self, station_name: str, pollutant: str, start_time: datetime, end_time: datetime) -> List[Observation]:
        """
        Get observations for a specific station and pollutant within a time range.

        Args:
            station_name: The local code of the station (e.g., "40AL02")
            pollutant: The name of the pollutant
            start_time: The start time of the observations
            end_time: The end time of the observations

        Returns:
            A list of observations

        Raises:
            ValueError: If the station or pollutant is not found
        """
        # Ensure times are in UTC
        time_zone = start_time.tzinfo
        if time_zone is None:
            start_time = start_time.replace(tzinfo=timezone.utc)
            end_time = end_time.replace(tzinfo=timezone.utc)

        logger.info(f"Getting observations for station {station_name}, pollutant {pollutant} from {start_time} to {end_time}")

        # Get stations and check if the requested station exists
        stations = self.get_stations_cached()
        if station_name not in stations:
            available_stations = ", ".join(stations.keys())
            error_msg = f"Station {station_name} not found. Available stations: {available_stations}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Get pollutants and check if the requested pollutant exists
        pollutants = self.get_pollutants_cached()
        if pollutant not in pollutants:
            available_pollutants = ", ".join(pollutants.keys())
            error_msg = f"Pollutant {pollutant} not found. Available pollutants: {available_pollutants}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        station: Station = stations[station_name]
        pollutant_obj: Pollutant = pollutants[pollutant]

        # Check if the station has the requested pollutant
        if not station.has_pollutant(pollutant):
            available_pollutants = ", ".join([p.name for p in station.pollutants])
            logger.warning(f"Station {station_name} does not measure pollutant {pollutant}. Available pollutants: {available_pollutants}")

        # Get station details to find the correct timeseries ID
        station_details = self._get_station_details(station_name)
        timeseries_id = self._find_timeseries_id(station_details, pollutant_obj.description)

        if not timeseries_id:
            error_msg = f"No timeseries found for pollutant {pollutant} at station {station_name}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Get data from the timeseries endpoint
        url = f"{self.base_url}/timeseries/{timeseries_id}/getData"
        params = {"generalize": "false", "expanded": "true", "format": "tvp", "force_latest_values": "true"}
        end_time_api = end_time + timedelta(hours=12)
        start_time_api = start_time - timedelta(hours=12)
        str_date_from = start_time_api.strftime("%Y-%m-%dT%H:%M:%S")
        str_date_to = end_time_api.strftime("%Y-%m-%dT%H:%M:%S")
        params["timespan"] = str_date_from + "/" + str_date_to
        # print("params: ", params)
        try:
            response = self._exec_get(url, params)

            data = response.json()
            observations = self._parse_v1_observations(data, station_name, pollutant, timeseries_id)
            logger.info(f"Retrieved {len(observations)} observations")
            # filter out observations < start_time or > end_time
            observations = [obs for obs in observations if start_time <= obs.result_time <= end_time]

            return observations
        except Exception as e:
            logger.error(f"Error retrieving observations: {e}")
            raise

    def _get_station_details(self, station_id: str) -> Dict[str, Any]:
        """Get detailed information about a station including timeseries"""
        # First get the station ID from the stations list
        stations_data = self._get_stations_raw()
        station_internal_id = None

        for station in stations_data:
            if station.get("properties", {}).get("label", "").startswith(station_id):
                station_internal_id = station.get("properties", {}).get("id")
                break

        if not station_internal_id:
            raise ValueError(f"Station {station_id} not found in stations list")

        # Get station details with timeseries information
        url = f"{self.base_url}/stations/{station_internal_id}"
        response = self._exec_get(url)
        return response.json()

    def _find_timeseries_id(self, station_details: Dict[str, Any], pollutant_description: str) -> Optional[str]:
        """Find the timeseries ID for a given pollutant at a station"""
        timeseries = station_details.get("properties", {}).get("timeseries", {})

        for ts_id, ts_info in timeseries.items():
            phenomenon = ts_info.get("phenomenon", {})
            if phenomenon.get("label") == pollutant_description:
                return ts_id

        return None

    def _parse_v1_observations(self, data: Dict[str, Any], station_eoi: str, pollutant_name: str, timeseries_id: str) -> List[Observation]:
        """Parse observation data from V1 API response"""
        observations: List[Observation] = []

        values = data.get(timeseries_id, {}).get("values", [])

        for value_entry in values:
            timestamp_ms = value_entry.get("timestamp")
            value = value_entry.get("value")

            if timestamp_ms is None:
                continue

            # Convert milliseconds to datetime
            try:
                result_time = datetime.fromtimestamp(timestamp_ms / 1000.0, tz=timezone.utc)
            except (ValueError, OSError) as e:
                logger.warning(f"Invalid timestamp {timestamp_ms}: {e}")
                continue

            # Handle null or invalid values
            if value is None or (isinstance(value, (int, float)) and value <= -999):
                value = None

            observation = Observation(
                result_time=result_time,
                value=value,
                unit="µg/m³",  # Default unit, could be enhanced to get from metadata
                meta_data={"timestamp_ms": timestamp_ms},
                station_eoi_code=station_eoi,
                pollutant_name=pollutant_name,
            )
            observations.append(observation)

        # Sort by result_time
        observations.sort(key=lambda x: x.result_time)
        return observations

    def _get_stations_raw(self) -> List[Dict[str, Any]]:
        """Get raw stations data from V1 API"""
        url = f"{self.base_url}/stations"
        response = self._exec_get(url)
        return response.json()

    def _get_categories_raw(self) -> List[Dict[str, Any]]:
        """Get raw categories data from V1 API"""
        url = f"{self.base_url}/categories"
        response = self._exec_get(url)
        return response.json()

    def get_pollutants(self) -> Set[Pollutant]:
        """
        Get all available pollutants from the V1 API.

        Returns:
            A set of pollutants
        """
        logger.info("Getting all available pollutants from V1 API")

        try:
            categories = self._get_categories_raw()
            pollutants: Set[Pollutant] = set()

            for category in categories:
                label = category.get("label")

                if label and label in POLLUTANT_REVERSE_MAP:
                    pollutant_enum = POLLUTANT_REVERSE_MAP[label]
                    pollutant = Pollutant(name=pollutant_enum.value, description=label)
                    pollutants.add(pollutant)

            logger.info(f"Found {len(pollutants)} pollutants")
            return pollutants
        except Exception as e:
            logger.error(f"Error getting pollutants: {e}")
            raise

    def get_stations(self) -> List[Station]:
        """
        Get all available stations from the V1 API.

        Returns:
            A list of stations
        """
        logger.info("Getting all available stations from V1 API")

        try:
            stations_data = self._get_stations_raw()
            stations: Dict[str, Station] = {}

            for station_data in stations_data:
                try:
                    properties = station_data.get("properties", {})
                    geometry = station_data.get("geometry", {})

                    # Parse station label to get local code and description
                    label = properties.get("label", "")
                    if " - " not in label:
                        continue

                    local_code = label.split(" - ")[0]
                    description = " - ".join(label.split(" - ")[1:])

                    # Get coordinates
                    coordinates = geometry.get("coordinates", [0, 0])
                    longitude = coordinates[0] if len(coordinates) > 0 else 0
                    latitude = coordinates[1] if len(coordinates) > 1 else 0

                    # Get detailed station info to get pollutants
                    station_id = properties.get("id")
                    if station_id:
                        try:
                            station_details = self._get_station_details_by_id(station_id)
                            pollutants = self._extract_pollutants_from_station(station_details)
                        except Exception as e:
                            logger.warning(f"Could not get pollutants for station {local_code}: {e}")
                            pollutants = []
                    else:
                        pollutants = []

                    if local_code not in stations:
                        stations[local_code] = Station(
                            local_code=local_code, description=description, longitude=longitude, latitude=latitude, pollutants=pollutants
                        )

                except Exception as e:
                    logger.warning(f"Error parsing station data: {e}")
                    continue

            stations_list = list(stations.values())
            stations_list.sort(key=lambda x: x.local_code)

            logger.info(f"Found {len(stations_list)} stations")
            return stations_list

        except Exception as e:
            logger.error(f"Error getting stations: {e}")
            raise

    def _get_station_details_by_id(self, station_id: str) -> Dict[str, Any]:
        """Get station details by internal ID"""
        url = f"{self.base_url}/stations/{station_id}"
        response = self._exec_get(url)
        return response.json()

    def _extract_pollutants_from_station(self, station_details: Dict[str, Any]) -> List[Pollutant]:
        """Extract pollutants from station details"""
        pollutants = []
        timeseries = station_details.get("properties", {}).get("timeseries", {})

        for ts_id, ts_info in timeseries.items():
            phenomenon = ts_info.get("phenomenon", {})
            label = phenomenon.get("label")

            if label and label in POLLUTANT_REVERSE_MAP:
                pollutant_enum = POLLUTANT_REVERSE_MAP[label]
                pollutant = Pollutant(name=pollutant_enum.value, description=label)
                if pollutant not in pollutants:
                    pollutants.append(pollutant)

        return pollutants

    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get service capabilities.

        Returns:
            A dictionary with service capabilities
        """
        logger.info("Getting service capabilities for V1 API")
        # V1 API doesn't have a capabilities endpoint, so we return basic info
        return {
            "service": "SOS",
            "version": "1.0.0",
            "base_url": self.base_url,
            "endpoints": {"stations": f"{self.base_url}/stations", "categories": f"{self.base_url}/categories", "timeseries": f"{self.base_url}/timeseries"},
        }

    @cached(_pollutants_cache)
    def get_pollutants_cached(self) -> Dict[str, Pollutant]:
        """
        Get all available pollutants (cached for 24 hours).

        Returns:
            A dictionary of pollutants indexed by name
        """
        set_pollutants = self.get_pollutants()
        pollutants = {pollutant.name: pollutant for pollutant in set_pollutants}
        return pollutants

    @cached(_station_cache)
    def get_stations_cached(self) -> Dict[str, Station]:
        """
        Get all available stations (cached for 24 hours).

        Returns:
            A dictionary of stations indexed by local code
        """
        list_stations = self.get_stations()
        stations = {station.local_code: station for station in list_stations}
        return stations

    def find_stations_with_pollutant(self, pollutant_name: str) -> List[Station]:
        """
        Find all stations that measure a specific pollutant.

        Args:
            pollutant_name: The name of the pollutant

        Returns:
            A list of stations that measure the pollutant
        """
        stations = self.get_stations_cached()
        return [station for station in stations.values() if station.has_pollutant(pollutant_name)]

    def _base_params(self) -> Dict[str, str]:
        """Get base parameters for API requests"""
        return {}

    def _base_headers(self) -> Dict[str, str]:
        """Get base headers for API requests"""
        return {"Accept": "application/json", "Content-Type": "application/json"}
