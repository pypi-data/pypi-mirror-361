
from leakybucket import LeakyBucket, AsyncLeakyBucket
from leakybucket.persistence import InMemoryLeakyBucketStorage

# MySale's API rate limits:
# - Burst: 90 hits/second over a 5-second period
# - Average: 60 hits/second over a 2-minute period
# Clients violating these thresholds will be blocked for 10 minutes

# Stay conservative and allow 50 / 5 seconds
storage = InMemoryLeakyBucketStorage(
    max_rate=50,
    time_period=5.0
)

# Global throttler instances
throttler = LeakyBucket(storage)
async_throttler = AsyncLeakyBucket(storage)