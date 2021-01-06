import requests

from flask_discord_interactions import (DiscordInteractionsBlueprint,
                                        InteractionResponse)


bp = DiscordInteractionsBlueprint()


def make_reddit_command(endpoint, info):
    if len(endpoint) < 3:
        endpoint += "_"*(3-len(endpoint))

    @bp.command(name=endpoint, description=info["desc"])
    def _reddit_command(ctx):
        result = requests.get(f"https://redditor.breq.dev/{endpoint}").json()
        return InteractionResponse(embed={
            "title": result["title"],
            "url": result["url"],
            "image": {"url": result["url"]}
        })


reddit_endpoints = requests.get("https://redditor.breq.dev/list").json()

for endpoint, info in reddit_endpoints.items():
    make_reddit_command(endpoint, info)
