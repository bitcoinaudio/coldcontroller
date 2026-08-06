# ColdController

> [!CAUTION]
> **This fork is not a production COLDCARD wallet project.**
>
> `bitcoinaudio/coldcontroller` exists to repurpose retired COLDCARD hardware as an experimental physical control surface for Bitcoin Audio. Any device used with ColdController firmware must be treated as **non-wallet development hardware**. Do not place Bitcoin, seed phrases, private keys, or other valuable wallet material on it.

## Purpose of this fork

ColdController explores reuse of the COLDCARD's keypad, OLED, USB interface, microcontroller, microSD slot, and related hardware for music and Bitcoin Audio control.

The first target is a retired **COLDCARD Mk3**. The first end-to-end milestone is intentionally small:

```text
Mk3 keypad
    -> BA/1 USB HID
    -> ColdController host bridge
    -> virtual MIDI
    -> Ableton / Bitcoin Audio
```

Possible later work includes OLED feedback, control banks, transport and loop controls, OSC/API adapters, NakamoTones and Band Builder integration, and evaluation of native USB MIDI.

## Status

**Experimental / R&D. Not production. Not a wallet.**

Mk3 ColdController development is based on the upstream **`v4-legacy`** firmware line. The fork's `master` branch is retained primarily as an upstream/default reference and is **not the implementation base for Mk3 ColdController firmware**.

Current physical definition of done:

```text
press Mk3 key 1
    -> BA/1 HID key-down/key-up reports
    -> coldcontroller/bridge.py
    -> virtual MIDI port "ColdController"
    -> MIDI note 36 visible in Ableton
```

Until that path is proven on physical hardware, firmware changes should be treated as proof-of-concept work.

## Agent and contributor contract

If you are an automated coding agent or contributor working in this repository, these are project constraints:

1. **Do not treat this fork as a production hardware wallet.** Its purpose is hardware repurposing for Bitcoin Audio.
2. **Do not restore wallet behavior as a "fix" to ColdController mode.** Bypassing wallet terms, PIN, seed, and transaction UX in developer-signed ColdController builds is intentional.
3. **Never use real secrets for testing.** Do not add, request, or load valuable seeds, PINs, private keys, PSBTs, or funds.
4. **For Mk3 work, branch from `v4-legacy`.** Do not blindly reset or merge the ColdController implementation to upstream `master`.
5. **Preserve the existing bootloader/security boundary.** ColdController uses the upstream developer-signing mechanism; no bootloader bypass, glitching, or secure-boot defeat is part of this project.
6. **Reuse existing Mk3 hardware paths first.** The current proof intentionally reuses the 64-byte USB HID interface and existing debounced membrane-keypad path.
7. **Keep musical timing host-side.** ColdController is a control surface, not the authoritative MIDI clock or distributed jam clock.
8. **Native USB MIDI is not M1.** Prove HID -> host bridge -> MIDI first.
9. **Keep Bitcoin Audio additions clearly scoped.** Prefer `coldcontroller/` and small, obvious firmware hooks over broad rewrites of inherited wallet code.
10. **Do not make production-security claims about this fork.** Documentation, issues, PRs, and code comments should consistently describe it as experimental repurposing work.
11. **Respect upstream licensing.** Inherited Coldcard source remains subject to `COPYING-CC`. Any commercial firmware product based substantially on it requires a separate licensing or clean-room decision.

A useful rule for agents: **if a proposed change makes the device behave more like a production wallet instead of more like a Bitcoin Audio controller, it is probably outside this fork's intended scope.**

## Branch model

- `master` — upstream/default reference line; not the Mk3 ColdController implementation base.
- `v4-legacy` — upstream legacy Mk2/Mk3 firmware base.
- ColdController feature branches — Mk3 work should normally branch from `v4-legacy`.

The active proof-of-concept branch is currently `agent/mk3-hid-poc`.

## ColdController-specific code

On ColdController development branches, project-specific files live primarily under:

```text
coldcontroller/
    README.md
    protocol.md
    bridge.py
    requirements.txt
    profiles/

shared/coldcontroller.py
```

`coldcontroller/` contains the BA/1 protocol, host bridge, profiles, and project documentation. Small hooks under `shared/` connect the inherited Mk3 keypad, USB, display, and boot flow to controller mode.

## Safety boundary

ColdController test units should be labeled and treated as **retired wallets**.

Never:

- load a valuable seed phrase onto a ColdController test device;
- use it to custody Bitcoin;
- assume experimental firmware retains production wallet security properties;
- present a ColdController build as an official Coinkite/COLDCARD product;
- use production-wallet behavior as an acceptance criterion for this fork.

Acceptance criteria for this project are controller behaviors: boot, display, keypad input, USB transport, MIDI/OSC/API translation, feedback, and Bitcoin Audio integration.

## Upstream origin

This repository is a fork of `Coldcard/firmware` so we can retain the Mk3 hardware support, bootloader compatibility, simulator/build tooling, and developer-signing path needed to experiment on real hardware.

Coldcard and the inherited firmware are products/source of Coinkite Inc. ColdController is an independent Bitcoin Audio hardware-repurposing experiment and is not an official Coinkite product.

For original production-wallet documentation, current security guidance, and current COLDCARD firmware, refer to the upstream `Coldcard/firmware` repository and Coinkite documentation. Upstream copyright and license notices remain authoritative for inherited files.

## Mk3 development starting point

```bash
git clone --recursive https://github.com/bitcoinaudio/coldcontroller.git
cd coldcontroller
git checkout agent/mk3-hid-poc
git submodule update --init --recursive

cd stm32
make setup
make
make firmware-signed.dfu
```

The resulting developer-signed image is **experimental firmware**. Read `coldcontroller/README.md` before flashing hardware.
