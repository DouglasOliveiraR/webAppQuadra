import os
os.environ["SECRET_KEY"] = "01234567890123456789012345678912"
os.environ["VAPID_PRIVATE_KEY"] = "mock_vapid_private_key_that_is_at_least_40_chars_long_for_testing_purposes"
os.environ["VAPID_PUBLIC_KEY"] = "mock_vapid_public_key_for_testing"
