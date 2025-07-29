import random
from datetime import datetime, timezone, timedelta
from faker import Faker

fake = Faker()


def gps_factory(num_entries=120):
    base_time = datetime.now(timezone.utc)
    gps_data = []

    for i in range(num_entries):
        timestamp = (base_time + timedelta(seconds=i)).isoformat() + "Z"

        entry = {
            "time": timestamp,
            "latitude": round(fake.latitude(), 6),
            "longitude": round(fake.longitude(), 6),
            "accuracy": round(random.uniform(5.0, 50.0), 2),
            "altitude": round(random.uniform(100.0, 1000.0), 2),
            "speed": round(random.uniform(0.0, 120.0), 2),
            "bearing": round(random.uniform(0.0, 360.0), 2),
            "available": {
                "accuracy": random.choice([True, False]),
                "altitude": random.choice([True, False]),
                "bearing": random.choice([True, False]),
                "date": random.choice([True, False]),
                "latlon": random.choice([True, False]),
                "speed": random.choice([True, False]),
                "time": random.choice([True, False]),
            },
        }

        gps_data.append(entry)

    return {"data": gps_data}
