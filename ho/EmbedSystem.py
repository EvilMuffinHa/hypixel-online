import discord


class SimpleEmbedSystem:
    def __init__(self, title, color, emoji="", url="", icon_url=""):
        self.title = title
        self.emoji = emoji
        self.color = color
        self.url = url
        self.icon_url = icon_url


class SimpleEmbed(SimpleEmbedSystem):
    def __init__(self, ses):
        super().__init__(ses.title, ses.color, emoji=ses.emoji, url=ses.url, icon_url=ses.icon_url)
        self.embed = discord.Embed(title="", author="", color=ses.color)
        self.embed.set_footer(text="HypixelOnline v 1.8.2")
        if ses.emoji == "":
            self.embed.set_author(name=ses.title, url=ses.url, icon_url=ses.icon_url)
        else:
            self.embed.set_author(name=ses.emoji + "  " + ses.title, url=ses.url, icon_url=ses.icon_url)

    def getEmbed(self):
        return self.embed

    def toString(self):
        return str(self.embed.to_dict())


    def add_field(self, name, value, inline):
        if name == "":
            name = "\u200b"
        if value == "":
            value = "\u200b"
        self.embed.add_field(name=name, value=value, inline=inline)

    def set_footer(self, text):
        self.embed.set_footer(text=text)

    def set_thumbnail(self, url):
        self.embed.set_thumbnail(url=url)

    def set_image(self, url):
        self.embed.set_image(url=url)
