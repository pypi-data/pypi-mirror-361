import random
from datetime import datetime, timezone, timedelta
from faker import Faker

fake = Faker()


def dtc_factory(num_entries=10):
    base_time = datetime.now(timezone.utc)
    dtc_data = []

    for i in range(num_entries):
        entry_time = (base_time + timedelta(seconds=i)).isoformat()

        entry = {
            "description": fake.sentence(nb_words=6),
            "dtcId": f"DTC{random.randint(1000, 9999)}",
            "status": random.choice(["Active", "Inactive"]),
            "time": entry_time,
        }

        if random.choice([True, False]):
            entry["extension"] = [
                {
                    "time": entry_time,
                    "bytes": fake.hexify(text="^" * 8),
                }
            ]

        if random.choice([True, False]):
            entry["snapshot"] = [
                {
                    "time": entry_time,
                    "bytes": fake.hexify(text="^" * 8),
                }
            ]

        dtc_data.append(entry)

    return {"data": dtc_data}
