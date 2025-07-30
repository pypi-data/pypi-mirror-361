'''
aio sse client
Edit from pypi module `aiosseclient`
'''

import re
import sys
import logging

from enum import Enum

if sys.version_info >= (3, 11):
    from typing import List, Optional, Final, Union, Self, Literal
else:
    from typing import List, Optional, Final, Union, Literal
    from typing_extensions import Self

from dataclasses import dataclass

_SSE_LINE_PATTERN: Final[re.Pattern] = re.compile('(?P<name>[^:]*):?( ?(?P<value>.*))?')
_LOGGER = logging.getLogger("aio-sse-chat")


class SSESep(str, Enum):
    '''
    Available separators for SSE.
    SSE only allows these separators.
    '''
    R_N = '\r\n'
    R = '\r'
    N = '\n'
    
    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other
        elif isinstance(other, DefaultSSEType):
            return self.value == other.value
        return Enum.__eq__(self, other)


class DefaultSSEType(str, Enum):
    '''The default event types for SSE'''
    
    DATA = 'data'
    EVENT = 'event'
    ID = 'id'
    RETRY = 'retry'
    Comment = ':'
    
    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other
        elif isinstance(other, DefaultSSEType):
            return self.value == other.value
        return Enum.__eq__(self, other)
    
    @classmethod
    def GetSSEType(cls, sse_type_str: str)->Union[Self, str]:
        for member in cls:
            if member.value == sse_type_str:
                return member
        return sse_type_str


@dataclass
class SSEventContent:
    '''Each content means a line in the SSE message. It can be a comment, data, event, id, or retry.'''
    content_type: Union[DefaultSSEType, str]
    value: str


DEFAULT_EVENT_NAME = 'message'
class SSEvent:
    '''The object created as the result of received events'''

    event: str
    id: Optional[str]
    contents: List[SSEventContent]
    retry: Optional[bool]

    def __init__(
        self,
        event: str = DEFAULT_EVENT_NAME,
        id: Optional[str] = None,
        retry: Optional[bool] = None
    ):
        self.event = event
        self.id = id
        self.retry = retry
        self.contents = []

    @classmethod
    def parse(cls, raw:str):
        '''
        Given a possibly-multiline string representing an SSE message, parse it
        and return a Event object.
        '''
        event = cls()
        for line in raw.splitlines():
            m = _SSE_LINE_PATTERN.match(line)
            if m is None:
                # Malformed line.  Discard but warn.
                _LOGGER.warning('Invalid SSE line: %s', line)
                continue

            name = m.group('name')
            if name == '':
                if line[0] == ':':
                    event.contents.append(SSEventContent(DefaultSSEType.Comment, line[1:]))
                continue    # line began with a ':', so is a comment.  Ignore
            else:
                sse_type = DefaultSSEType.GetSSEType(name)
            
            value = m.group('value')
            event.contents.append(SSEventContent(sse_type, value))
            
            if sse_type == DefaultSSEType.EVENT:
                event.event = value
            elif sse_type == DefaultSSEType.ID:
                event.id = value
            elif sse_type == DefaultSSEType.RETRY:
                event.retry = int(value)    # type: ignore

        return event

    def __str__(self) -> str:
        return self.data

    @property
    def data(self) -> str:
        data_str = ''
        last_data = None
        for content in self.contents:
            if content.content_type == DefaultSSEType.DATA:
                data_str += (('\n' if last_data is not None else '') + content.value)
                last_data = content.value
        return data_str



__all__ = ['SSEvent', 'SSEventContent', 'DefaultSSEType', 'SSESep']

class AioSSEChatError(Exception):
    '''Base class for all aio-sse-chat exceptions.'''
    pass

class AioSSEChatInvalidResponseCodeError(AioSSEChatError):
    '''Raised when the server returns an invalid HTTP response code.'''
    def __init__(self, code: int):
        super().__init__(f'Invalid HTTP response code: {code}')
        self.code = code
        
        
__all__.extend(['AioSSEChatError', 'AioSSEChatInvalidResponseCodeError'])