#!/usr/bin/env python3
"""Funniest Time Machine Warning Label — make.fun bounty entry.

Writes a single warning label for a time machine to /output/entry.txt.
Deterministic: no randomness, no network, no reads outside this repo.
"""

import hashlib
import os
import sys

ENTRY = (
    "WARNING: Do not kill your grandfather. "
    "He is the only one who knows how this machine works."
)

OUTPUT_PATH = "/output/entry.txt"

MAX_LENGTH = 120


def validate_entry(text: str) -> str:
    """Validate the label against the competition gate.

    Rules: 1-120 characters, valid UTF-8, not only whitespace,
    and no control characters. Raises ValueError on failure.
    """
    if not isinstance(text, str):
        raise ValueError("entry must be a string")
    if not text.strip():
        raise ValueError("entry must not be empty or only whitespace")
    if len(text) > MAX_LENGTH:
        raise ValueError(
            f"entry is {len(text)} characters, over the {MAX_LENGTH} limit"
        )
    # Must round-trip as UTF-8.
    text.encode("utf-8")
    # No C0/C1 control characters (allow none here; a warning label
    # has no legitimate need for them). TAB/LF/CR are also rejected:
    # the label is a single line of plain text.
    for ch in text:
        code = ord(ch)
        if code < 0x20 or 0x7F <= code <= 0x9F:
            raise ValueError(
                f"entry contains control character U+{code:04X}"
            )
    if "\uFFFD" in text:
        raise ValueError("entry contains U+FFFD replacement character")
    # Lone surrogates can never be encoded as valid UTF-8; reject them
    # explicitly rather than relying on the encode() above.
    for ch in text:
        code = ord(ch)
        if 0xD800 <= code <= 0xDFFF:
            raise ValueError(f"entry contains lone surrogate U+{code:04X}")
    # Invisible format characters (zero-width space/joiners, BOM, etc.)
    # would silently change what the judge sees; a warning label has
    # no legitimate use for them.
    invisible = {
        0x200B,  # ZERO WIDTH SPACE
        0x200C,  # ZERO WIDTH NON-JOINER
        0x200D,  # ZERO WIDTH JOINER
        0x200E,  # LEFT-TO-RIGHT MARK
        0x200F,  # RIGHT-TO-LEFT MARK
        0xFEFF,  # ZERO WIDTH NO-BREAK SPACE / BOM
    }
    for ch in text:
        if ord(ch) in invisible:
            raise ValueError(
                f"entry contains invisible format character U+{ord(ch):04X}"
            )
    return text


def write_entry(path: str = OUTPUT_PATH) -> str:
    """Validate the label and write it to path. Returns the sha256 hex."""
    label = validate_entry(ENTRY)
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    data = label.encode("utf-8")
    with open(path, "wb") as fh:
        fh.write(data)
    return hashlib.sha256(data).hexdigest()


def self_check(path: str = OUTPUT_PATH, expected_hash: str = "") -> None:
    """Re-read the written file and re-verify content and hash."""
    with open(path, "rb") as fh:
        data = fh.read()
    text = data.decode("utf-8")
    validate_entry(text)
    if text != ENTRY:
        raise ValueError("written file does not match the entry constant")
    actual_hash = hashlib.sha256(data).hexdigest()
    if expected_hash and actual_hash != expected_hash:
        raise ValueError(
            f"hash mismatch: expected {expected_hash}, got {actual_hash}"
        )


def main() -> int:
    digest = write_entry()
    self_check(expected_hash=digest)
    print(f"Wrote {OUTPUT_PATH} ({len(ENTRY)} chars, sha256 {digest})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
