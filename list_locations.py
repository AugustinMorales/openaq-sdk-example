from openaq import OpenAQ

with OpenAQ() as client:
    locations = client.locations.list(
        parameters_id=2,
        coordinates=(15.81207, 102.02316),
        radius=10_000,
        limit=1000,
    )
    print(f"Found {len(locations.results)} PM2.5 locations within 10 km\n")
    for loc in locations.results:
        first = loc.datetime_first.utc if loc.datetime_first else None
        last = loc.datetime_last.utc if loc.datetime_last else None
        print(f"{loc.id:>10}  {loc.name:<40}  first: {first}  last: {last}")
