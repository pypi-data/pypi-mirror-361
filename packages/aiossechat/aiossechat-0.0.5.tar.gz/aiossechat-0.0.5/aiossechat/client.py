
import logging
import aiohttp
import asyncio

from aiohttp import ClientSession
from typing import List, Optional, AsyncGenerator, Final, Sequence, Tuple, Union, Callable, Awaitable, Any, Dict, Literal

from .datatypes import *


async def _run_func(func, *args):
    if hasattr(func, '__call__'):
        func= func.__call__
    if asyncio.iscoroutinefunction(func):
        return await func(*args)
    else:
        return func(*args)

_LOGGER = logging.getLogger("aio-sse-chat")


DEFAULT_VALID_HTTP_CODES: Final[Tuple[int, int, int]] = (200, 301, 307)

EventCallback = Union[Callable[[SSEvent], Any], Callable[[SSEvent], Awaitable[Any]]]
'''Callback when an event is received. It can be async or non-async'''

async def aiosseclient(
    url: str, 
    session: Optional[ClientSession] = None,
    method: Literal['get', 'post', 'put', 'delete', 'patch', 'options', 'head'] = 'get',
    json: Optional[dict] = None,
    headers: Optional[dict[str, str]] = None,
    last_id: Optional[str] = None,
    valid_http_codes: Sequence[int] = DEFAULT_VALID_HTTP_CODES,
    exit_events: Optional[List[str]] = None,
    events: Optional[Dict[str, EventCallback]] = None,
    **kwargs,
) -> AsyncGenerator[SSEvent, None]:
    '''
    A modifier to enable the aio session to handle SSE events.
    
    Args:
        - session: aiohttp.ClientSession
        - url: the url to connect to
        - method: the method to use for the request
        - json: the json data to be sent with the request
        - last_id: the last event id
        - valid_http_codes: the valid http codes, default (200, 301, 307)
        - exit_events: the events that will cause the session to close
        - headers: the extra headers to be added to the request
        - events: Callables for triggering events. {event_name: no-arg-callable}. Callable can be async or non-async.
        - kwargs: other arguments to be passed to the aiohttp.ClientSession.request method
        
    Example:
    ```python
    async for event in aiosseclient(url=some_url, method='post', json=some_data):
        print(data, end='', flush=True)
    ```
    '''
    if session is None:
        session = aiohttp.ClientSession()
    if not isinstance(session, ClientSession):
        raise ValueError('session must be an aiohttp.ClientSession object')
    if not method.lower() in ('get', 'post', 'put', 'delete', 'patch', 'options', 'head'):
        raise ValueError('method must be one of: get, post, put, delete, patch, options, head. Got: "{}"'.format(method))
    method = method.lower() # type: ignore
    
    # The SSE spec requires making requests with Cache-Control: nocache
    headers = headers or {}
    headers.update(
            {
                'Cache-Control' : 'no-cache',
                'Accept': 'text/event-stream',
            }
        )
    if last_id:
        headers['Last-Event-ID'] = last_id

    # Override default timeout of 5 minutes
    session = session or aiohttp.ClientSession()
    json = json or {}
    async with session:
        try:
            sse_method = getattr(session, method)
            response = await sse_method(url, headers=headers, json=json, **kwargs)
            if response.status not in valid_http_codes:
                await session.close()
                raise AioSSEChatInvalidResponseCodeError(response.status)
                
            response_lines = []
            async for line in response.content:
                line = line.decode('utf-8')
                
                if line in SSESep.__members__.values():  # if line is a separator, means the end of an event
                    if response_lines[0] == ':ok\n':
                        response_lines = []
                        continue

                    current_event = SSEvent.parse(''.join(response_lines))
                    if events and current_event.event in events:
                        try:
                            await _run_func(events[current_event.event], current_event)
                        except Exception as e:
                            _LOGGER.error('Error in event %s: %s', current_event.event, e)
                    yield current_event
                    
                    if exit_events and current_event.event in exit_events:
                        await session.close()
                    response_lines = []
                else:
                    response_lines.append(line)
                
        except (TimeoutError, asyncio.TimeoutError) as e:
            _LOGGER.error('TimeoutError: %s', e)



__all__ = ['aiosseclient']