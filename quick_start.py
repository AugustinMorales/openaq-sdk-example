from openaq import OpenAQ

client = OpenAQ()  # reads OPENAQ_API_KEY from the environment
location = client.locations.get(2178)
client.close()

print(location.results[0].name)
