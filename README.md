# SGCIronConnect

An enterprise-grade automation framework for IBM i (TN5250) terminal sessions, specifically designed for verifying **IBM FlashSystem SafeGuarded Copy** snapshot restoration.

## Overview

SGCIronConnect leverages Python, `libtmux`, and `tn5250` to provide a robust, data-driven automation engine. It allows for the verification of multiple IBM i LPARs post-snapshot restoration without the need for complex, screen-specific Python code.

## Prerequisites

The framework requires the following system binaries:
- `python3`: 3.12 or higher.
- `tmux`: To manage persistent terminal sessions.
- `tn5250`: The terminal emulator binary.

## Installation

1. **Clone the repository** (or copy the framework files).
2. **Install system dependencies**:
   ```bash
   # On Debian/Ubuntu (tn5250 is no longer available via apt)
   sudo apt-get update
   sudo apt-get install -y build-essential autoconf automake libtool libncurses5-dev libssl-dev git
   
   # Build tn5250 from source
   git clone https://github.com/tn5250/tn5250.git
   cd tn5250
   ./autogen.sh
   ./configure
   make
   sudo make install
   sudo ldconfig
   
   # Install tmux
   sudo apt-get install -y tmux
   ```
3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Web Application

The project includes a React-based web interface built with Vite for monitoring and interacting with the automation framework.

### Running the Web Application

1. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

2. **Start the development server**:
   ```bash
   npm run dev
   ```

3. **Access the application**:
   Open your browser and navigate to `http://localhost:3000` (or the network URL displayed in the terminal output). The server runs on port 3000 and is accessible from the network.

The web interface provides a visual dashboard showing terminal session status, framework operations, and system information.

## Deployment Instructions

### 1. Environment Variables
The framework can be configured via environment variables. These are used as defaults by the `Initialize Connection` keyword.

| Variable | Description | Default |
|----------|-------------|---------|
| `IBMI_HOST` | Host name or IP address | `localhost` |
| `IBMI_SSL` | Enable SSL/TLS | `True` |
| `IBMI_PORT` | Telnet port | `992` (SSL) / `23` (plain) |
| `IBMI_MODEL` | 5250 display type | `3477-FC` |
| `IBMI_MAP` | Keyboard map / Code page | `285` (UK English) |
| `IBMI_LU_NAME` | Device/LU name | `""` |
| `IBMI_USER` | Username for login | |
| `IBMI_PASSWORD` | Password for login | |

### 2. Structure
Ensure your project follows this structure:
```text
project_root/
├── framework/           # Core engine
├── config/              # YAML Screen definitions
└── tests/               # Robot Framework .robot files
```

### 2. Configuration
Define your screens in YAML located in `framework/config/`. 
Example `login.yaml`:
```yaml
login:
  screen_name: "Sign On"
  indicators:
    - "Sign On"
  fields:
    user: { tabs_to_reach: 0 }
    password: { tabs_to_reach: 1 }
```

### 3. SSL Connectivity
If your IBM i system requires SSL, ensure you set `enable_tls=True` during initialization. The system uses the standard `tn5250` SSL implementation.

## Invocation Examples

### 1. Robot Framework (Recommended)
Import the library and use high-level keywords to verify and navigate.

```robot
*** Settings ***
Library    framework.libraries.IBMiLibrary

*** Test Cases ***
Verify Storage Snapshot
    Initialize Connection    host_name=10.0.0.5    enable_tls=True
    Verify Screen            framework/config/login.yaml    login
    Type Text                user    OPERATOR
    Type Text                password    TOPSECRET
    Send Enter
    
    # Bypass optional info screen if displayed
    Handle Optional Signon Info
    
    Verify Screen            framework/config/main_menu.yaml    main
    Close Connection
```

### 2. Python API
Use the `P5250Client` directly for custom scripts.

```python
from framework.core.p5250_client import P5250Client

client = P5250Client(host_name="10.0.0.5", enable_tls=True)
client.connect()

if client.is_connected():
    client.send_text("WRKSYSSTS")
    client.send_enter()
    
    # Read text at specific coordinates
    cpu_usage = client.read_text_at_position(row=1, col=70, length=5)
    print(f"Current CPU: {cpu_usage}%")
    
client.disconnect()
```

### 3. Command Line Demo
You can run the included demo script to see a simulated workflow:
```bash
python3 demo.py
```

## Running Tests

Once deployed and configured, you can execute your Robot Framework tests using the standard `robot` command.

### 1. Simple Execution
Run a single `.robot` file from the terminal:
```bash
robot tests/verify_snapshot.robot
```

### 2. Execution with Environment Variables
You can pass connection settings directly at runtime via environment variables:
```bash
IBMI_HOST=10.0.0.5 IBMI_USER=OPERATOR robot tests/verify_snapshot.robot
```

### 3. Reporting
Robot Framework automatically generates detailed HTML reports in the current directory:
- `report.html`: High-level summary.
- `log.html`: Detailed step-by-step execution log (useful for debugging 5250 interactions).
- `output.xml`: Machine-readable results.

### 4. Continuous Integration (CI)
Integrate these tests into your CI pipeline by installing the prerequisites on your runner and executing the `robot` command as a build step.

## Security Best Practices
- Never commit passwords to YAML configurations.
- Use Robot Framework variable files or environment variables for credentials.
- Ensure `enable_tls` is used for production IBM i connections.
