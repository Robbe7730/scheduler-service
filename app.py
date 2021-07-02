"""
web.py: entry point of the service
"""

from enum import Enum, auto

from dateutil import parser
from flask import Flask, request

from helpers import error

app = Flask(__name__)

class ActionStatus(Enum):
    """
    ActionStatus: Python enum for https://schema.org/ActionStatusType
    """
    ACTIVE = auto()
    COMPLETED = auto()
    FAILED = auto()
    POTENTIAL = auto()

class InvalidDataException(Exception):
    """
    InvalidDataException: Exception thrown when the request data is invalid
    """
    def __init__(self, message="Invalid data"):
        self.message = message
        super().__init__(message)

    def as_jsonapi_error(self):
        """
        as_jsonapi_error: Return the exception as a JSON:API error
        """
        return error(self.message)

class Reservation: #pylint: disable=R0903
    """
    A scheduled reservation
    """
    def __init__(
            self,
            start_time,
            end_time,
            target_method=None,
            target_url_template=None
        ):
        self.start_time = start_time
        self.end_time = end_time
        self.target_method = target_method
        self.target_url_template = target_url_template
        self.action_status = ActionStatus.POTENTIAL

    @classmethod
    def from_json_data(cls, json_data):
        """
        from_json_data: Create a Reservation from a json request

        :throws:
            InvalidDataException if the data is an invalid reservation
        """
        if json_data is None or "data" not in json_data:
            return error('No JSON data found')

        data = json_data["data"]

        data_type = data.get('type', 'no type')
        if data_type != 'reservation':
            raise InvalidDataException(
                f'Expected type \'reservation\', but got \'{data_type}\''
            )

        start_time_str = data.get("startTime", "no time given")
        try:
            start_time = parser.parse(start_time_str)
        except ValueError as e:
            raise InvalidDataException(
                f"Invalid startTime ({start_time_str})"
            ) from e

        end_time_str = data.get("endTime", "no time given")
        try:
            end_time = parser.parse(end_time_str)
        except ValueError as e:
            raise InvalidDataException(
                f"Invalid endTime ({end_time_str})"
            ) from e

        if end_time <= start_time:
            raise InvalidDataException("Start time must be before end time")

        if "target" in data:
            target = data["target"]
            method = target.get("httpMethod", "GET")

            if "urlTemplate" not in target:
                raise InvalidDataException("No URL template in target")

            url = target.get("urlTemplate", "no url given")
            return cls(start_time, end_time, method, url)

        return cls(start_time, end_time)

@app.route('/', methods=['POST'])
def schedule():
    """
    schedule: the main route of the service
    """

    try:
        Reservation.from_json_data(request.json)
    except InvalidDataException as e:
        return e.as_jsonapi_error()

    return "OK"
