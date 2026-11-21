#!/usr/bin/env python3
"""Open one SSH transport through Olm without changing host routing."""
import errno
import os
import select
import socket
import sys
import time


def relay(connection, input_fd=0, output_fd=1, idle_timeout=120, buffer_limit=262144):
    """Relay both directions with bounded buffers and independent EOF handling."""
    blocking = {fd: os.get_blocking(fd) for fd in (input_fd, output_fd)}
    previous_timeout = connection.gettimeout()
    to_network, to_output = bytearray(), bytearray()
    input_open = remote_open = output_open = network_write_open = True
    last_activity = time.monotonic()
    try:
        for fd in blocking:
            os.set_blocking(fd, False)
        connection.setblocking(False)
        while True:
            if not input_open and not to_network and network_write_open:
                try:
                    connection.shutdown(socket.SHUT_WR)
                except OSError as error:
                    if error.errno != errno.ENOTCONN:
                        raise
                network_write_open = False
            if not remote_open and not to_output and output_open:
                os.close(output_fd)
                output_open = False
            if not input_open and not remote_open and not to_network and not to_output:
                break
            readers, writers = [], []
            if input_open and len(to_network) < buffer_limit:
                readers.append(input_fd)
            if remote_open and len(to_output) < buffer_limit:
                readers.append(connection)
            if to_network:
                writers.append(connection)
            if to_output:
                writers.append(output_fd)
            remaining = idle_timeout - (time.monotonic() - last_activity)
            if remaining <= 0:
                raise TimeoutError("SSH transport made no progress")
            readable, writable, _ = select.select(readers, writers, [], remaining)
            for source in readable:
                try:
                    if source == input_fd:
                        chunk = os.read(input_fd, min(65536, buffer_limit - len(to_network)))
                        to_network.extend(chunk)
                        input_open = bool(chunk)
                    else:
                        chunk = connection.recv(min(65536, buffer_limit - len(to_output)))
                        to_output.extend(chunk)
                        remote_open = bool(chunk)
                    last_activity = time.monotonic()
                except BlockingIOError:
                    continue
            for target in writable:
                try:
                    pending = to_network if target is connection else to_output
                    count = connection.send(pending) if target is connection else os.write(output_fd, pending)
                    if not count:
                        raise ConnectionError("SSH transport closed during write")
                    del pending[:count]
                    last_activity = time.monotonic()
                except BlockingIOError:
                    continue
    finally:
        for fd, was_blocking in blocking.items():
            if fd != output_fd or output_open:
                os.set_blocking(fd, was_blocking)
        connection.settimeout(previous_timeout)


def main():
    if len(sys.argv) != 3:
        raise ValueError("expected HOST PORT")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
        # Binding a source address alone does not bypass Tailscale policy routing.
        connection.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, b"olm\0")
        connection.settimeout(12)
        connection.connect((sys.argv[1], int(sys.argv[2])))
        relay(connection)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as error:
        print(f"Olm SSH transport failed: {error}", file=sys.stderr)
        sys.exit(1)
