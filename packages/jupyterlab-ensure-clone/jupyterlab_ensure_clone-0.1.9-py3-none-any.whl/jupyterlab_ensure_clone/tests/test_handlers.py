import pytest
from tornado.httpclient import HTTPError


async def test_get_example(jp_fetch):
    with pytest.raises(HTTPError, match="HTTP 405: Method Not Allowed"):
        await jp_fetch("jupyterlab-ensure-clone")
