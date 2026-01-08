import src.config.constants as C
import random


#region random geolocation
def random_geolocation():
    West_longitude = -73.983033
    East_longitude = -28.84764
    South_latitude = -33.751178
    North_latitude = 5.271841

    geolocation= {
        "latitude": random.uniform(South_latitude, North_latitude),
        "longitude": random.uniform(East_longitude, West_longitude),
    }
    return geolocation
#endregion random geolocation


#region random user agent
def random_user_agent():
    agent_list = [
# from this page: https://deviceatlas.com/blog/list-of-user-agent-strings
# Android User Agents
# With the Client Hints support
'Mozilla/4.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
'Mozilla/4.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
'Mozilla/4.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36,gzip(gfe)',
# Desktop User Agents
"Mozilla/4.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0",
"Mozilla/4.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
"Mozilla/4.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3.1 Safari/605.1.15",
"Mozilla/4.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36>",
"Mozilla/4.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1"
    ]
    return random.choice(agent_list)
    ...
#endregion random user agent


#region request curncurrency limit decorator
import asyncio
from functools import wraps
def request_concurrency_limit_decorator():
    # Bind the default event loop
    # print(f"C.WINDOW_NUMBER {C.WINDOW_NUMBER}")
    sem = asyncio.Semaphore(C.WINDOW_NUMBER)

    def executor(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with sem:
                return await func(*args, **kwargs)
        return wrapper
    return executor
#endregion request curncurrency limit decorator
