import os

from flask import Flask, redirect
from flask_discord_interactions import DiscordInteractions

import reddit
import card


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


@app.route("/")
def index():
    return redirect(os.environ["OAUTH_URL"])


discord.register_blueprint(reddit.bp)
discord.register_blueprint(card.bp)

discord.update_slash_commands(guild_id=os.environ["TESTING_GUILD"])
discord.update_slash_commands()


if __name__ == '__main__':
    app.run()
