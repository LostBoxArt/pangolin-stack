import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


watchdog = load('watchdog_test_target', 'service-watchdog.py')
diagnostics = load('diagnostics_test_target', 'check-diagnostic-trigger.py')
release = load('release_test_target', 'hermes-agent-release-check.py')


class WatchdogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.state = Path(self.temp.name) / 'state.json'
        self.trigger = Path(self.temp.name) / 'trigger.json'
        self.state_patch = mock.patch.multiple(watchdog, STATE_FILE=str(self.state), TRIGGER_FILE=str(self.trigger))
        self.state_patch.start()
        self.addCleanup(self.state_patch.stop)
        self.now = 1793100000

    def run_checks(self, checks, dry=False):
        output = io.StringIO()
        with mock.patch.object(watchdog, 'collect_checks', return_value=checks), mock.patch.object(watchdog.time, 'time', return_value=self.now), contextlib.redirect_stdout(output):
            result = watchdog.main(['--dry-run'] if dry else [])
        self.now += 60
        return result, output.getvalue()

    def test_dry_run_cannot_change_state_or_trigger(self):
        result, text = self.run_checks({'critical': False}, dry=True)
        self.assertEqual(result, 1)
        self.assertEqual(json.loads(text)['failures'], ['critical'])
        self.assertFalse(self.state.exists())
        self.assertFalse(self.trigger.exists())

    def test_healthy_normal_run_is_quiet(self):
        _, text = self.run_checks({'critical': True})
        self.assertEqual(text, '')
        self.assertEqual(json.loads(self.state.read_text())['failures'], [])

    def test_failure_threshold_dedup_diagnostic_and_recovery(self):
        self.assertEqual(self.run_checks({'critical': False})[1], '')
        self.assertIn('Service alerts', self.run_checks({'critical': False})[1])
        self.assertEqual(self.run_checks({'critical': False})[1], '')
        self.assertEqual(json.loads(self.trigger.read_text())['services'], ['critical'])
        self.trigger.unlink()  # A completed diagnostic must not trigger again each tick.
        self.assertEqual(self.run_checks({'critical': False})[1], '')
        self.assertFalse(self.trigger.exists())
        self.now += watchdog.RE_ALERT_SECONDS
        self.assertIn('Still down', self.run_checks({'critical': False})[1])
        self.assertIn('recovered', self.run_checks({'critical': True})[1])
        self.assertEqual(self.run_checks({'critical': True})[1], '')

    def test_silent_check_does_not_block_real_recovery(self):
        self.run_checks({'critical': False, 'Tailscale router': False})
        self.run_checks({'critical': False, 'Tailscale router': False})
        self.assertIn('recovered', self.run_checks({'critical': True, 'Tailscale router': False})[1])
        self.assertEqual(self.run_checks({'critical': True, 'Tailscale router': False})[1], '')

    def test_explicit_origin_does_not_fallback_to_public_dns_on_failure(self):
        with mock.patch.object(watchdog, 'curl_check', return_value=None) as curl, mock.patch.object(watchdog, '_resolve_via_upstream') as resolve:
            self.assertFalse(watchdog.http_check('https://dennisb.xyz/', [200], resolved_ip='51.195.100.11'))
            self.assertEqual(curl.call_args.kwargs['resolved_ip'], '51.195.100.11')
            resolve.assert_not_called()

    def test_residential_edge_probe_uses_public_dns_and_ssh_with_tls(self):
        ok = subprocess.CompletedProcess([], 0, '200', '')
        with mock.patch.object(watchdog, '_resolve_via_upstream', return_value='188.114.97.3'), mock.patch.object(watchdog.subprocess, 'run', return_value=ok) as run:
            self.assertTrue(watchdog.residential_landing_check())
        cmd = run.call_args.args[0]
        self.assertIn('StrictHostKeyChecking=yes', cmd)
        self.assertIn('jesus@192.168.0.12', cmd)
        self.assertIn('dennisb.xyz:443:188.114.97.3', cmd[-1])
        self.assertNotIn(' -k ', f' {cmd[-1]} ')
        with mock.patch.object(watchdog, '_resolve_via_upstream', return_value=None), mock.patch.object(watchdog.subprocess, 'run') as run:
            self.assertFalse(watchdog.residential_landing_check())
            run.assert_not_called()

    def test_collector_keeps_landing_and_dash_paths_separate(self):
        calls = []
        def http(url, expect, **kwargs):
            calls.append((url, expect, kwargs))
            return True
        with mock.patch.object(watchdog, 'ping', return_value=True), \
             mock.patch.object(watchdog, 'container_health', side_effect=lambda checks, *args: {c['container']: True for c in checks}), \
             mock.patch.object(watchdog, 'http_check', side_effect=http), \
             mock.patch.object(watchdog, 'residential_landing_check', return_value=True) as residential, \
             mock.patch.object(watchdog.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0)):
            results = watchdog.collect_checks()
        self.assertTrue(results['Public landing'])
        residential.assert_called_once()
        origin = next(x for x in calls if x[0] == 'https://dennisb.xyz/')
        self.assertEqual(origin[2]['resolved_ip'], '51.195.100.11')
        self.assertEqual(origin[1], [200])
        auth = next(x for x in calls if x[0] == 'https://dash.dennisb.xyz/')
        self.assertIn(401, auth[1])
        self.assertNotIn(200, auth[1])

    def test_public_denials_and_auth_boundary(self):
        for check in watchdog.PUBLIC:
            self.assertNotIn(403, check['expect'])
        prefix = 'https://pangolin.dennisb.xyz/auth/resource/'
        self.assertTrue(watchdog.response_matches(302, {'Location': prefix + 'test'}, [302], prefix))
        self.assertFalse(watchdog.response_matches(302, {'Location': 'https://unexpected.test/'}, [302], prefix))
        self.assertFalse(watchdog.response_matches(403, {}, [302], prefix))
        self.assertFalse(watchdog.response_matches(200, {}, [302], prefix))
        self.assertTrue(watchdog.response_matches(401, {}, [302, 401], prefix))

    def test_one_ssh_inspect_handles_missing_and_unhealthy_containers(self):
        checks = [{'name': n, 'container': n} for n in ['a', 'b', 'c', 'missing']]
        output = subprocess.CompletedProcess([], 1, '/a|running|healthy\n/b|running|none\n/c|running|unhealthy\n', '')
        with mock.patch.object(watchdog.subprocess, 'run', return_value=output) as run:
            result = watchdog.container_health(checks, '192.168.0.12')
        self.assertEqual(result, {'a': True, 'b': True, 'c': False, 'missing': False})
        run.assert_called_once()
        self.assertEqual(run.call_args.args[0][0], 'ssh')
        self.assertIn('StrictHostKeyChecking=yes', run.call_args.args[0])

    def test_transport_retry_is_bounded_and_never_retries_http_403(self):
        denied = subprocess.CompletedProcess([], 0, 'HTTP/2 403\r\n\r\n\n403', '')
        with mock.patch.object(watchdog.subprocess, 'run', return_value=denied), mock.patch.object(watchdog, '_resolve_via_upstream') as resolve:
            self.assertFalse(watchdog.http_check('https://example.test/', [200]))
            resolve.assert_not_called()
        with mock.patch.object(watchdog, 'curl_check', side_effect=[None, True]) as curl, mock.patch.object(watchdog, '_resolve_via_upstream', return_value='192.0.2.1'):
            self.assertTrue(watchdog.http_check('https://example.test/', [200]))
            self.assertEqual(curl.call_count, 2)
        with mock.patch.object(watchdog, 'curl_check', return_value=None), mock.patch.object(watchdog, '_resolve_via_upstream') as resolve:
            self.assertFalse(watchdog.http_check('http://127.0.0.1:80/', [200]))
            resolve.assert_not_called()

    def test_total_http_deadline_and_tls_verification_remain_enabled(self):
        success = subprocess.CompletedProcess([], 0, 'HTTP/2 200\r\n\r\n\n200', '')
        with mock.patch.object(watchdog.subprocess, 'run', return_value=success) as run:
            self.assertTrue(watchdog.curl_check('https://example.test/', [200], 8, True, None))
        cmd = run.call_args.args[0]
        self.assertIn('--max-time', cmd)
        self.assertEqual(cmd[cmd.index('--max-time') + 1], '8')
        self.assertNotIn('-k', cmd)
        self.assertNotIn('-L', cmd)

    def test_olm_health_probe_is_forced_to_the_tunnel_and_bypasses_proxies(self):
        success = subprocess.CompletedProcess([], 0, 'HTTP/1.1 200 OK\r\n\r\n\n200', '')
        check = next(c for c in watchdog.CLOUDNODE if c['name'] == 'Olm data path')
        self.assertEqual(check['interface'], 'olm')
        with mock.patch.object(watchdog.subprocess, 'run', return_value=success) as run:
            self.assertTrue(watchdog.http_check(check['url'], check['expect'], interface=check['interface']))
        cmd = run.call_args.args[0]
        self.assertEqual(cmd[cmd.index('--interface') + 1], 'olm')
        self.assertEqual(cmd[cmd.index('--noproxy') + 1], '*')

    def test_media_checks_follow_scryer_migration(self):
        checks = {item['name']: item['container'] for item in watchdog.RAMMUS_SSH}
        for name in ('Sonarr', 'Radarr', 'Bazarr', 'Profilarr', 'Recyclarr'):
            self.assertNotIn(name, checks)
        self.assertEqual(checks['Scryer'], 'scryer')
        for name in ('qBit', 'Prowlarr', 'Plex', 'arr-mcp'):
            self.assertIn(name, checks)
        probe = next(c for c in watchdog.PUBLIC if c['name'] == 'request.dennisb.xyz')
        self.assertEqual(probe['expect'], [200, 301, 302, 307])

    def test_removed_fileflows_is_not_monitored(self):
        self.assertFalse(any('fileflows' in str(c).lower() for c in watchdog.RAMMUS_SSH))


class DiagnosticsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.trigger = self.home / 'trigger.json'
        self.patch = mock.patch.object(diagnostics.watchdog, 'TRIGGER_FILE', str(self.trigger))
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def run_consumer(self, args=None):
        output = io.StringIO()
        with mock.patch.object(diagnostics.Path, 'home', return_value=self.home), mock.patch.object(diagnostics.watchdog, 'collect_checks', return_value={'NASUS': False}) as checks, contextlib.redirect_stdout(output):
            diagnostics.main(args or [])
        return output.getvalue(), checks

    def test_no_trigger_is_quiet(self):
        text, checks = self.run_consumer()
        self.assertEqual(text, '')
        checks.assert_not_called()

    def test_dry_run_never_consumes_or_writes(self):
        self.trigger.write_text(json.dumps({'services': ['NASUS']}))
        original = self.trigger.read_bytes()
        text, _ = self.run_consumer(['--dry-run'])
        self.assertTrue(json.loads(text)['pending'])
        self.assertEqual(self.trigger.read_bytes(), original)
        self.assertFalse((self.home / '.hermes').exists())

    def test_consume_preserves_next_trigger_and_deduplicates(self):
        processing = self.trigger.with_name(self.trigger.name + '.processing')
        processing.write_text(json.dumps({'services': ['old incident']}))
        self.trigger.write_text(json.dumps({'services': ['new incident']}))
        self.assertIn('diagnostics saved', self.run_consumer()[0])
        self.assertTrue(self.trigger.exists())
        self.assertFalse(processing.exists())
        self.assertIn('diagnostics saved', self.run_consumer()[0])
        self.assertEqual(len(list((self.home / '.hermes/diagnostics/watchdog').glob('*.json'))), 2)
        self.assertEqual(self.run_consumer()[0], '')


class ReleaseTests(unittest.TestCase):
    def test_network_failure_is_a_failed_job_without_state_write(self):
        with mock.patch.object(release, 'fetch_latest', side_effect=TimeoutError('test')), mock.patch.object(release, 'save_state') as save, contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(release.main(), 1)
        self.assertFalse(json.loads(output.getvalue())['ok'])
        save.assert_not_called()

    def test_repeat_release_check_is_idempotent_and_does_not_execute_commands(self):
        with tempfile.TemporaryDirectory() as directory, mock.patch.dict(release.os.environ, {'HERMES_HOME': directory}), mock.patch.object(release, 'fetch_latest', return_value={'tag_name': 'v-test', 'body': 'notes'}), mock.patch.object(release, 'urlopen', side_effect=TimeoutError('test')):
            with contextlib.redirect_stdout(io.StringIO()) as first:
                release.main()
            with contextlib.redirect_stdout(io.StringIO()) as second:
                release.main()
        self.assertIsNone(json.loads(first.getvalue())['previous_tag'])
        self.assertFalse(json.loads(second.getvalue())['changed'])
        self.assertEqual(json.loads(second.getvalue())['previous_tag'], 'v-test')


if __name__ == '__main__':
    unittest.main()
