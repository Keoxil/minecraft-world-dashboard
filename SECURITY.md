# Security

## Reporting a vulnerability
Please use GitHub's **private vulnerability reporting** (Security tab -> *Report a vulnerability*). Do not open a public issue for security problems.

## What the app does and does not do
- It only **reads** the Minecraft world files; it never writes to them.
- The local web server listens only on `127.0.0.1`, answers only `GET`, serves a fixed list of files, rejects unknown `Host` names (DNS-rebinding) and cross-site requests, and limits simultaneous connections.
- The optional public link uses a Cloudflare quick tunnel (outbound only). Anyone with the link can see player names and coordinates: share it only with people you trust.
- Release builds are produced by GitHub Actions from this repository, with pinned actions and a build-provenance attestation. Verify with `gh attestation verify MinecraftWorldDashboard-Setup.exe --repo Keoxil/minecraft-world-dashboard`.
- The installer is **not code-signed**, so Windows SmartScreen may warn on first run.
