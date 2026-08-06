# BA/1 — Bitcoin Audio HID control protocol

BA/1 is the smallest protocol needed to turn a COLDCARD Mk3 into a Bitcoin Audio control surface while reusing its existing 64-byte USB HID endpoint.

## Key event report

Every report is exactly 64 bytes.

| Offset | Size | Meaning |
|---|---:|---|
| 0 | 1 | marker `0xBA` |
| 1 | 1 | protocol version `0x01` |
| 2 | 1 | message type `0x01` = key event |
| 3 | 1 | key code |
| 4 | 4 | little-endian sequence number |
| 8 | 1 | state: `1` pressed, `0` released |
| 9..63 | 55 | reserved, zero in BA/1 |

### Key codes

| Code | Mk3 key |
|---:|---|
| 0..9 | `0`..`9` |
| 10 | `x` |
| 11 | `y` / confirm |

The firmware increments the sequence counter even when the HID endpoint is busy and a report cannot be written. A host can therefore detect dropped events from sequence gaps.

## Transport rule

BA/1 currently uses the Mk3 legacy firmware's existing HID IN endpoint (`VID 0xd13e`, `PID 0xcc10`). It does not change the USB descriptors or claim to be class-compliant MIDI.

Do not run a normal Coldcard USB client and the ColdController bridge against the device at the same time. M1 treats the device as a dedicated controller.

## Future message types

Reserved for later versions:

- display/status updates from host to device
- bank/profile selection
- transport state
- tempo/key/scene state
- agent/member selection
- generation/commit/cancel commands

Native USB MIDI is explicitly outside BA/1 and should be evaluated only after the HID proof is stable.
