# file: projects/games/qpig.py
"""Prototype incremental game about quantum guinea pigs."""

from gway import gw
import time
import json
import math

DEFAULT_PIGS = 1
DEFAULT_MICROCERTS = 500  # 0.5 Cert
DEFAULT_ENC_SMALL = 1
DEFAULT_ENC_LARGE = 0
DEFAULT_AVAILABLE = 3
DEFAULT_VEGGIES = {}
DEFAULT_FOOD = []

ENCLOSURE_MAX = 8

CERTAINTY_MAX = 1000  # stored in microcerts
FILL_TIME = 10 * 60  # base seconds from 0 to 1
ENC_TIME_SMALL = 5 * 60
ENC_TIME_LARGE = 8 * 60

SMALL_COST = 650
LARGE_COST = 920
UPKEEP_SMALL_HR = 2.0
UPKEEP_LARGE_HR = 3.0

ADOPTION_ADD = 2
ADOPTION_INTERVAL = 3 * 3600
ADOPTION_THRESHOLD = 7

# QP generation: 50% chance every 30s plus +/-25% from Certainty
QP_INTERVAL = 30.0  # seconds between pellet attempts
QP_BASE_CHANCE = 0.5
QP_CERT_BONUS = 0.25

VEGGIE_TYPES = ["carrot", "lettuce", "cilantro", "cucumber"]
VEGGIE_BASE_PRICE = 12
VEGGIE_PRICE_SPREAD = 8

# chance to generate an extra pellet while nibbling
VEGGIE_BONUS = {
    "carrot": 0.25,
    "lettuce": 0.15,
    "cilantro": 0.3,
    "cucumber": 0.2,
}

# how long each veggie is eaten and how long the boost lingers, in seconds
VEGGIE_EFFECTS = {
    "carrot": (60, 30),
    "lettuce": (90, 45),
    "cilantro": (120, 60),
    "cucumber": (75, 40),
}


def _use_cookies():
    """Return True if cookie support is available and accepted."""
    use = (
        hasattr(gw.web, "app")
        and hasattr(gw.web, "cookies")
        and getattr(gw.web.app, "is_setup", lambda x: False)("web.cookies")
        and gw.web.cookies.accepted()
    )
    gw.debug(f"_use_cookies -> {use}")
    return use


def _get_offer():
    """Return the current veggie offer, generating a new one if needed."""
    if not _use_cookies():
        import random

        kind = random.choice(VEGGIE_TYPES)
        qty = random.randint(1, 3)
        price = VEGGIE_BASE_PRICE + random.randint(-VEGGIE_PRICE_SPREAD, VEGGIE_PRICE_SPREAD)
        offer = kind, qty, max(5, min(20, price))
        gw.debug(f"_get_offer (no cookies) -> {offer}")
        return offer

    cookies = gw.web.cookies
    kind = cookies.get("qpig_offer_kind")
    qty = cookies.get("qpig_offer_qty")
    price = cookies.get("qpig_offer_price")
    if kind and qty and price:
        offer = (kind, int(qty), int(price))
        gw.debug(f"_get_offer (existing) -> {offer}")
        return offer
    import random

    kind = random.choice(VEGGIE_TYPES)
    qty = random.randint(1, 3)
    price = VEGGIE_BASE_PRICE + random.randint(-VEGGIE_PRICE_SPREAD, VEGGIE_PRICE_SPREAD)
    price = max(5, min(20, price))
    cookies.set("qpig_offer_kind", kind, path="/", max_age=300)
    cookies.set("qpig_offer_qty", str(qty), path="/", max_age=300)
    cookies.set("qpig_offer_price", str(price), path="/", max_age=300)
    offer = (kind, qty, price)
    gw.debug(f"_get_offer (new) -> {offer}")
    return offer


def _clear_offer():
    if not _use_cookies():
        return

    cookies = gw.web.cookies
    for k in ["qpig_offer_kind", "qpig_offer_qty", "qpig_offer_price"]:
        cookies.delete(k, path="/")
    gw.debug("_clear_offer: offer cookies cleared")


def _get_state():
    cookies = gw.web.cookies
    pigs = int(cookies.get("qpig_pigs") or DEFAULT_PIGS)
    mc = float(cookies.get("qpig_mc") or DEFAULT_MICROCERTS)
    pellets = float(cookies.get("qpig_qp") or 0.0)
    last_time = float(cookies.get("qpig_time") or time.time())
    avail = int(cookies.get("qpig_avail") or DEFAULT_AVAILABLE)
    enc_small = int(cookies.get("qpig_enc_small") or DEFAULT_ENC_SMALL)
    enc_large = int(cookies.get("qpig_enc_large") or DEFAULT_ENC_LARGE)
    last_add = float(cookies.get("qpig_last_add") or last_time)
    veggies = json.loads(cookies.get("qpig_veggies") or "{}")
    food = json.loads(cookies.get("qpig_food") or "[]")
    state = (
        pigs,
        mc,
        pellets,
        last_time,
        avail,
        enc_small,
        enc_large,
        last_add,
        veggies,
        food,
    )
    gw.debug(f"_get_state -> {state}")
    return state


