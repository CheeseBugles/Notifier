from os import environ
from discord import Client, Intents, Message
import asyncio

from ui.components import ViewUI, NotifierUsage, NotifyMessage
from utility.notify import Notify


class NotifierBot(Client):
    def __init__(self, channel_id: int, notifire: Notify):
        super().__init__(intents=Intents.all())
        self.channel_id = channel_id
        self.notifier = notifire

    async def on_ready(self):
        while True:
            (time_now, dates) = (self.notifier.time_now(), self.notifier.read_dates())
            if time_now in dates:
                for (user_id, message) in self.notifier.notify(time_now):
                    await self.notify(user_id, time_now, message)
            # print(dates, time_now)
            await asyncio.sleep(1)

    async def notify(self, user_id: str, date: str, message: str):
        channel = self.get_channel(self.channel_id)
        date = self.notifier.timestamp_to_date(date)

        await channel.send(
            self.get_user(int(user_id)).mention,
            embed=NotifyMessage("Reminder!!", user_id, date, message),
        )

    async def on_message(self, message: Message):
        if message.content.startswith("!notifier"):
            view = ViewUI(message.author.id, self.notifier)
            embed = NotifierUsage(message.author.id)

            await self.get_channel(self.channel_id).send(
                view=view, embed=embed, delete_after=60 * 5
            )

            await message.delete()


if __name__ == "__main__":
    (token, channel_id) = (environ["TOKEN"], int(environ["CHANNEL_ID"]))
    NotifierBot(channel_id, Notify()).run(token)
