#!/usr/bin/env python3
"""Re-sign Alpine apk packages with a different key.

An apk (v2) is the concatenation of three gzip streams:

    [signature tar.gz] [control tar.gz] [data tar.gz]

This script removes the old signature segment and replaces it with one made
by the given private key, preserving the control and data segments
byte-for-byte (the .PKGINFO datahash stays valid). After re-signing, the
repository APKINDEX must be regenerated (the apk size changed).

Usage: resign.py <private-key.rsa> <apk-file>...
"""

import os
import subprocess
import sys
import tempfile
import zlib


def next_stream(data):
    """Decompress the first gzip stream; return (payload, remaining)."""
    d = zlib.decompressobj(16 + zlib.MAX_WBITS)
    return d.decompress(data), d.unused_data


def strip_signature(apk_bytes):
    """Split apk_bytes into (signature-segment, control-gz, data-gz)."""
    sig_tar, rest = next_stream(apk_bytes)   # signature stream -> control+data
    ctrl_tar, data_gz = next_stream(rest)    # control stream    -> data
    sig_gz_len = len(apk_bytes) - len(rest)
    ctrl_gz_len = len(rest) - len(data_gz)
    if not (sig_tar and ctrl_tar):
        raise ValueError("unexpected apk structure (missing segments)")
    return apk_bytes[:sig_gz_len], rest[:ctrl_gz_len], data_gz


def resign(path, privkey):
    with open(path, "rb") as f:
        apk = f.read()
    _sig, control_gz, data_gz = strip_signature(apk)

    with tempfile.TemporaryDirectory() as td:
        ctrl_path = os.path.join(td, "control.tar.gz")
        with open(ctrl_path, "wb") as f:
            f.write(control_gz)
        # abuild-sign prepends the new signature segment to the control tar
        subprocess.run(["abuild-sign", "-k", privkey, ctrl_path], check=True)
        with open(ctrl_path, "rb") as f:
            new_control = f.read()

    with open(path, "wb") as f:
        f.write(new_control + data_gz)
    print(f"re-signed {path}")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    privkey = sys.argv[1]
    for apk in sys.argv[2:]:
        resign(apk, privkey)
    return 0


if __name__ == "__main__":
    sys.exit(main())