def _set_state(
    pigs: int,
    mc: float,
    pellets: float,
    timestamp: float,
    avail: int,
    enc_small: int,
    enc_large: int,
    last_add: float,
    veggies: dict,
    food: list,
) -> None:
    cookies = gw.web.cookies
    cookies.set("qpig_pigs", str(pigs), path="/", max_age=30 * 24 * 3600)
    cookies.set("qpig_mc", str(mc), path="/", max_age=30 * 24 * 3600)
    cookies.set("qpig_qp", str(pellets), path="/", max_age=30 * 24 * 3600)
    cookies.set("qpig_time", str(timestamp), path="/", max_age=30 * 24 * 3600)
    cookies.set("qpig_avail", str(avail), path="/", max_age=30 * 24 * 3600)
    cookies.set("qpig_enc_small", str(enc_small), path="/", max_age=30 * 24 * 3600)
    cookies.set("qpig_enc_large", str(enc_large), path="/", max_age=30 * 24 * 3600)
    cookies.set("qpig_last_add", str(last_add), path="/", max_age=30 * 24 * 3600)
    cookies.set("qpig_veggies", json.dumps(veggies), path="/", max_age=30 * 24 * 3600)
    cookies.set("qpig_food", json.dumps(food), path="/", max_age=30 * 24 * 3600)
    gw.debug(
        "_set_state: pigs=%s mc=%s pellets=%s avail=%s enc_small=%s enc_large=%s veggies=%s food=%s"
        % (pigs, mc, pellets, avail, enc_small, enc_large, veggies, food)
    )


def _process_state(action: str | None = None):
    """Update and optionally mutate the farm state."""
    use_cookies = _use_cookies()
    gw.debug(f"_process_state start: action={action} use_cookies={use_cookies}")
    (
        pigs,
        mc,
        pellets,
        last_time,
        avail,
        enc_small,
        enc_large,
        last_add,
        veggies,
        food,
    ) = (
        _get_state()
        if use_cookies
        else (
            DEFAULT_PIGS,
            DEFAULT_MICROCERTS,
            0.0,
            time.time(),
            DEFAULT_AVAILABLE,
            DEFAULT_ENC_SMALL,
            DEFAULT_ENC_LARGE,
            time.time(),
            DEFAULT_VEGGIES.copy(),
            DEFAULT_FOOD.copy(),
        )
    )
    gw.debug(
        "initial state: pigs=%s mc=%s pellets=%s avail=%s enc_small=%s enc_large=%s veggies=%s food=%s"
        % (pigs, mc, pellets, avail, enc_small, enc_large, veggies, food)
    )

    now = time.time()
    dt = max(0.0, min(now - last_time, 3600))
    gw.debug(f"time delta={dt}")

    upkeep_mc = ((UPKEEP_SMALL_HR * enc_small) + (UPKEEP_LARGE_HR * enc_large)) * (
        dt / 3600
    )
    mc = max(0.0, mc - upkeep_mc)
    gw.debug(f"after upkeep: mc={mc}")

    fill_time = FILL_TIME + enc_small * ENC_TIME_SMALL + enc_large * ENC_TIME_LARGE
    cert_frac = mc / CERTAINTY_MAX
    cert_frac = 1.0 - (1.0 - cert_frac) * math.exp(-dt / fill_time)
    mc = min(CERTAINTY_MAX, cert_frac * CERTAINTY_MAX)
    gw.debug(f"after fill: mc={mc}")

    # handle food buffs
    food = [f for f in food if f[1] > now]
    buff_active = any(f[2] > now for f in food)
    buff_mult = 2.0 if buff_active else 1.0

    intervals = int(dt / QP_INTERVAL)
    if intervals > 0:
        import random
        base_prob = QP_BASE_CHANCE * (1 + (cert_frac - 0.5) * QP_CERT_BONUS * 2)
        prob = min(1.0, base_prob * buff_mult)
        gw.debug(f"pellet gen: intervals={intervals} prob={prob} pigs={pigs}")
        for _ in range(intervals):
            for _ in range(pigs):
                if random.random() < prob:
                    pellets += 1
                    if random.random() < prob:
                        pellets += 1
        last_time += intervals * QP_INTERVAL

    # chance for bonus pellets from active veggies
    nibbling = [f[0] for f in food if f[1] > now]
    if nibbling:
        import random
        gw.debug(f"nibbling: {nibbling}")
        for kind in nibbling:
            chance = VEGGIE_BONUS.get(kind, 0.0)
            if random.random() < chance:
                pellets += 1

    # replenish adoption queue
    while now - last_add >= ADOPTION_INTERVAL and avail <= ADOPTION_THRESHOLD:
        avail = min(avail + ADOPTION_ADD, ADOPTION_THRESHOLD)
        last_add += ADOPTION_INTERVAL
        gw.debug(f"adoption queue replenished -> avail={avail}")

    offer_kind, offer_qty, offer_price = _get_offer()

    capacity = enc_small + enc_large * 2
    if action == "adopt" and avail > 0 and pigs < capacity:
        pigs += 1
        avail -= 1
        gw.debug(f"action adopt -> pigs={pigs} avail={avail}")
    elif action == "buy_small" and mc >= SMALL_COST and (enc_small + enc_large) < ENCLOSURE_MAX:
        mc -= SMALL_COST
        enc_small += 1
        gw.debug(f"action buy_small -> enc_small={enc_small} mc={mc}")
    elif action == "buy_large" and mc >= LARGE_COST and (enc_small + enc_large) < ENCLOSURE_MAX:
        mc -= LARGE_COST
        enc_large += 1
        gw.debug(f"action buy_large -> enc_large={enc_large} mc={mc}")
    elif action == "buy_veggie":
        total = offer_price * offer_qty
        if mc >= total:
            mc -= total
            veggies[offer_kind] = veggies.get(offer_kind, 0) + offer_qty
            _clear_offer()
            offer_kind, offer_qty, offer_price = _get_offer()
            gw.debug(f"action buy_veggie -> veggies={veggies} mc={mc}")
    elif action and action.startswith("place_"):
        kind = action.split("_", 1)[1]
        slots = (enc_small + enc_large) * 3
        if veggies.get(kind, 0) > 0 and len(food) < slots:
            veggies[kind] -= 1
            if veggies[kind] == 0:
                del veggies[kind]
            eat, linger = VEGGIE_EFFECTS.get(kind, (60, 30))
            food.append([kind, now + eat, now + eat + linger])
            gw.debug(f"action place_{kind} -> food={food} veggies={veggies}")

    if use_cookies:
        _set_state(
            pigs,
            mc,
            pellets,
            last_time,
            avail,
            enc_small,
            enc_large,
            last_add,
            veggies,
            food,
        )

    state = (
        pigs,
        mc,
        pellets,
        last_time,
        avail,
        enc_small,
        enc_large,
        veggies,
        food,
        (offer_kind, offer_qty, offer_price),
        use_cookies,
    )
    gw.debug(f"_process_state end -> {state}")
    return state


