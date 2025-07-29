"""HTTP client module for async requests with enhanced logging and timeout handling.

This module provides an AsyncClient class that extends httpx.AsyncClient,
adding detailed logging, custom timeout defaults, and pretty-printing of HTTP headers.
"""

from __future__ import annotations

import json
from datetime import datetime

import httpx

from . import log

logger = log.get_logger(__name__)

def ppr_header_key(k):
    """Capitalize each word in a HTTP header key separated by hyphens.

    Args:
        k (str): The HTTP header key.

    Returns:
        str: The pretty-printed header key.
    """
    return '-'.join(word.capitalize() for word in k.split('-'))

def ppr_headers(headers):
    """Pretty-print HTTP headers with colored keys.

    Args:
        headers (dict): The HTTP headers to pretty-print.

    Returns:
        str: The formatted headers as a string, or None if headers is empty.
    """
    if headers:
        return '\n'.join(f'{log.cyan(ppr_header_key(k))}: {v}'
                         for (k, v) in headers.items())

class AsyncClient(httpx.AsyncClient):
    """An asynchronous HTTP client with enhanced logging, pretty-printed headers, and custom timeout handling.

    Extends httpx.AsyncClient to provide detailed request/response logging, 
    colored output for status codes, and default timeout settings suitable for internal use.
    """

    def __init__(self, timeout=None, **kwargs):
        """Initialize the AsyncClient with a custom timeout and additional keyword arguments.

        Args:
            timeout (float, optional): The read timeout in seconds. Defaults to 120.0.
            **kwargs: Additional keyword arguments passed to httpx.AsyncClient.
        """
        timeout = timeout or 120.0 # matches mako365 internal timeout
        to = httpx.Timeout(connect=10.0, read=timeout, write=10.0, pool=10.0)
        super().__init__(timeout=to, **kwargs)

    async def request(self, *args, **kwargs):
        """Send an HTTP request with enhanced logging and pretty-printed headers.

        Args:
            *args: Positional arguments for the request.
            **kwargs: Keyword arguments for the request.

        Returns:
            httpx.Response: The HTTP response object.

        Raises:
            Exception: Propagates any exception raised during the request.
        """
        method = kwargs.get("method") or (args[0] if args else "GET")
        url = kwargs.get("url") or (args[1] if len(args) > 1 else "")
        params = kwargs.get("params")
        if params:
            params = httpx.QueryParams(params) if isinstance(params, dict) else params
            url = str(httpx.URL(url).copy_merge_params(params))
        req_str = log.magenta(f'HTTP {method} {url}')
        is_debug = logger.isEnabledFor(log.DEBUG)
        is_trace = is_debug and logger.isEnabledFor(log.TRACE)

        # Handle JSON body and headers
        json_body = kwargs.pop('json', None)
        if json_body is not None:
            headers = kwargs.setdefault('headers', {})
            if not isinstance(headers, dict):
                headers = dict(headers)
                kwargs['headers'] = headers
            headers['Content-Type'] = 'application/json'
            kwargs['data'] = json.dumps(json_body)

        # Logging request
        if is_trace:
            headers_str = ppr_headers(kwargs.get('headers', {}))
            body = kwargs.get('data')
            logger.trace(
                'Sent %s:%s%s%s%s',
                req_str,
                "\n" if headers_str else "",
                headers_str or '',
                "\n" if body else "",
                body or ''
            )
        elif is_debug:
            logger.debug(f"Sent {req_str}")

        now = datetime.now()
        try:
            response = await super().request(*args, **kwargs)
            code = response.status_code
            code_str = f"HTTP {code}"
            code_color = (
                log.yellow if 400 <= code <= 599 else
                log.green if 100 <= code <= 399 else
                log.red
            )
            code_str = code_color(code_str)
            time_ms = int((datetime.now() - now).total_seconds() * 1000)
            msg = f'Got {code_str} for {req_str} in {log.cyan(time_ms)} ms'

            if is_trace:
                headers_str = ppr_headers(response.headers)
                body = response.text
                logger.trace(
                    '%s:%s%s%s%s',
                    msg,
                    "\n" if headers_str else "",
                    headers_str or '',
                    "\n" if body else "",
                    body or ''
                )
            elif is_debug:
                logger.debug(msg)
            return response
        except Exception as e:
            time_ms = int((datetime.now() - now).total_seconds() * 1000)
            msg = f'Got {log.red("HTTP ERROR")} for {req_str} in {log.cyan(time_ms)} ms'
            if is_trace:
                logger.trace(f'{msg}: {log.red(str(e))}')
            elif is_debug:
                logger.debug(msg)
            raise
