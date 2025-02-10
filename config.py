# Set this to True to enable push notifications. You will need to provide the necessary information below.

PUSH_NOTIFICATIONS = False

PUSH_ENDPOINT = None
PUSH_P256DH = None
PUSH_AUTH = None
PUSH_VAPID_PRIVATE_KEY = None
PUSH_EMAIL = None


# Configure the sleep hours for the application. The sensor will be put to sleep during these hours.
# The format is "HH:MM" (24-hour format). Set to None to disable sleep mode.
SLEEP_HOURS_START = "23:30"
SLEEP_HOURS_END = "06:30"

# Configure the timezone and location for the data visualization.
# The TIMEZONE should be a string from the IANA Time Zone Database.
TIMEZONE = "Europe/Berlin"