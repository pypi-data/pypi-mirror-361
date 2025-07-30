# Proxidize: Proxy Tester

A professional, multi-threaded proxy testing tool for HTTP and SOCKS proxies with built-in speed testing and geo-location lookup.

## Features

- 🚀 **Multi-threaded Testing**: Efficient parallel proxy testing with intelligent thread management
- 🌍 **HTTP & SOCKS5 Support**: Test both HTTP and SOCKS5 proxies seamlessly
- 📍 **Geo-location Lookup**: Get detailed location information for working proxies
- ⚡ **Speed Testing**: Built-in download speed testing using speedtest-cli
- 🎨 **Beautiful UI**: Rich terminal interface with colored output and formatted tables
- 📊 **Export Results**: Save results to CSV format for analysis
- 🛡️ **Robust Error Handling**: Graceful handling of failures and interruptions
- 🔧 **Flexible Configuration**: Command-line options and interactive prompts

## Installation

### Option 1: Using pipx (Recommended for applications)

```bash
# Install pipx if you don't have it
pip install --user pipx
pipx ensurepath

# Install proxidize_pt
pipx install proxidize_pt
```

### Option 2: Using pip with virtual environment

```bash
# Create a virtual environment
python3 -m venv proxy_tester_env
source proxy_tester_env/bin/activate  # On Windows: proxy_tester_env\Scripts\activate

# Install the package
pip install proxidize_pt
```

### Option 3: Using pip with user flag

```bash
pip install --user proxidize_pt
```

### Option 4: System-wide installation (not recommended)

```bash
pip install --break-system-packages proxidize_pt
```

### From Source

```bash
git clone https://github.com/fawaz7/Proxy-tester.git
cd Proxy-tester
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/fawaz7/Proxy-tester.git
cd Proxy-tester
cd proxy-tester
pip install -e ".[dev]"
```

## Usage

### Command Line Interface

Once installed, you can use any of these commands:

```bash
# Main command
proxidize_pt [options] <proxy_file_or_single_proxy>
```

### Basic Examples

```bash
# Test a single proxy
proxidize_pt "proxy.example.com:8080:username:password" --http

# Test proxies from a file
proxidize_pt data/proxies.txt --http --geo --speed-test

# Test SOCKS5 proxies with verbose output
proxidize_pt data/socks_proxies.txt --sock --geo -v

# Export results to CSV
proxidize_pt data/proxies.txt --http --geo -o results.csv
```

### Command Line Options

```
positional arguments:
  proxy                 Single proxy or path to proxy list file

options:
  -h, --help            show this help message and exit
  --sock                Use SOCKS5 proxy
  --http                Use HTTP proxy
  --geo                 Enable IP geolocation lookup
  --speed-test          Include download speed test
  -o OUTPUT, --output OUTPUT
                        Output file path
  -v, --verbose         Enable verbose debug output
```

### Proxy Format

Proxies should be in the format: `host:port:username:password`

Examples:

```
proxy.example.com:8080:user123:pass123
192.168.1.100:3128:admin:secret
socks.example.com:1080:sockuser:sockpass
```

### Sample Proxy Files

You can find sample proxy files in the `data/` directory:

- `working_http_proxies.txt` - Working HTTP proxies for testing
- `working_socks_proxies.txt` - Working SOCKS5 proxies for testing
- `semi_working_http_proxies.txt` - Mixed HTTP proxies for testing error handling

## Platform Support

Proxidize works on all major platforms:

- ✅ **Windows** (Windows 10, 11)
- ✅ **Linux** (Ubuntu, Debian, CentOS, etc.)
- ✅ **macOS** (10.14+)

## Requirements

- Python 3.7 or higher
- Internet connection for proxy testing
- All dependencies are automatically installed via pip

## Configuration

The tool uses intelligent defaults but can be customized via:

- Command-line arguments
- Interactive prompts
- Configuration files (coming soon)

## Output

Results are displayed in a beautiful table format and can be exported to CSV:

```
                          Proxy Test Results
┏━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┓
┃ # ┃ Proxy Type ┃ IP Address     ┃ Location                          ┃ Latency ┃ Speed     ┃ Status  ┃
┡━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━┩
│ 1 │ HTTP       │ 172.56.168.96  │ Brooklyn, New York, United States │ 966ms   │ 5.03 Mbps │ Working │
│ 2 │ SOCKS5     │ 172.58.255.34  │ College Park, Maryland, US        │ 1240ms  │ 3.2 Mbps  │ Working │
└───┴────────────┴────────────────┴───────────────────────────────────┴─────────┴───────────┴─────────┘
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have questions:

1. Check the [documentation](https://github.com/proxidize/proxy-tester/wiki)
2. Search [existing issues](https://github.com/proxidize/proxy-tester/issues)
3. Create a [new issue](https://github.com/proxidize/proxy-tester/issues/new)

## Changelog

### v1.0.0

- Initial release
- Multi-threaded proxy testing
- HTTP and SOCKS5 support
- Geo-location lookup
- Speed testing
- Beautiful terminal UI
- CSV export functionality

### Troubleshooting Installation

#### Error: "externally-managed-environment"

This error occurs on newer Python installations (especially with Homebrew on macOS). Use one of these solutions:

1. **Recommended**: Use `pipx` for application installation:

   ```bash
   pip install --user pipx
   pipx install proxidize_pt
   ```

2. **Use virtual environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install proxidize_pt
   ```

3. **User installation**:
   ```bash
   pip install --user proxidize_pt
   ```

#### PATH Issues

If you can't run `proxidize_pt` after installation:

- **With pipx**: Run `pipx ensurepath` and restart your terminal
- **With --user**: Add `~/.local/bin` (Linux/Mac) or `%APPDATA%\Python\Scripts` (Windows) to your PATH
- **With virtual environment**: Make sure the environment is activated
