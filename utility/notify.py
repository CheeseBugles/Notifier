import json
from datetime import datetime, timezone, timedelta


class Notify:
    def __init__(self) -> None:
        self.filename = "data.json"
        self.data = {}
        try:
            self.data = json.load(open(self.filename, "r+"))
        except json.decoder.JSONDecodeError:
            pass

    def subscribe(self, user_id: str, date: str, message: str) -> None:
        timestamp = self.date_to_timestamp(date)
        try:
            self.data[timestamp]
        except KeyError:
            self.data[timestamp] = {user_id: message}
            self.update()
            return
        self.data[timestamp][user_id] = message  # overwrite message OnEdit
        self.update()
        return

    def notify(self, timestamp: str) -> list[tuple[str, str]]:
        return [
            (user_id, self.data[timestamp][user_id]) for user_id in self.data[timestamp]
        ]

    def read_dates(self) -> list[str]:
        return [date for date in self.data]

    def get_dates_of_user(self, user_id) -> list[str]:
        user_id = str(user_id)
        dates = []

        for date in self.read_dates():
            try:
                if self.data[date][user_id]:
                    dates.append(date)
            except KeyError:
                pass
        return [self.timestamp_to_date(date) for date in dates]

    def time_now(self) -> str:
        return str(int((datetime.now(timezone.utc) + timedelta(hours=3)).timestamp()))

    def date_now(self) -> str:
        return self.timestamp_to_date(self.time_now())

    def date_to_timestamp(self, date: str) -> str:
        return str(
            int(
                (
                    datetime.strptime(date, "%Y-%m-%d %H:%M") + timedelta(hours=3)
                ).timestamp()
            )
        )

    def timestamp_to_date(self, timestamp: str) -> str:
        return datetime.utcfromtimestamp(int(timestamp)).strftime("%Y-%m-%d %H:%M")

    def edit_date(
        self, old_timestamp: str, new_timestamp: str, user_id: str, new_message
    ) -> None:
        self.data.pop(old_timestamp)
        self.data[new_timestamp] = {user_id: new_message}
        self.update()

    def get_date_message(self, timestamp: str, user_id: str) -> str:
        return self.data[timestamp][user_id]

    def update(self):
        self.data.update()
        json.dump(self.data, open(self.filename, "w+"), indent=4)
