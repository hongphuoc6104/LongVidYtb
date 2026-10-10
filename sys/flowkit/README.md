# Flow Kit — Local Backend Setup

An independent Flow Kit Backend system (FastAPI + WebSocket Server) has been configured and launched for the project.

---

## 1. Service Status & Addresses

- **FastAPI REST API**: `http://127.0.0.1:8100`
- **Swagger API Docs**: `http://127.0.0.1:8100/docs`
- **WebSocket Bridge**: `ws://127.0.0.1:9222` (connection endpoint from Chrome Extension)
- **Chrome Extension Directory**: `sys/flowkit/extension` (or `<project_root>/sys/flowkit/extension`)

---

## 2. Process Management (CLI)

Manage Flow Kit via the CLI controller script `sys/flowkit/run.py`:

```bash
# Check daemon operational status and extension connection
python3 sys/flowkit/run.py status

# Start backend in daemon mode
python3 sys/flowkit/run.py start

# Gracefully stop backend
python3 sys/flowkit/run.py stop

# Restart backend
python3 sys/flowkit/run.py restart

# View recent logs
python3 sys/flowkit/run.py logs -n 50
```

---

## 3. Chrome Extension Installation Instructions

Flow Kit requires the Chrome Extension running in the browser to relay RPC commands to `flow.google.com`:

1. Open Google Chrome.
2. Navigate to: `chrome://extensions`
3. Toggle on **Developer mode** in the top-right corner.
4. Click **Load unpacked**.
5. Select directory:
   ```
   <project_root>/sys/flowkit/extension
   ```
6. Visit `https://flow.google.com/` and log in to a Google account authorized for Google Flow.
7. Open the extension popup from the browser toolbar to activate the connection.
8. Verify connectivity using:
   ```bash
   python3 sys/flowkit/run.py status
   ```
   Upon successful connection, `Extension Status` displays `CONNECTED` (`extension_connected: true`).

---

## 4. Directory Structure `sys/flowkit`

- `run.py`: CLI controller script (start / stop / status / logs).
- `config.json`: Configuration for port, provider, and Flow Project ID.
- `extension`: Symlink pointing to the Chrome Extension Manifest V3 directory.
- `runtime/`: Isolated runtime directory containing SQLite database `flow_agent.db` and `flowkit.pid`.
- `logs/`: Complete output logs written to `flowkit.log`.
- `repo/`: Flow Kit source tree (`vendor/flowkit`).
- `.venv/`: Python 3.12 virtual environment containing required dependencies (FastAPI, Uvicorn, aiosqlite, websockets, etc.).
