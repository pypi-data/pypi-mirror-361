from tapi.client import Client
from datetime    import datetime
from typing      import Optional, Union, Literal


class ReportingAPI(Client):
    def __init__(self, domain: str, apiKey: str):
        super().__init__(domain, apiKey)
        self.base_endpoint = "reporting"

    def action_performance(
            self,
            team_id:       Optional[int] = None,
            story_id:      Optional[int] = None,
            action_id:     Optional[int] = None,
            filter_option: Optional[Literal["most_active_actions", "action_with_least_activity", "slowest_actions", "fastest_actions"]] = None,
            per_page:      int           = 10,
            page:          int           = 1,
    ):
        return self._http_request(
            "GET",
            f"{self.base_endpoint}/action_performance",
            params = {key: value for key, value in locals().items() if value is not None and key != "self"}
        )

    def time_saved(
            self,
            start_date: Optional[Union[datetime, str]]          = None,
            end_date:   Optional[Union[datetime, str]]          = None,
            date_unit:  Literal["hour", "day", "week", "month"] = "day",
            fill_gaps:  bool                                    = True,
            team_id:    Optional[int]                           = None,
            story_id:   Optional[int]                           = None,
            per_page:   int                                     = 10,
            page:       int                                     = 1,
    ):
        return self._http_request(
            "GET",
            f"{self.base_endpoint}/time_saved",
            params = {key: value for key, value in locals().items() if value is not None and key != "self"}
        )
