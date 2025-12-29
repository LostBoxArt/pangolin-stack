# Handoff: Enable Remote Docker Monitoring on Nasus

**Objective:** Configure `homenode` (Home Server, 192.168.1.10) to expose its Docker API over TCP so the CloudNode can monitor its containers via the Dashboard.

**Current Status:**
- CloudNode has a secure tunnel to `homenode` (via Olm/WireGuard).
- CloudNode can ping `192.168.1.10`.
- CloudNode fails to connect to Docker API: `Connection reset by peer` on port 2375.
- This indicates Docker on `homenode` is installed but NOT configured to accept remote TCP connections.

---

## Instructions for Agent on Nasus

Please perform the following steps on the `homenode` server:

### 1. Configure Docker Daemon to Expose TCP Port

You need to add the TCP socket to the Docker configuration. Check if `/etc/docker/daemon.json` exists.

**Option A: If using `daemon.json` (Recommended)**

1.  Edit `/etc/docker/daemon.json`:
    ```json
    {
      "hosts": ["unix:///var/run/docker.sock", "tcp://0.0.0.0:2375"]
    }
    ```
    *Note: Keep any existing settings in the JSON file. If `hosts` key already exists, just add the tcp socket.*

**Option B: If using systemd override**

If `daemon.json` cannot be used (e.g., conflicting with systemd flags), configure via systemd:

1.  Create/Edit override file:
    ```bash
    sudo mkdir -p /etc/systemd/system/docker.service.d/
    sudo nano /etc/systemd/system/docker.service.d/override.conf
    ```
2.  Add the following:
    ```ini
    [Service]
    ExecStart=
    ExecStart=/usr/bin/dockerd -H fd:// -H tcp://0.0.0.0:2375
    ```

### 2. Restart Docker Service

Apply the changes:

```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

### 3. Verify Configuration

1.  Check if port 2375 is listening:
    ```bash
    sudo netstat -tulpn | grep 2375
    # OR
    ss -tulpn | grep 2375
    ```
2.  Test local access:
    ```bash
    curl http://localhost:2375/version
    ```

### Security Note
Since `homenode` is behind a secure VPN/WireGuard tunnel (not exposed to the public internet) and only accessible via the trusted tunnel interface, exposing unencrypted Docker socket on port 2375 is acceptable for this internal monitoring use case.
