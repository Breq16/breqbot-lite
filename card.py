import os
import threading

import requests
import redis

from flask_discord_interactions import (DiscordInteractionsBlueprint,
                                        InteractionResponse,
                                        CommandOptionType)

bp = DiscordInteractionsBlueprint()

db = redis.from_url(os.environ["REDIS_URL"], decode_responses=True)

fields = {
    "bio": "Set your profile card description!",
    "background": "Pick a cool background image for your card.",
    "template": ("Set the template for the card. "
                 "Current options are 'light-profile' and 'dark-profile'.")
}

defaults = {
    "bio": "",
    "background": "https://breq.dev/assets/images/pansexual.png",
    "template": "light-profile"
}


def freeze_card(ctx):
    params = {
        field: (db.hget(f"card:{ctx.author.id}:params", field)
                or defaults[field])
        for field in fields
    }

    params["name"] = ctx.author.display_name
    params["avatar"] = ctx.author.avatar_url

    response = requests.post("https://cards.breq.dev/card", params=params)
    response.raise_for_status()

    card_id = response.json()["card_id"]

    db.set(f"card:{ctx.author.id}:id", card_id)

    return card_id


def get_card(ctx):
    card_id = db.get(f"card:{ctx.author.id}:id")
    if not card_id:
        card_id = freeze_card(ctx)

    return f"https://cards.breq.dev/card/{card_id}.png"


@bp.command()
def card(ctx):
    "Return the card of a user"
    return InteractionResponse(embed={
        "image": {"url": get_card(ctx)}
    })


set_options = []
for name, description in fields.items():
    set_options.append({
        "name": name,
        "description": description,
        "type": CommandOptionType.STRING,
        "required": False
    })


@bp.command(options=set_options)
def setcard(ctx, **kwargs):
    "Set an attribute of a card"
    for field, value in kwargs.items():
        db.hset(f"card:{ctx.author.id}:params", field, value)

    freeze_thread = threading.Thread(target=freeze_card, args=(ctx,))
    freeze_thread.start()
    return ":white_check_mark:"
