from discord import SelectOption, Interaction, TextStyle, ButtonStyle, Embed, Colour
from discord.ui import View, Select, TextInput, Button, Modal


class NotifyMessage(Embed):

    def __init__(self, title: str, user_id: str, date: str, message: str, success_icon: bool = False):
        super().__init__()
        url = "https://cdn-icons-png.flaticon.com/512/190/190411.png" if success_icon else "https://cdn-icons-png.flaticon.com/512/595/595067.png"
        self.set_thumbnail(url=url)
        self.color   = Colour.random()
        self.title   = title
        
        (date, time) = date.split(" ")

        self.description  = "** Date    : `%s` %s    "   % (date, "**\n")
        self.description += "** Time    : `%s` %s    "   % (time, "**\n\n")
        self.description += "** Message :  %s `%s` %s"   % ("\n", message, "**\n") 

class NotifierUsage(Embed):

    def __init__(self, user_id: int):
        super().__init__()
        self.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/1157/1157000.png")
        self.title        =  "Notifier Bot"
        self.description  =  "- Add new date by clicking on `Add new` button.            \n"
        self.description +=  "- Edit date or message by select the date.                 \n"
        self.description +=  "- This form will be deleted automatically after 5 minutes. \n"
        self.description +=  "- Form owner: <@%s>                                          " % user_id

class NewDateForm(Modal):
    
    def __init__(self, title: str, notifier) -> None:
        super().__init__(title=title)
        self.notifier = notifier

        (self.date, self.message) = (
            TextInput(
                label="Date:",
                placeholder="Example: 2023-12-31 13:37",
                max_length=16,
                style=TextStyle.short,
            ),
            TextInput(
                label="Message:",
                placeholder="Enter your message here",
                max_length=1337,
                style=TextStyle.paragraph,
            ),
        )
        self.date.default = notifier.date_now()
        self.add_items([self.date, self.message])

    def add_items(self, items: list):
        [self.add_item(item) for item in items]

    async def on_submit(self, interaction: Interaction):
        self.notifier.subscribe(
            str(interaction.user.id),
            self.date.value.strip(),
            self.message.value.strip(),
        )
        await interaction.response.send_message(
            interaction.user.mention,
            embed=NotifyMessage("Added", interaction.user.id, self.date.value.strip(), self.message, success_icon=True), delete_after=4
        )
        await interaction.message.delete(delay=5.5)

class EditDateForm(Modal):
    
    def __init__(self, title: str, notifier, selected_value: str, user_id: str) -> None:
        super().__init__(title=title)
        self.notifier = notifier
        timestamp = notifier.date_to_timestamp(selected_value)
        self.selected_value = selected_value

        (self.date, self.message) = (
            TextInput(label="Date:", max_length=16, style=TextStyle.short),
            TextInput(
                label="Message:",
                placeholder="Enter your message here",
                max_length=1337,
                style=TextStyle.paragraph,
            ),
        )

        self.date.default = selected_value
        self.message.default = notifier.get_date_message(timestamp, str(user_id))

        self.add_items([self.date, self.message])

    def add_items(self, items: list):
        [self.add_item(item) for item in items]

    async def on_submit(self, interaction: Interaction):
        (new_timestamp, old_timestamp) = (
            self.notifier.date_to_timestamp(self.date.value.strip()),
            self.notifier.date_to_timestamp(self.selected_value),
        )

        self.notifier.edit_date(
            old_timestamp, new_timestamp, str(interaction.user.id), self.message.value
        )

        await interaction.response.send_message(
            embed = NotifyMessage("Modified", interaction.user.id, self.date.value.strip(), self.message, success_icon=True), delete_after=4
        )

        await interaction.message.delete(delay=5.5)

class SelectMenu(Select):

    def __init__(self, user_id: int, notifier):
        super().__init__(placeholder="All dates", options=[SelectOption(label="None")])
        dates = notifier.get_dates_of_user(user_id)
        self.notifier = notifier
        self.user_id = user_id
        self.options = (
            [SelectOption(label=date) for date in dates]
            if dates
            else [SelectOption(label="None")]
        )

    async def callback(self, interaction: Interaction):
        if self.values[0] == "None" or interaction.user.id != self.user_id:
            await interaction.response.defer()
            return
        await interaction.response.send_modal(
            EditDateForm(
                title="Edit Date",
                selected_value=self.values[0],
                user_id=interaction.user.id,
                notifier=self.notifier,
            )
        )

class AddButton(Button):

    def __init__(self, user_id, notifier):
        super().__init__(style=ButtonStyle.blurple, label="Add new")
        self.notifier = notifier
        self.user_id = user_id

    async def callback(self, interaction: Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.defer()
            return
        await interaction.response.send_modal(
            NewDateForm(title="Add Date", notifier=self.notifier)
        )

class ViewUI(View):

    def __init__(self, user_id: int, notifier):
        super().__init__(timeout=180)
        self.notifier = notifier
        self.add_items([SelectMenu(user_id, notifier), AddButton(user_id, notifier)])

    def add_items(self, items: list):
        [self.add_item(item) for item in items]


