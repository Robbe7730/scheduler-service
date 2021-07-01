# scheduler-service

A microservice for scheduling events.

## Model

All objects are `schema:ScheduleAction`s with the following properties:

- `startTime`: (`schema:DateTime`) When the event starts/started.
- `endTime`: (`schema:DateTime`) When the event ends/ended.
- `actionStatus`: (`schema:ActionStatusType`) The status of the event.
- `target`: (`schema:EntryPoint`) What to execute when the event starts or ends.
  Can contain [rfc6570][rfc6570] string expansion for:
    - `id`: The generated uuid for this 
    - `status`: 1 when started and 0 when stopped

## API

`POST /schedule`

Required fields: `startTime`, `endTime`

Responses:

- 201 Created
- 409 Conflict, if there is overlap with another scheduled action

Example:
```
{
    "startTime": "2021-02-25T18:14:22Z",
    "endTime": "2021-03-11T11:04:59Z",
    "target": {
        "httpMethod": "POST",
        "urlTemplate": "http://myservice/schedulecallback?id={id}&status={status}"
    }
}
```

`DELETE /schedule/<id>`

Responses:

- 204 No content, if the event is successfully deleted
- 404 Not found, if no event with that id exists
- 403 Forbidden, if the event has already started

To get the scheduled events, the user can query the database.

## Limitations

- Events cannot be updated
- Events cannot be stopped while in progress

[rfc6570]: https://datatracker.ietf.org/doc/html/rfc6570
