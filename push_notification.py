import json
from pywebpush import webpush

def send(title, message, endpoint, p256dh, auth, vapid_private, email):
    webpush(
        subscription_info={
            "endpoint": endpoint,
            "keys": {
                "p256dh": p256dh,
                "auth": auth
            }
        },
        data=json.dumps({"title": f"{title}", "body": f"{message}"}),
        vapid_private_key=vapid_private,
        vapid_claims={"sub": f"mailto:{email}"},
    )