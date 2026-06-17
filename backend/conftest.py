import os

os.environ["SECRET_KEY"] = "01234567890123456789012345678912"
os.environ["VAPID_PRIVATE_KEY"] = "mock_private_key_that_is_long_enough_for_validation_123456789"
os.environ["VAPID_PUBLIC_KEY"] = "mock_public_key"
