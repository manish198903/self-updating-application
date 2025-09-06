# NameTag - Self-Updating Application

A self-updating Python application that demonstrates an automatic update mechanism

## Features

**Automatic Updates**

- Periodic checking for new versions
- Secure download with checksum verification
- Atomic updates (all-or-nothing)
- Automatic rollback on failure

**Security & Reliability**

- SHA256 checksum verification
- Backup creation before updates
- Comprehensive error handling
- Detailed logging

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd nametag

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Running the Update Server

Start the update server first:

```bash
# Start the update server (default: localhost:8000)
python update_server.py

# Or with custom host/port
python update_server.py --host 0.0.0.0 --port 9000
```

### 3. Running the Application

In a separate terminal, start the application:

```bash
# Start the application (connects to default server: localhost:8000)
python program.py

# Or if server is running on different host/port, set environment variable
UPDATE_SERVER_URL=http://0.0.0.0:9000 python program.py
```

### 4. Testing the Update Mechanism

To see the auto-updater in action with your running server and application:

1. **Create an update package** (in a new terminal):

   ```bash
   # This will increment the version and create an update file
   python create_update.py
   ```

2. **Watch the application logs**: Within a minute, you'll see the running application detect the new version, download it, verify the checksum, create a backup, apply the update, and restart itself with the new version.

Expected log output:

```
INFO - Checking for updates...
INFO - New version available: 1.0.16 (current: 1.0.15)
INFO - Downloading update...
INFO - Verifying checksum...
INFO - Creating backup...
INFO - Applying update...
INFO - Restarting application...
INFO - Starting NameTag Application v1.0.16
```

## Configuration

### Environment Variables

- `UPDATE_SERVER_URL`: Update server URL (default: http://localhost:8000)

### Application Settings

Edit `config.py` to modify:

- Version information
- Directory paths
- Update behavior
- Platform settings
