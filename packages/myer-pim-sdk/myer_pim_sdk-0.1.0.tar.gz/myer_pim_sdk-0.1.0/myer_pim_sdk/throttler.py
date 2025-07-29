import asyncio
import time
from typing import Optional

from leakybucket import LeakyBucket, AsyncLeakyBucket
from leakybucket.persistence import InMemoryLeakyBucketStorage

# Myer's API allows max 20 calls per minute = 20/60 = 0.333 calls per second
# We'll be conservative and use 18 calls per minute to account for timing variations
storage = InMemoryLeakyBucketStorage(
    max_rate=18,
    time_period=60.0
)


throttler = LeakyBucket(storage)
async_throttler = AsyncLeakyBucket(storage)