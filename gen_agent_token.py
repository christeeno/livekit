from livekit import api

# Replace with your LiveKit Cloud API key + secret
API_KEY="APIVPm7gKomS996"
API_SECRET="FYY8EppBzVOBHMmYTahaMjZCf4t3ABXJdVfLVUwQ8m1"
# Create an agent token
# Create an agent grant

# Define video grants (permissions)
video_grants = api.VideoGrants(
    room_join=True,   # allow joining rooms
    room="*"          # allow joining any room
)

# Build token
token = api.AccessToken(API_KEY, API_SECRET) \
    .with_identity("mednova-agent") \
    .with_grants(video_grants) \
    .to_jwt()

print("Agent Token:\n", token)