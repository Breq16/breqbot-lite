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


def freeze_card(user):
    params = {
        field: (db.hget(f"card:{user.id}:params", field)
                or defaults[field])
        for field in fields
    }

    params["name"] = user.display_name
    params["avatar"] = user.avatar_url

    response = requests.post("https://cards.breq.dev/card", params=params)
    response.raise_for_status()

    card_id = response.json()["card_id"]

    db.set(f"card:{user.id}:id", card_id)

    return card_id


def get_card(user):
    card_id = db.get(f"card:{user.id}:id")
    if not card_id:
        card_id = freeze_card(user)

    return f"https://cards.breq.dev/card/{card_id}.png"


def get_card_by_id(user_id):
    card_id = db.get(f"card:{user_id}:id")

    if card_id:
        return f"https://cards.breq.dev/card/{card_id}.png"
    else:
        return None


@bp.command(options=[{
    "name": "member",
    "description": "Member to get the card from (defaults to yourself).",
    "type": CommandOptionType.USER,
    "required": False
}])
def card(ctx, member=None):
    "Return the card of a user"

    if member is None:
        return InteractionResponse(
            embed={"image": {"url": get_card(ctx.author)}})
    else:
        card_url = get_card_by_id(member)
        if card_url:
            return InteractionResponse(embed={"image": {"url": card_url}})
        else:
            return "That user has not set their card with `/setcard`."


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

    freeze_thread = threading.Thread(target=freeze_card, args=(ctx.author,))
    freeze_thread.start()
    return ":white_check_mark:"
