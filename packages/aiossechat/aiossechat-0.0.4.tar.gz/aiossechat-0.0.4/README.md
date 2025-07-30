# aio-sse-chat

Special python aio sse client module especially for parsing server-sent events (SSE) response from LLM. 

Modified from [aiohttp-sse-client](https://github.com/ebraminio/aiosseclient)

## Why need this?
Normal SSE packages will not get correct value from streaming LLM response(in case you have not escape `\n` to `\\n`) since it will not parse the response correctly. This module will parse the response correctly and return the correct value.  

Also, LLM request usually need to submit a `POST` request while most current aio sse modules choose to raise error when submit a `POST` request. Though it is not a good practice to use `POST` request to get a streaming response, but it helps a lot for simplifying the code.

## Installation
```bash
pip install aio-sse-chat
```

## Usage
Create your aiohttp session and use `aiosseclient` to wrap the session to do request. 

```python
# fastapi side

@app.post('/sse')   # support all http methods
async def sse_endpoint(data: dict):
    async def f():
        for i in range(10):
            yield '\n'
            await asyncio.sleep(0.2)
    return EventSourceResponse(f())

##################
# client side

import aiohttp
from aiossechat import aiosseclient

async for event in aiosseclient(url=some_url, method='post', json=some_data):
    print(data, end='', flush=True)   # can get single `'\n'` correctly

```
```