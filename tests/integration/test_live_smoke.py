"""Live Ableton smoke tests — verify each fork feature against a running Live instance.

Requires:
    - Ableton Live running on host with the AbletonMCP Remote Script loaded
    - TCP socket reachable at $ABLETON_HOST:$ABLETON_PORT (default host.docker.internal:9877)
    - Remote Script must be the post-B10/B11/B12 version (commit 539ce69+) — older
      Remote Scripts will fail with "Unknown command" on B7/B8/B10/B11 commands

Run:
    pytest tests/integration/test_live_smoke.py -v -m integration
    # or directly:
    .venv/bin/python -m pytest tests/integration/test_live_smoke.py -v -m integration

Layered design:
    Layer 1 — surface checks: command is in dispatch (no "Unknown command" error).
              Safe to run on any session, won't touch user content.
    Layer 2 — sanity checks: command with safe params returns structured response.
              Mostly safe; may select a track/device temporarily.
    Layer 3 — end-to-end: command actually loads samples / creates tracks.
              Requires $TEST_SAMPLE_URI / $TEST_DRUM_RACK_TRACK env vars,
              skipped if not set. Will modify the Live session.

Environment variables:
    ABLETON_HOST          — defaults to host.docker.internal
    ABLETON_PORT          — defaults to 9877
    TEST_SAMPLE_URI       — a real sample URI (e.g. query:Drums#Drum%20Hits:Kick:FileId_227111)
    TEST_SAMPLE_FILENAME  — filename for B10 lookup (e.g. "505 Kick.flac")
    TEST_SAMPLE_SEARCHROOT — User_folders/_lib_ or User_folders/Splice (default Splice)
    TEST_MOUNT_FILEPATH   — host path to test B11 (e.g. /ocp/mnt/Splice/Pack/snare.flac)
"""

from __future__ import annotations

import json
import os
import socket
import time
from typing import Any

import pytest

pytestmark = pytest.mark.integration

HOST = os.getenv("ABLETON_HOST", "host.docker.internal")
PORT = int(os.getenv("ABLETON_PORT", "9877"))
SOCKET_TIMEOUT = float(os.getenv("ABLETON_TEST_TIMEOUT", "95.0"))


# ---------- Fixtures / helpers ----------


def _send(command_type: str, params: dict[str, Any] | None = None, *, timeout: float | None = None) -> dict[str, Any]:
    """Send a single command and return the parsed JSON response.

    Opens a fresh socket per call so failed commands don't poison subsequent
    ones. This matches how the MCP server currently behaves (single
    long-lived connection in practice, but each call is independent).
    """
    payload = json.dumps({"type": command_type, "params": params or {}}).encode("utf-8")
    sock = socket.create_connection((HOST, PORT), timeout=timeout or SOCKET_TIMEOUT)
    try:
        sock.sendall(payload)
        chunks: list[bytes] = []
        sock.settimeout(timeout or SOCKET_TIMEOUT)
        while True:
            chunk = sock.recv(8192)
            if not chunk:
                break
            chunks.append(chunk)
            try:
                return json.loads(b"".join(chunks).decode("utf-8"))
            except json.JSONDecodeError:
                continue
        raise RuntimeError("Connection closed before complete JSON response")
    finally:
        try:
            sock.close()
        except OSError:
            pass


@pytest.fixture(scope="session", autouse=True)
def _verify_connection() -> None:
    """Sanity check that Ableton's socket is reachable before any test runs."""
    try:
        info = _send("get_session_info", timeout=3.0)
    except (OSError, RuntimeError) as e:
        pytest.skip(f"Ableton not reachable at {HOST}:{PORT} — {e}")
    if info.get("status") != "success":
        pytest.skip(f"get_session_info failed: {info}")


# ---------- Layer 1 — surface checks (command exists in dispatch) ----------


