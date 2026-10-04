from database.db import is_message_replayed


message_id = "TEST-MESSAGE-002"
timestamp = "2026-10-01T23:00:00"


print("==============================================")
print("          Replay Attack Test")
print("==============================================")


# First time receiving the message
first_attempt = is_message_replayed(
    message_id,
    timestamp
)

if first_attempt:
    print("First attempt: REPLAY DETECTED ❌")
else:
    print("First attempt: Message accepted ✅")


# Sending the exact same message again
second_attempt = is_message_replayed(
    message_id,
    timestamp
)

if second_attempt:
    print("Second attempt: REPLAY DETECTED ❌")
else:
    print("Second attempt: Message accepted ✅")


print("==============================================")