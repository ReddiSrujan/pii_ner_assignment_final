import json
import os
import random
import string

PII_LABELS = [
    "CREDIT_CARD",
    "PHONE",
    "EMAIL",
    "PERSON_NAME",
    "DATE",
]
NON_PII_LABELS = [
    "CITY",
    "LOCATION",
]

FIRST_NAMES = ["john", "mary", "sanjay", "priya", "rohit", "emma", "li", "fatima"]
LAST_NAMES = ["smith", "reddy", "khan", "patel", "wang", "fernandez", "singh"]
CITIES = ["mumbai", "delhi", "new york", "london", "bangalore", "san francisco"]
LOCATIONS = ["central park", "times square", "marine drive", "india gate"]

MONTHS = ["january", "february", "march", "april", "may", "june",
          "july", "august", "september", "october", "november", "december"]


def random_email():
    user = random.choice(FIRST_NAMES) + random.choice([".", "_", ""]) + random.choice(LAST_NAMES)
    domain = random.choice(["gmail", "yahoo", "outlook", "hotmail"])
    tld = random.choice(["com", "in", "net"])
    return f"{user}@{domain}.{tld}"


def random_email_stt():
    # john dot doe at gmail dot com
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    domain = random.choice(["gmail", "yahoo", "outlook"])
    tld = random.choice(["com", "in"])
    return f"{first} dot {last} at {domain} dot {tld}"


def random_phone():
    # 10 or 11 digit phone, maybe +91
    base = "".join(random.choice(string.digits) for _ in range(10))
    if random.random() < 0.4:
        return "+91" + base
    return base


def random_credit_card():
    # 16 digit, grouped or plain
    digits = "".join(random.choice(string.digits) for _ in range(16))
    if random.random() < 0.5:
        return " ".join([digits[i:i+4] for i in range(0, 16, 4)])
    return digits


def random_person_name():
    return random.choice(FIRST_NAMES) + " " + random.choice(LAST_NAMES)


def random_date_text():
    # a few simple patterns
    year = random.randint(2010, 2025)
    day = random.randint(1, 28)
    month = random.choice(MONTHS)

    pattern = random.choice([
        f"{day} {month} {year}",
        f"{month} {day} {year}",
        f"{day}/{random.randint(1,12)}/{str(year)[2:]}",
        f"{year}-{random.randint(1,12):02d}-{day:02d}",
    ])
    return pattern


def random_city():
    return random.choice(CITIES)


def random_location():
    return random.choice(LOCATIONS)


def add_entity(text, entities, entity_text, label):
    """
    Append ' entity_text' (with a preceding space) to text, register span.
    Returns new_text, updated_entities.
    """
    # Add a space before entity_text unless text is empty
    prefix = "" if len(text) == 0 else " "
    start = len(text) + len(prefix)
    end = start + len(entity_text)
    new_text = text + prefix + entity_text
    entities.append({"start": start, "end": end, "label": label})
    return new_text, entities


def make_example(idx: int):
    """
    Build a single noisy STT-style example with 1–3 entities.
    """
    text = ""
    entities = []

    # Some random filler words like STT
    def add_filler(t):
        fillers = ["uh", "like", "you know", "actually", "so", "basically"]
        if random.random() < 0.5:
            t = t + (" " if t else "") + random.choice(fillers)
        return t

    pattern = random.choice([
        "credit_card",
        "phone",
        "email",
        "person_date_city",
        "mixed",
    ])

    if pattern == "credit_card":
        text = "my credit card number is"
        text = add_filler(text)
        cc = random_credit_card()
        text, entities = add_entity(text, entities, cc, "CREDIT_CARD")

    elif pattern == "phone":
        text = "you can call me on"
        text = add_filler(text)
        ph = random_phone()
        text, entities = add_entity(text, entities, ph, "PHONE")

    elif pattern == "email":
        if random.random() < 0.5:
            em = random_email()
        else:
            em = random_email_stt()
        text = "my email is"
        text = add_filler(text)
        text, entities = add_entity(text, entities, em, "EMAIL")

    elif pattern == "person_date_city":
        name = random_person_name()
        dt = random_date_text()
        city = random_city()
        text = "i met"
        text, entities = add_entity(text, entities, name, "PERSON_NAME")
        text = text + " on"
        text, entities = add_entity(text, entities, dt, "DATE")
        text = text + " in"
        text, entities = add_entity(text, entities, city, "CITY")

    elif pattern == "mixed":
        # Combine 2–3 entities
        name = random_person_name()
        em = random_email() if random.random() < 0.5 else random_email_stt()
        ph = random_phone()
        loc = random_location()
        text = "contact"
        text, entities = add_entity(text, entities, name, "PERSON_NAME")
        text = text + " on"
        text, entities = add_entity(text, entities, em, "EMAIL")
        text = text + " or"
        text, entities = add_entity(text, entities, ph, "PHONE")
        text = text + " near"
        text, entities = add_entity(text, entities, loc, "LOCATION")

    # Add trailing filler
    text = add_filler(text)

    return {
        "id": f"utt_{idx:04d}",
        "text": text,
        "entities": entities,
    }


def main():
    random.seed(42)

    os.makedirs("data", exist_ok=True)

    train_size = 800
    dev_size = 200
    test_size = 200

    # Train
    with open("data/train.jsonl", "w", encoding="utf-8") as f:
        for i in range(train_size):
            ex = make_example(i)
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    # Dev
    with open("data/dev.jsonl", "w", encoding="utf-8") as f:
        for i in range(train_size, train_size + dev_size):
            ex = make_example(i)
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    # Test (no labels)
    with open("data/test.jsonl", "w", encoding="utf-8") as f:
        for i in range(train_size + dev_size, train_size + dev_size + test_size):
            ex = make_example(i)
            ex.pop("entities", None)
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    print("Wrote train/dev/test to data/")

if __name__ == "__main__":
    main()