@pytest.mark.parametrize(
    "command_type",
    [
        # Inherited from upstream (must not regress)
        "get_session_info",
        "get_track_info",
        "create_midi_track",
        "set_track_name",
        "create_clip",
        "add_notes_to_clip",
        "set_clip_name",
        "fire_clip",
        "stop_clip",
        "load_instrument_or_effect",
        "set_track_volume",
        "set_track_panning",
        # B7 — load_sample_to_simpler
        "load_sample_to_simpler",
        # B8 — Drum Rack family
        "load_sample_to_drum_pad",
        "ensure_drum_rack_on_track",
        "verify_drum_pad_loaded",
        "wait_for_load_complete",
        # B10/B11 — fork-only
        "load_browser_sample_by_name",
        "resolve_filepath_to_browser_path",
    ],
)
def test_command_in_dispatch(command_type: str) -> None:
    """Every supported command must dispatch (not return 'Unknown command')."""
    # Send with empty params — most commands will return a structured error
    # (missing required field, invalid index, etc.), but NOT "Unknown command".
    response = _send(command_type, {})
    err = (response.get("error") or "") + " " + (response.get("message") or "")
    assert "Unknown command" not in err, (
        f"Command '{command_type}' not in dispatch — Remote Script is OLD. "
        f"Got: {response!r}"
    )


# ---------- Layer 2 — sanity checks (structured response on safe params) ----------


def test_get_session_info_returns_tempo_and_tracks() -> None:
    """B2 implicitly verified — we reached the socket via $ABLETON_HOST."""
    response = _send("get_session_info")
    assert response["status"] == "success"
    result = response["result"]
    assert "tempo" in result
    assert "track_count" in result
    assert isinstance(result["track_count"], int)


def test_get_track_info_handles_group_track_guard() -> None:
    """Inherited from upstream PR #17 (a8463bf) — group track must not crash."""
    response = _send("get_session_info")
    track_count = response["result"]["track_count"]
    if track_count == 0:
        pytest.skip("No tracks in session — create at least one for this test")
    # Query track 1 (1-based per MCP convention from server.py); the Remote
    # Script handler must populate is_group_track regardless of whether the
    # track is foldable.
    response = _send("get_track_info", {"track_index": 0})
    assert response["status"] == "success"
    # is_group_track is the upstream contract from PR #17
    assert "is_group_track" in response["result"]


def test_resolve_filepath_returns_browser_root_for_supported_mount() -> None:
    """B11: known prefix maps to User_folders/* browser root."""
    response = _send("resolve_filepath_to_browser_path", {"filepath": "/ocp/mnt/_lib_"})
    assert response["status"] == "success"
    assert response["result"]["browser_path"] == "User_folders/_lib_"


def test_resolve_filepath_appends_relative_suffix() -> None:
    """B11: subpath maps to <browser_root>/<rel>."""
    response = _send("resolve_filepath_to_browser_path", {"filepath": "/ocp/mnt/Splice/Demo/sample.wav"})
    assert response["status"] == "success"
    assert response["result"]["browser_path"] == "User_folders/Splice/Demo/sample.wav"


def test_resolve_filepath_rejects_unsupported_prefix() -> None:
    """B11: paths outside mapping return typed error."""
    response = _send("resolve_filepath_to_browser_path", {"filepath": "/tmp/random.wav"})
    # The handler raises ValueError; the server marshals it as status=error.
    assert response["status"] == "error" or "unsupported_prefix" in str(response).lower()


def test_browser_user_folders_walk_does_not_close_connection() -> None:
    """B12: get_browser_items_at_path('user_folders') uses safe range iter."""
    response = _send("get_browser_items_at_path", {"path": "user_folders"})
    assert response["status"] == "success", f"user_folders walk failed: {response}"
    result = response["result"]
    assert result["name"] == "User_folders"
    assert "items" in result
    # We don't assert on item count — depends on the user's Live setup.
    # The fact we get a structured response (not a closed TCP) is the test.


def test_browser_user_folders_then_get_session_info_still_works() -> None:
    """B12: after a user_folders walk, the socket must still respond.

    This is the regression target — before B12, direct iteration of Live's
    user_folders vector could close the Live TCP server.
    """
    walk = _send("get_browser_items_at_path", {"path": "user_folders"})
    assert walk["status"] == "success"
    # Now confirm the socket is still alive by re-running session_info
    info = _send("get_session_info")
    assert info["status"] == "success"


