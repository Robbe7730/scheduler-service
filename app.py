"""
web.py: entry point of the service
"""

from __future__ import annotations

from enum import Enum, auto

from dateutil import parser
from flask import Flask, jsonify, request, Response

from helpers import error, generate_uuid

app = Flask(__name__)

class ActionStatus(Enum):
    """
    ActionStatus: Python enum for https://schema.org/ActionStatusType
    """
    ACTIVE = auto()
    COMPLETED = auto()
    FAILED = auto()
    POTENTIAL = auto()

    def __str__(self):
        if self == ActionStatus.ACTIVE:
            return 'active'
        if self == ActionStatus.COMPLETED:
            return 'completed'
        if self == ActionStatus.FAILED:
            return 'failed'
        if self == ActionStatus.POTENTIAL:
            return 'potential'
        return 'invalid status'

    def to_json(self) -> str:
        """
        to_json: Make ActionStatus JSON serializable

        :returns: The JSON (string) representation of the ActionStatus
        """
        return str(self)

class InvalidDataException(Exception):
    """
    InvalidDataException: Exception thrown when the request data is invalid
    """
    def __init__(self, message="Invalid data"):
        self.message = message
        super().__init__(message)

    def as_jsonapi_error(self) -> Response:
        """
        as_jsonapi_error: Return the exception as a JSON:API error

        :returns: The stringified JSON:API error
        """
        return error(self.message)

class Reservation:
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
        self.id = generate_uuid()
        self.start_time = start_time
        self.end_time = end_time
        self.target_method = target_method
        self.target_url_template = target_url_template
        self.action_status = ActionStatus.POTENTIAL

    @classmethod
    def from_json_data(cls, json_data) -> Reservation:
        """
        from_json_data: Create a Reservation from a json request

        :returns: The created reservation

        :raises InvalidDataException: if the data is an invalid reservation
        """
        if json_data is None or "data" not in json_data:
            raise InvalidDataException('No JSON data found')

        data = json_data["data"]

        data_type = data.get('type', 'no type')
        if data_type != 'reservation':
            raise InvalidDataException(
                f'Expected type \'reservation\', but got \'{data_type}\''
            )

        attributes = data.get('attributes', {})

        start_time_str = attributes.get("startTime", "no time given")
        try:
            start_time = parser.parse(start_time_str)
        except ValueError as e:
            raise InvalidDataException(
                f"Invalid startTime ({start_time_str})"
            ) from e

        end_time_str = attributes.get("endTime", "no time given")
        try:
            end_time = parser.parse(end_time_str)
        except ValueError as e:
            raise InvalidDataException(
                f"Invalid endTime ({end_time_str})"
            ) from e

        if end_time <= start_time:
            raise InvalidDataException("Start time must be before end time")

        if "target" in attributes:
            target = attributes["target"]
            method = target.get("httpMethod", "GET")

            if "urlTemplate" not in target:
                raise InvalidDataException("No URL template in target")

            url = target.get("urlTemplate", "no url given")
            return cls(start_time, end_time, method, url)

        return cls(start_time, end_time)

    def as_jsonapi_response(self) -> dict:
        """
        as_jsonapi_response: Returns the reservation as a JSON:API response

        :returns: A JSON:API compliant response dict
        """
        return {
            'type': 'reservation',
            'id': str(self.id),
            'attributes': {
                'startTime': self.start_time.isoformat(),
                'endTime': self.end_time.isoformat(),
                'target': {
                    'httpMethod': self.target_method,
                    'urlTemplate': self.target_url_template
                },
                'actionStatus': self.action_status.to_json()
            }
        }


@app.route('/', methods=['POST'])
def schedule() -> Response:
    """
    schedule: the main route of the service

    :returns: A response to this request
    """
    try:
        reservation = Reservation.from_json_data(request.json)
    except InvalidDataException as e:
        return e.as_jsonapi_error()

    return jsonify(reservation.as_jsonapi_response(), 201)
