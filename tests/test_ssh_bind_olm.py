import importlib.util
import os
from pathlib import Path
import socket
import threading
import time
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location("olm_proxy", Path(__file__).resolve().parents[1] / "scripts/ssh-bind-olm.py")
proxy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(proxy)


def write_all(fd, data):
    while data:
        count = os.write(fd, data)
        data = data[count:]


def read_all(fd, slow=False):
    result = bytearray()
    while chunk := os.read(fd, 4096 if slow else 65536):
        result.extend(chunk)
        if slow:
            time.sleep(0.0001)
    return bytes(result)


class RelayTests(unittest.TestCase):
    def start_relay(self, idle_timeout=3):
        input_fd, writer = os.pipe()
        reader, output_fd = os.pipe()
        connection, peer = socket.socketpair()
        peer.settimeout(5)
        failures = []

        def run():
            try:
                proxy.relay(connection, input_fd, output_fd, idle_timeout, buffer_limit=16384)
            except Exception as error:
                failures.append(error)
            finally:
                connection.close()
                for fd in (input_fd, output_fd):
                    try:
                        os.close(fd)
                    except OSError:
                        pass

        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        self.addCleanup(peer.close)
        for fd in (reader, writer):
            self.addCleanup(self.close_fd, fd)
        return writer, reader, peer, thread, failures, output_fd

    @staticmethod
    def close_fd(fd):
        try:
            os.close(fd)
        except OSError:
            pass

    def finish(self, thread, failures):
        thread.join(5)
        self.assertFalse(thread.is_alive(), "relay did not terminate")
        self.assertEqual(failures, [])

    def test_large_bidirectional_data_with_backpressure_and_partial_output_writes(self):
        upload, download = os.urandom(1048576), os.urandom(1048576 + 137)
        writer, reader, peer, thread, failures, output_fd = self.start_relay()
        received = bytearray()
        real_write = os.write

        def partial_write(fd, data):
            return real_write(fd, data[:701] if fd == output_fd else data)

        def produce():
            write_all(writer, upload)
            os.close(writer)

        def remote():
            sender = threading.Thread(target=lambda: (peer.sendall(download), peer.shutdown(socket.SHUT_WR)))
            sender.start()
            while chunk := peer.recv(65536):
                received.extend(chunk)
            sender.join(5)

        with patch.object(proxy.os, "write", partial_write):
            producer = threading.Thread(target=produce, daemon=True)
            server = threading.Thread(target=remote, daemon=True)
            producer.start()
            server.start()
            self.assertEqual(read_all(reader, slow=True), download)
            producer.join(5)
            server.join(5)
            self.assertFalse(producer.is_alive())
            self.assertFalse(server.is_alive())
            self.assertEqual(bytes(received), upload)
            self.finish(thread, failures)

    def test_input_eof_still_allows_remote_response(self):
        writer, reader, peer, thread, failures, _ = self.start_relay()
        write_all(writer, b"request")
        os.close(writer)
        self.assertEqual(peer.recv(100), b"request")
        self.assertEqual(peer.recv(100), b"")
        peer.sendall(b"response-after-eof")
        peer.shutdown(socket.SHUT_WR)
        self.assertEqual(read_all(reader), b"response-after-eof")
        self.finish(thread, failures)

    def test_remote_eof_preserves_opposite_direction(self):
        writer, reader, peer, thread, failures, _ = self.start_relay()
        peer.sendall(b"greeting")
        peer.shutdown(socket.SHUT_WR)
        self.assertEqual(read_all(reader), b"greeting")
        write_all(writer, b"request-after-remote-eof")
        os.close(writer)
        self.assertEqual(peer.recv(100), b"request-after-remote-eof")
        self.assertEqual(peer.recv(100), b"")
        self.finish(thread, failures)

    def test_idle_connection_fails_with_bounded_timeout(self):
        writer, reader, peer, thread, failures, _ = self.start_relay(idle_timeout=0.05)
        thread.join(1)
        self.assertFalse(thread.is_alive())
        self.assertEqual(len(failures), 1)
        self.assertIsInstance(failures[0], TimeoutError)


if __name__ == "__main__":
    unittest.main()