# ---------- Layer 3 — end-to-end (modifies Live session, opt-in) ----------


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        pytest.skip(f"Set {name} to enable this end-to-end test")
    return value


def test_e2e_load_sample_to_simpler() -> None:
    """B7: load a real sample URI into a Simpler / onto a MIDI track."""
    uri = _require_env("TEST_SAMPLE_URI")
    # Use track 1 (1-based) — should be the first MIDI track in the session
    response = _send("load_sample_to_simpler", {
        "track_index": 0,  # Remote Script uses 0-based
        "item_uri": uri,
        "device_index": None,
    })
    assert response["status"] == "success", f"load_sample_to_simpler failed: {response}"
    result = response["result"]
    assert result.get("loaded") is True
    assert "item_name" in result


def test_e2e_ensure_drum_rack_then_load_then_verify() -> None:
    """B8: full Drum Rack happy path — ensure rack, load to pad, verify, wait."""
    uri = _require_env("TEST_SAMPLE_URI")

    # Create a new MIDI track with a Drum Rack (track_index=-1 means new)
    ensure = _send("ensure_drum_rack_on_track", {
        "track_index": -1,
        "name": "Sisyphus_Test_DrumRack",
        "create_if_missing": True,
    })
    assert ensure["status"] == "success", f"ensure failed: {ensure}"
    track_index = ensure["result"]["track_index"]
    rack_index = ensure["result"]["rack_device_index"]

    # Load a sample onto pad note 36 (C1, default kick pad)
    load = _send("load_sample_to_drum_pad", {
        "track_index": track_index,
        "rack_device_index": rack_index,
        "pad_note": 36,
        "item_uri": uri,
        "replace": False,
    })
    assert load["status"] == "success", f"load failed: {load}"
    assert load["result"].get("loaded") is True

    # Give Live a moment to settle the async load
    time.sleep(0.5)

    # Verify the pad has a chain
    verify = _send("verify_drum_pad_loaded", {
        "track_index": track_index,
        "rack_device_index": rack_index,
        "pad_note": 36,
        "expected_filename": "",
    })
    assert verify["status"] == "success"
    assert verify["result"].get("loaded") is True

    # Wait-for-load should also report loaded=True (chain already there)
    wait = _send("wait_for_load_complete", {
        "track_index": track_index,
        "rack_device_index": rack_index,
        "pad_note": 36,
        "max_ticks": 20,
    })
    assert wait["status"] == "success"
    assert wait["result"].get("loaded") is True


def test_e2e_load_browser_sample_by_name() -> None:
    """B10 (fork-only): name-based sample lookup on a real filename."""
    filename = _require_env("TEST_SAMPLE_FILENAME")
    search_root = os.getenv("TEST_SAMPLE_SEARCHROOT", "User_folders/Splice")

    # Need a Drum Rack to load into; ensure one exists
    ensure = _send("ensure_drum_rack_on_track", {
        "track_index": -1,
        "name": "Sisyphus_Test_B10",
        "create_if_missing": True,
    })
    assert ensure["status"] == "success"
    track_index = ensure["result"]["track_index"]
    rack_index = ensure["result"]["rack_device_index"]

    load = _send("load_browser_sample_by_name", {
        "track_index": track_index,
        "rack_device_index": rack_index,
        "pad_note": 38,  # snare pad to avoid kick collision with other tests
        "filename": filename,
        "search_root": search_root,
        "replace": False,
    })
    assert load["status"] == "success", f"B10 load failed: {load}"
    assert load["result"].get("loaded") is True
    assert load["result"].get("filename") == filename


def test_e2e_resolve_filepath_with_real_mount() -> None:
    """B11: resolve a real host filepath that exists in the mapping."""
    filepath = _require_env("TEST_MOUNT_FILEPATH")
    response = _send("resolve_filepath_to_browser_path", {"filepath": filepath})
    assert response["status"] == "success", f"B11 resolve failed: {response}"
    browser_path = response["result"]["browser_path"]
    assert browser_path.startswith("User_folders/"), (
        f"Resolved path should start with User_folders/ — got {browser_path!r}"
    )
