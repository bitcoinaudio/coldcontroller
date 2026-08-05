# Bitcoin Audio ColdController — Mk3 proof

This branch repurposes a retired COLDCARD Mk3 as a dedicated Bitcoin Audio control surface.

The first milestone deliberately reuses the Mk3's existing USB HID transport instead of implementing native USB MIDI.

```text
Mk3 keypad
   -> BA/1 64-byte HID report
   -> host bridge
   -> virtual MIDI port "ColdController"
   -> Ableton / other MIDI software
```

## Scope of M1

- developer-signed Mk3 firmware only
- no wallet terms/PIN flow
- OLED shows Bitcoin Audio / ColdController / USB READY
- all 12 physical key press/release transitions are mirrored to HID
- host bridge translates BA/1 reports to MIDI notes/CCs
- key `1` maps to MIDI note 36 for the end-to-end proof

Not in M1: native USB MIDI, MIDI clock, networking, secure-element identity, signing, LooperAI/Engine/NakamoTones adapters, or host-to-OLED status.

## Firmware changes

- `shared/coldcontroller.py` — BA/1 report construction, HID emission, boot screen
- `shared/numpad.py` — mirrors existing keypad transitions without consuming the normal queue
- `shared/main.py` — developer-signed firmware diverts into ColdController mode before wallet terms/PIN UX

The base is upstream `v4-legacy`, not modern Mk4/Q `master`.

## Build the Mk3 firmware

Clone recursively and select this branch:

```bash
git clone --recursive https://github.com/bitcoinaudio/coldcontroller.git
cd coldcontroller
git checkout agent/mk3-hid-poc
git submodule update --init --recursive
```

Follow the legacy firmware prerequisites in the repository root `README.md`, then:

```bash
cd stm32
make setup
make
make firmware-signed.dfu
```

Upstream provides signing key zero specifically for experimental developer firmware. A Mk3 booting developer firmware intentionally shows a warning/delay before running it.

The resulting image is:

```text
stm32/firmware-signed.dfu
```

Upgrade using the legacy Coldcard CLI flow documented upstream:

```bash
ckcc upgrade firmware-signed.dfu
```

### Expected device result

After the developer-firmware warning, the normal wallet login path should not run. The OLED should show:

```text
BITCOIN AUDIO
COLDCONTROLLER
MK3 / BA-1
USB READY
```

## Run the HID -> MIDI bridge

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r coldcontroller/requirements.txt
```

Confirm the Mk3 HID interface is visible:

```bash
python coldcontroller/bridge.py --list
```

Then start the bridge:

```bash
python coldcontroller/bridge.py
```

The bridge creates a virtual MIDI output named `ColdController` on supported macOS/Linux python-rtmidi backends.

Pressing Mk3 key `1` should print a BA/1 down/up pair and emit MIDI note 36 on channel 1 (MIDI channel value 0 internally).

## Ableton proof

1. Start `coldcontroller/bridge.py`.
2. Enable the `ColdController` MIDI input in Ableton's MIDI preferences if required by the host/backend.
3. Route/arm a MIDI track receiving from `ColdController`.
4. Press `1` on the Mk3.
5. Confirm note 36 down/up is received.

The initial mapping lives in `coldcontroller/profiles/ableton.json`.

## BA/1

See [`protocol.md`](protocol.md).

M1 report layout:

```text
byte 0      0xBA marker
byte 1      0x01 version
byte 2      0x01 key-event type
byte 3      key code
bytes 4..7  uint32 LE sequence
byte 8      1=down, 0=up
bytes 9..63 reserved
```

## Hardware and security boundary

Treat the test Mk3 as permanently retired from wallet duty.

- Do not restore or enter valuable seed material.
- Do not use Coldcard wallet software and the BA/1 bridge concurrently.
- Do not make the Mk3 the MIDI clock authority; timing stays host-side.
- Do not assume this experimental firmware is suitable for custody or signing.

## Licensing boundary

This repository is a fork of Coldcard firmware and remains subject to the upstream `COPYING-CC` terms, including its Commons Clause language. The project is currently an R&D/prototyping path. Any commercial ColdController product needs an explicit firmware licensing decision or a clean-room firmware path.

## Next milestones

- **M1:** physical keypad -> HID -> MIDI proof
- **M2:** banks/profiles and transport mappings
- **M3:** host -> OLED feedback
- **M4:** Bitcoin Audio adapters (Engine, LooperAI, NakamoTones, Band Builder)
- **M5:** evaluate native class-compliant USB MIDI
- **M6:** evaluate hardware-backed device/creator identity
