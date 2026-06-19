import os
import pytest

# Mock required environment variables before app imports
os.environ["SECRET_KEY"] = "01234567890123456789012345678912"
os.environ["VAPID_PRIVATE_KEY"] = "your_vapid_private_key_here_that_is_long_enough_for_test"
os.environ["VAPID_PUBLIC_KEY"] = "mock_public_key"
