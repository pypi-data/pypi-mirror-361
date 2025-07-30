'''
Module that fixes SSE prase bugs when facing to single '\n' characters.
Modify from module `aiosseclient`

Example:
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

async for event in aiosseclient(url=some_url, method='post', json=some_data):
    print(data, end='', flush=True)   # can get single `'\n'` correctly

```
    
'''

from .datatypes import *

from .client import *