"""Stream proxy: forwards ErsatzTV's MPEG-TS / HLS to clients.

Clients hit the Pi rather than ErsatzTV directly so mobile browsers avoid
CORS issues. Uses chunked iteration so the response streams in real time.
"""

from __future__ import annotations

import requests
from flask import Blueprint, Response

from . import _state

bp = Blueprint("stream", __name__)


@bp.route("/<int:ch_num>.ts")
def stream_proxy_ts(ch_num: int):
    url = f"{_state.ERSATZTV_URL}/iptv/channel/{ch_num}.ts"
    try:
        resp = requests.get(url, stream=True, timeout=10)
        return Response(
            resp.iter_content(chunk_size=64 * 1024),
            content_type=resp.headers.get("Content-Type", "video/mp2t"),
            headers={"Cache-Control": "no-cache", "Access-Control-Allow-Origin": "*"},
        )
    except Exception as e:
        print(f"Stream proxy error ch{ch_num}: {e}")
        return f"Stream error: {e}", 502


@bp.route("/<int:ch_num>.m3u8")
def stream_proxy_hls(ch_num: int):
    url = f"{_state.ERSATZTV_URL}/iptv/channel/{ch_num}.m3u8"
    try:
        resp = requests.get(url, timeout=10, allow_redirects=False)
        if resp.status_code in (301, 302):
            # ErsatzTV doesn't serve HLS; let the client fall back to .ts.
            return "HLS not available", 404
        return Response(
            resp.content,
            content_type=resp.headers.get("Content-Type", "application/vnd.apple.mpegurl"),
            headers={"Cache-Control": "no-cache", "Access-Control-Allow-Origin": "*"},
        )
    except Exception as e:
        return f"HLS error: {e}", 502
