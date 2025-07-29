# -*- coding: utf-8 -*-

from googleapiclient.errors import HttpError

from dough.google_api.google_api_with_service_accounts import (
    GoogleApiWithServiceAccounts,
)


class GoogleCalendarAPI(GoogleApiWithServiceAccounts):
    SCOPES = ["https://www.googleapis.com/auth/calendar"]

    def __init__(self, impersonate):
        super().__init__(self.SCOPES, impersonate)
        self.service = super().get_service(api="calendar", version="v3")

    def list_events(self, **kwargs):
        """
        https://developers.google.com/calendar/api/v3/reference/events/list
        """
        kwargs["timeMax"] = kwargs["timeMax"].isoformat("T") + "Z"
        kwargs["timeMin"] = kwargs["timeMin"].isoformat("T") + "Z"

        try:
            events_list = (
                self.service.events()  # pylint: disable=no-member
                .list(**kwargs)
                .execute()
            )
        except HttpError:
            events_list = None

        return events_list
