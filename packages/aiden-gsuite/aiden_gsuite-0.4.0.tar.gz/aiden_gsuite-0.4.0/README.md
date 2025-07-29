# aiden-gsuite MCP server

![PyPI - Version](https://img.shields.io/pypi/v/aiden-gsuite)

> This project is based on [mcp-gsuite](https://github.com/MarkusPfundstein/mcp-gsuite)

MCP server to interact with Google products. With [Aiden](https://github.com/AllWiseAI/aiden-chat), Google account authorization is extremely simplified.

## Example prompts

Right now, this MCP server supports Gmail, Google Calendar, Google Drive and Google Maps integration with the following capabilities:

1. Gmail

* Get your Gmail user information
* Query emails with flexible search (e.g., unread, from specific senders, date ranges, with attachments)
* Retrieve complete email content by ID
* Create new draft emails with recipients, subject, body and CC options
* Send draft emails
* Delete draft emails
* Delete emails
* Reply to existing emails (can either send immediately or save as draft)
* Retrieve multiple emails at once by their IDs.
* Save multiple attachments from emails to your local system.

2. Google Calendar

* Manage multiple calendars
* Get calendar events within specified time ranges
* Create calendar events with:
  + Title, start/end times
  + Optional location and description
  + Optional attendees
  + Custom timezone support
  + Notification preferences
* Modify calendar events
* Delete calendar events

3. Google Drive

* Search drive files
* List drive files
* Read drive file content
* Create drive files or folders
* Trash/Restore files or folders
* List trash files
* Empty the trash

4. Google Maps

* Convert an address into geographic coordinates
* Convert a geographic coordinates into an address
* Search for places
* Get details about a place
* Get distance and duration between two places
* Get elevation at a given location
* Get directions between two places

Example prompts you can try:

* Retrieve my latest unread messages
* Search my emails from the Scrum Master
* Retrieve all emails from accounting
* Take the email about ABC and summarize it
* Write a nice response to Alice's last email and upload a draft.
* Reply to Bob's email with a Thank you note. Store it as draft

* What do I have on my agenda tomorrow?
* Check my private account's Family agenda for next week
* I need to plan an event with Tim for 2hrs next week. Suggest some time slots.

## Quickstart

### Install

No credential file needed with [Aiden](https://github.com/AllWiseAI/aiden-chat).

```json
"aiden-gsuite": {
  "command": "uvx",
  "args": [
    "aiden-gsuite@0.4.0"
  ],
  "env": {
    "GOOGLE_MAPS_API_KEY": ""
  },
  "aiden_credential": {
    "type": "oauth",
    "service": "google",
    "scopes": [
      "openid",
      "https://www.googleapis.com/auth/gmail.compose",
      "https://www.googleapis.com/auth/gmail.modify",
      "https://www.googleapis.com/auth/gmail.send",
      "https://www.googleapis.com/auth/gmail.readonly",
      "https://www.googleapis.com/auth/calendar.readonly",
      "https://www.googleapis.com/auth/calendar.events",
      "https://www.googleapis.com/auth/drive.file"
    ]
  },
  "transport": "stdio"
}
```

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

You can launch the MCP Inspector via [ `npm` ](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/aiden-gsuite run aiden-gsuite
```

Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.
