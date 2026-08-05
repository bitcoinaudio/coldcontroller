#!/usr/bin/env python3
"""ColdController Mk3 BA/1 HID -> virtual MIDI proof bridge."""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

import hid
import mido

COINKITE_VID = 0xD13E
CKCC_PID = 0xCC10
REPORT_SIZE = 64
MARKER = 0xBA
VERSION = 0x01
TYPE_KEY = 0x01

KEY_NAMES = {
    0: "0", 1: "1", 2: "2", 3: "3", 4: "4", 5: "5",
    6: "6", 7: "7", 8: "8", 9: "9", 10: "x", 11: "y",
}


def normalize_report(data) -> bytes:
    raw = bytes(data)
    if len(raw) == REPORT_SIZE + 1 and raw[0] == 0:
        raw = raw[1:]
    return raw


def parse_key_report(raw: bytes):
    if len(raw) < 9:
        return None
    if raw[0] != MARKER or raw[1] != VERSION or raw[2] != TYPE_KEY:
        return None

    key = KEY_NAMES.get(raw[3])
    if key is None:
        return None

    sequence = struct.unpack_from("<I", raw, 4)[0]
    state = raw[8]
    if state not in (0, 1):
        return None
    return sequence, key, bool(state)


def load_profile(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        profile = json.load(fh)
    if not isinstance(profile.get("keys"), dict):
        raise ValueError("profile must contain a 'keys' object")
    return profile


def emit_midi(port, profile: dict, key: str, pressed: bool) -> None:
    mapping = profile["keys"].get(key)
    if not mapping:
        return

    channel = int(mapping.get("channel", profile.get("channel", 0)))
    kind = mapping.get("type")

    if kind == "note":
        note = int(mapping["note"])
        velocity = int(mapping.get("velocity", profile.get("velocity", 127)))
        port.send(
            mido.Message(
                "note_on" if pressed else "note_off",
                channel=channel,
                note=note,
                velocity=velocity if pressed else 0,
            )
        )
        return

    if kind == "cc" and pressed:
        port.send(
            mido.Message(
                "control_change",
                channel=channel,
                control=int(mapping["control"]),
                value=int(mapping.get("value", 127)),
            )
        )
        return

    if kind not in ("note", "cc"):
        raise ValueError(f"unsupported mapping type for key {key!r}: {kind!r}")


def list_devices() -> int:
    matches = hid.enumerate(COINKITE_VID, CKCC_PID)
    if not matches:
        print("No COLDCARD Mk3 HID interface found.")
        return 1

    for item in matches:
        path = item.get("path")
        if isinstance(path, bytes):
            path = path.decode(errors="replace")
        print(
            f"path={path} product={item.get('product_string')} "
            f"serial={item.get('serial_number')} interface={item.get('interface_number')}"
        )
    return 0


def open_device(device_path: str | None):
    device = hid.device()
    if device_path:
        device.open_path(device_path.encode())
    else:
        device.open(COINKITE_VID, CKCC_PID)
    device.set_nonblocking(False)
    return device


def run(args) -> int:
    profile = load_profile(args.profile)
    midi_port_name = args.midi_port or profile.get("midi_port", "ColdController")

    device = open_device(args.device_path)
    try:
        with mido.open_output(midi_port_name, virtual=True) as midi_out:
            print(
                f"ColdController connected ({COINKITE_VID:04x}:{CKCC_PID:04x}); "
                f"virtual MIDI output: {midi_port_name}"
            )
            last_sequence = None

            while True:
                data = device.read(REPORT_SIZE, timeout_ms=1000)
                if not data:
                    continue

                parsed = parse_key_report(normalize_report(data))
                if parsed is None:
                    if args.verbose:
                        print(f"ignored HID report: {bytes(data).hex()}")
                    continue

                sequence, key, pressed = parsed
                if (
                    last_sequence is not None
                    and sequence != ((last_sequence + 1) & 0xFFFFFFFF)
                ):
                    print(
                        f"warning: BA/1 sequence gap {last_sequence} -> {sequence}",
                        file=sys.stderr,
                    )
                last_sequence = sequence

                print(f"seq={sequence} key={key} {'down' if pressed else 'up'}")
                emit_midi(midi_out, profile, key, pressed)
    finally:
        device.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--profile",
        type=Path,
        default=Path(__file__).resolve().parent / "profiles" / "ableton.json",
        help="mapping profile JSON",
    )
    parser.add_argument("--midi-port", help="override virtual MIDI port name")
    parser.add_argument("--device-path", help="open a specific hidapi device path")
    parser.add_argument("--list", action="store_true", help="list matching HID interfaces")
    parser.add_argument("-v", "--verbose", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.list:
        return list_devices()

    try:
        return run(args)
    except KeyboardInterrupt:
        print("\nStopped.")
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"ColdController bridge error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
