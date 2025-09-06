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

### 5. Testing Error Scenarios

#### No Updates Available

To test the scenario where no updates are available:

1. **Ensure application is up-to-date**: Run `python create_update.py` once and let the application update
2. **Watch the logs**: You'll see the application check for updates but find none:

```
INFO - Checking for updates...
INFO - Already up to date (version 1.0.16)
```

#### Checksum Verification Failure

To test checksum failure scenarios:

1. **Create an update**:

   ```bash
   python create_update.py
   ```

2. **Corrupt the zip file**:

   ```bash
   # Add some random data to corrupt the zip
   echo "corrupt data" >> updates/latest.zip
   ```

3. **Watch the application logs**: You'll see checksum verification fail and the update rejected:

```
INFO - Checking for updates...
INFO - New version available: 1.0.17 (current: 1.0.16)
INFO - Downloading update...
ERROR - Checksum verification failed for downloaded file
ERROR - Update failed: Checksum mismatch
```

4. **Clean up**: Remove the corrupted file and recreate a clean update:
   ```bash
   rm updates/latest.zip updates/latest_manifest.json
   python create_update.py
   ```

#### Update Rollback on Extraction Failure

To test automatic rollback when zip extraction fails:

1. **Create a normal update first**:

   ```bash
   python create_update.py
   ```

2. **Create a malformed zip file** that passes checksum but fails extraction:

   ```bash
   # Backup the original zip file
   cp updates/latest.zip updates/latest_backup.zip

   # Create an invalid zip file
   echo "This is not a valid zip" > updates/latest.zip

   # Get the new checksum
   sha256sum updates/latest.zip
   ```

   **Manually update the manifest**: Copy the checksum output from above and replace the "checksum" value in `updates/latest_manifest.json`

3. **Watch the application logs**: You'll see the update start, pass checksum verification, but fail during extraction and automatically rollback:

```
INFO - Checking for updates...
INFO - New version available: 1.0.17 (current: 1.0.16)
INFO - Downloading update...
INFO - Verifying checksum...
INFO - Creating backup...
INFO - Applying update...
ERROR - Failed to extract update: BadZipFile: File is not a zip file
INFO - Rolling back to previous version...
INFO - Rollback completed successfully
ERROR - Update failed: Update extraction failed
```

4. **Clean up and restore**: Remove the corrupted files and restore working state:
   ```bash
   rm updates/latest.zip updates/latest_manifest.json
   mv updates/latest_backup.zip updates/latest.zip
   python create_update.py
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
