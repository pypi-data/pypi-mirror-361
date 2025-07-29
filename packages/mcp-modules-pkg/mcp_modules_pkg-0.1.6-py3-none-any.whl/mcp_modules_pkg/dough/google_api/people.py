# -*- coding: utf-8 -*-

from dough.google_api.google_api_with_service_accounts import (
    GoogleApiWithServiceAccounts,
)


class GooglePeopleAPI(GoogleApiWithServiceAccounts):
    SCOPES = [
        "https://www.googleapis.com/auth/contacts",
        "https://www.googleapis.com/auth/directory.readonly",
    ]

    def __init__(self, impersonate):
        super().__init__(self.SCOPES, impersonate)
        self.service = super().get_service(api="people", version="v1")

    def list_directory_people(self, read_mask="emailAddresses"):
        """
        https://developers.google.com/people/api/rest/v1/people/listDirectoryPeople
        """
        results = (
            self.service.people()  # pylint: disable=no-member
            .listDirectoryPeople(
                readMask=read_mask,
                sources=[
                    "DIRECTORY_SOURCE_TYPE_DOMAIN_PROFILE",
                    "DIRECTORY_SOURCE_TYPE_DOMAIN_CONTACT",
                ],
            )
            .execute()
        )
        return results
