from tapi.client      import Client
from tapi.utils.types import CaseNoteColor
from typing           import Optional, Union


class CaseNotesAPI(Client):
    def __init__(self, domain: str, apiKey: str):
        super().__init__(domain, apiKey)
        self.base_endpoint = "cases"

    def create(
            self,
            case_id:  int,
            title:    str,
            content:  Optional[str]                       = None,
            color:    Optional[Union[CaseNoteColor, str]] = None,
            position: Optional[int]                       = None
    ):
        return self._http_request(
            "POST",
            f"{self.base_endpoint}/{case_id}/notes",
            "v2",
            json = {key: value for key, value in locals().items() if
                    value is not None and key not in ("self", "case_id")}
        )

    def get(
            self,
            case_id: int,
            note_id: int
    ):
        return self._http_request(
            "GET",
            f"{self.base_endpoint}/{case_id}/notes/{note_id}",
            "v2"
        )

    def update(
            self,
            case_id:  int,
            note_id:  int,
            title:    Optional[str]                       = None,
            content:  Optional[str]                       = None,
            color:    Optional[Union[CaseNoteColor, str]] = None,
            position: Optional[int]                       = None
    ):
        return self._http_request(
            "PUT",
            f"{self.base_endpoint}/{case_id}/notes/{note_id}",
            "v2",
            json = {key: value for key, value in locals().items() if
                    value is not None and key not in ("self", "case_id", "note_id")}
        )

    def list(
            self,
            case_id:  int,
            per_page: int = 10,
            page:     int = 1
    ):
        return self._http_request(
            "GET",
            f"{self.base_endpoint}/{case_id}/notes",
            "v2",
            params = {"per_page": per_page, "page": page}
        )

    def delete(
            self,
            case_id: int,
            note_id: int
    ):
        return self._http_request(
            "DELETE",
            f"{self.base_endpoint}/{case_id}/notes/{note_id}",
            "v2"
        )