def render_qpig_farm_stats(*_, **__):
    """Return the farm stats block (used by render.js)."""
    gw.debug("render_qpig_farm_stats called")
    (
        pigs,
        mc,
        pellets,
        _now,
        avail,
        enc_small,
        enc_large,
        veggies,
        food,
        offer,
        _use,
    ) = _process_state()
    capacity = enc_small + enc_large * 2
    veg_list = ", ".join(f"{k}:{v}" for k, v in veggies.items()) or "none"
    food_list = ", ".join(f"{f[0]}" for f in food) or "none"
    html = [
        f"<p>You have <b>{pigs}</b> quantum pigs (capacity {capacity}).</p>",
        f"<p>Certainty: <b>{int(mc)}</b> MC / {CERTAINTY_MAX}</p>",
        f"<p>QPellets: <b>{int(pellets)}</b></p>",
        f"<p>Veggies: {veg_list}</p>",
        f"<p>Food placed: {food_list}</p>",
        f"<p>Pigs waiting for adoption: {avail}</p>",
    ]
    return "\n".join(html)


def view_qpig_farm(*, action: str = None, **_):
    """Main Quantum Piggy farm view."""
    gw.debug(f"view_qpig_farm called with action={action}")
    (
        pigs,
        mc,
        pellets,
        _now,
        avail,
        enc_small,
        enc_large,
        veggies,
        food,
        offer,
        use_cookies,
    ) = _process_state(action)

    offer_kind, offer_qty, offer_price = offer
    capacity = enc_small + enc_large * 2
    refresh = 3 if any(f[1] > time.time() for f in food) else 5
    html = [
        '<link rel="stylesheet" href="/static/games/qpig/farm.css">',
        '<div class="qpig-garden">',
        "<h1>Quantum Piggy Farm</h1>",
        f'<div id="qpig-stats" data-gw-render="stats" data-gw-refresh="{refresh}">',
        render_qpig_farm_stats(),
        "</div>",
        "<form method='post' class='qpig-buttons'>",
    ]
    if avail > 0 and pigs < capacity:
        html.append("<button type='submit' name='action' value='adopt'>Adopt Pig</button>")
    html.extend(
        [
            f"<button type='submit' name='action' value='buy_small'>Buy Enclosure ({SMALL_COST} MC)</button>",
            f"<button type='submit' name='action' value='buy_large'>Buy Large Enclosure ({LARGE_COST} MC)</button>",
            f"<button type='submit' name='action' value='buy_veggie'>Buy {offer_qty} {offer_kind}(s) ({offer_price * offer_qty} MC)</button>",
        ]
    )

    slots = (enc_small + enc_large) * 3
    if len(food) < slots:
        for k, v in veggies.items():
            if v > 0:
                html.append(f"<button type='submit' name='action' value='place_{k}'>Feed {k}</button>")
    html.append("</form>")
    if not use_cookies:
        html.append(
            "<div class='qpig-warning'>Enable cookies to save your progress.</div>"
        )
    html.append("</div>")
    return "\n".join(html)
