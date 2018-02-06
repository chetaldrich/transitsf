import requests
import json
from geopy.geocoders import Nominatim
from geopy.distance import vincenty


class NextBusAPIWrapper:
    """
        Wrapper of nextbus API for predictions
        Sample Usage:
            address = "99 Grove St, San Francisco, CA 94102"
            print(NextBusAPIWrapper.get_next_bus(address, "J", "Outbound"))
    """

    BASE_URL = "http://webservices.nextbus.com/service/publicJSONFeed"
    AGENCY = "sf-muni"

    @classmethod
    def get_next_bus(cls, location, route, direction):
        """
        Get the time for the next bus on a route going in some direction
        :param location: the user's address (string)
        :param route: the route name (string)
        :param direction: the direction of the bus. We assume Inbound/Outbound (string)
        :return: the number of minutes (integer) until the next bus comes
        """
        # TODO: consider multiple names for routes
        stop_tag = cls._get_stop_id(location, route, direction)
        request_url = cls._compose_url(
            "predictions", route, stop_tag=stop_tag)
        # TODO: error handling
        predictions = json.loads(requests.get(request_url).text)["predictions"]["direction"]

        all_times = []
        # sometimes this is a dict, sometimes it's not...
        predictions = predictions if isinstance(predictions, list) else [predictions]
        for prediction_set in predictions:
            if isinstance(prediction_set["prediction"], dict):
                all_times.append(int(prediction_set["prediction"]["minutes"]))
            else:
                all_times.extend(int(prediction["minutes"]) for prediction in prediction_set["prediction"])
        # TODO: handle different destinations. Some busses turn around before
        # reaching the terminus
        # TODO: return the next n times?
        return min(all_times)

    @classmethod
    def _get_stop_id(cls, location, route, direction):
        """
        Gets the stop ID for the closest stop to the user's location
        :param location: the current address (string)
        :param route: the route name (string)
        :param direction: the direction of the bus. We assume Inbound/Outbound (string)
        :return: The stop tag (string). We technically use the tag, not the ID
        """
        # get latitude and longitude for the location
        # TODO: error handling
        user_location = Nominatim().geocode(location)
        user_ll = (user_location.latitude, user_location.longitude, )

        # get all appropriate stops for the request
        request_url = cls._compose_url("routeConfig", route)
        # TODO: error handling
        correct_route = json.loads(requests.get(request_url).text)['route']

        # get the stops that go in the correct direction
        correct_direction_stops = None
        for direction_stops in correct_route["direction"]:
            if direction_stops["name"] == direction:
                correct_direction_stops = set(stop["tag"] for stop in direction_stops["stop"])
                break

        # get the stop closest to the user's location
        closest_stop = None
        closest_distance = None
        for stop in correct_route["stop"]:
            if stop["tag"] in correct_direction_stops:
                stop_ll = (stop["lat"], stop["lon"], )
                # TODO: is this the right distance measure to use?
                distance = vincenty(user_ll, stop_ll).miles
                if closest_stop is None or distance < closest_distance:
                    closest_stop = stop
                    closest_distance = distance

        return closest_stop["tag"]

    @classmethod
    def _compose_url(cls, command, route, stop_tag=None):
        """
        Compose the URL for the request
        :param command: nextbus command (string)
        :param route: route name (string)
        :param stop_tag: the tag of the stop (string) (optional)
        :return: request URL (string)
        """
        # build params
        params_raw = {
            "a": cls.AGENCY,
            "command": command,
            "r": route,
            "s": stop_tag
        }
        # remove empty params
        params = {k: v for k, v in params_raw.items() if v}

        # build request
        prepared = requests.Request(
            "GET", cls.BASE_URL, params=params).prepare()
        return prepared.url

