# Bitcoin Audio ColdController Mk3 proof-of-concept.
#
# This module is intentionally small: it reuses the Mk3's existing USB HID
# endpoint and keypad driver. It is loaded only by developer-signed firmware
# through the v4-legacy development path.

ENABLED = True

REPORT_SIZE = 64
MARKER = 0xBA
PROTOCOL_VERSION = 0x01
TYPE_KEY_EVENT = 0x01

KEY_CODES = {
    '0': 0,
    '1': 1,
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    'x': 10,
    'y': 11,
}

_sequence = 0


def _write_u32_le(buf, offset, value):
    buf[offset] = value & 0xff
    buf[offset + 1] = (value >> 8) & 0xff
    buf[offset + 2] = (value >> 16) & 0xff
    buf[offset + 3] = (value >> 24) & 0xff


def start():
    """Enter the ColdController proof mode and bring up USB HID."""
    from usb import enable_usb
    from glob import dis

    enable_usb()

    dis.clear()
    dis.text(None, 2, 'BITCOIN AUDIO')
    dis.text(None, 18, 'COLDCONTROLLER')
    dis.text(None, 34, 'MK3 / BA-1')
    dis.text(None, 50, 'USB READY')
    dis.show()


def key_event(previous_key, current_key):
    """Mirror a physical key transition to the BA/1 HID IN endpoint.

    The normal keypad queue is untouched. A failed/busy HID write is dropped;
    the sequence number still advances so the host can detect the gap.
    """
    global _sequence

    if current_key:
        key = current_key
        pressed = 1
    elif previous_key:
        key = previous_key
        pressed = 0
    else:
        return False

    key_code = KEY_CODES.get(key, None)
    if key_code is None:
        return False

    try:
        import usb
        if not usb.handler:
            return False

        report = bytearray(REPORT_SIZE)
        report[0] = MARKER
        report[1] = PROTOCOL_VERSION
        report[2] = TYPE_KEY_EVENT
        report[3] = key_code
        _write_u32_le(report, 4, _sequence)
        report[8] = pressed

        _sequence = (_sequence + 1) & 0xffffffff
        return usb.handler.dev.send(report) == REPORT_SIZE
    except Exception:
        # Key handling must never be allowed to crash because the host stopped
        # reading the HID IN endpoint or USB has not finished enumerating.
        return False
