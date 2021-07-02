"""
test_api: helper script to test the JSON:API compliancy
"""
import datetime

import jsonapi_requests

api = jsonapi_requests.Api.config({
    'API_ROOT': 'http://localhost/',
    'VALIDATE_SSL': False,
    'TIMEOUT': 1,
})

now = datetime.datetime.now()
endpoint = api.endpoint('schedule')
print(endpoint.post(object=jsonapi_requests.JsonApiObject(
    type='reservation',
    attributes={
        'startTime': now.isoformat(),
        'endTime': (now + datetime.timedelta(hours=1)).isoformat()
    },
)))

print(endpoint.post(object=jsonapi_requests.JsonApiObject(
    type='reservation',
    attributes={
        'startTime': now.isoformat(),
        'endTime': (now + datetime.timedelta(hours=1)).isoformat(),
        'target': {
            'httpMethod': 'POST',
            'urlTemplate': 'http://example.com/reservation/{id}?status={status}'
        }
    },
)))
