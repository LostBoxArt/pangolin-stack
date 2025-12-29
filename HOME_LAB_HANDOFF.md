# Handoff: Enable Remote Docker Monitoring on Nasus

**Objective:** Configure `homenode` (Home Server, 192.168.1.10) to expose its Docker API over TCP so the CloudNode can monitor its containers via the Dashboard.

**Current Status:**
- CloudNode has a secure tunnel to `homenode` (via Olm/WireGuard).
- CloudNode can ping `192.168.1.10`.
- CloudNode fails to connect to Docker API: `Connection reset by peer` on port 2375.
- This indicates Docker on `homenode` is installed but NOT configured to accept remote TCP connections.

---

## Instructions for Agent on Nasus (Asustor ADM)

Since Asustor ADM makes it difficult to modify the Docker daemon configuration directly, the best solution is to run a lightweight **proxy container**. This exposes the remote API without modifying system files.

### Solution: Deploy Docker Socket Proxy

Run the following command on `homenode` to create a bridge between the internal socket and a TCP port:

```bash
docker run -d \
  --name docker-socket-proxy \
  --restart unless-stopped \
  -p 2375:2375 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  tecnativa/docker-socket-proxy
```

### Verification

1.  Check if the container is running:
    ```bash
    docker ps | grep docker-socket-proxy
    ```
2.  Test connectivity from within `homenode`:
    ```bash
    curl http://localhost:2375/version
    ```

Once this container is running, the CloudNode will be able to connect to `http://192.168.1.10:2375` via the tunnel.

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
