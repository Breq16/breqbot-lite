import os

from flask import Flask
from flask_discord_interactions import DiscordInteractions


app = Flask(__name__)
discord = DiscordInteractions(app)


app.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
app.config["DISCORD_PUBLIC_KEY"] = os.environ["DISCORD_PUBLIC_KEY"]
app.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]


@discord.command()
def ping(ctx):
    "Respond with a friendly 'pong'!"
    return "Pong!"


discord.set_route("/interactions")


discord.clear_slash_commands(guild_id=os.environ["TESTING_GUILD"])
discord.clear_slash_commands()
discord.register_slash_commands(guild_id=os.environ["TESTING_GUILD"])
discord.register_slash_commands()


if __name__ == '__main__':
    app.run()
