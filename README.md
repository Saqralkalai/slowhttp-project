```markdown
# SlowHTTPTest - Python Implementation

A Python-based tool for testing web servers against Slow HTTP DoS attacks, similar to the original `slowhttptest` tool. This implementation focuses on Slowloris attacks that keep HTTP connections open by sending partial headers slowly.

## Features

- **Slowloris Attack**: Sends HTTP headers slowly to keep connections open
- **Configurable Parameters**: Control connection count, rate, intervals, and more
- **Statistics Generation**: Export detailed attack statistics to CSV and HTML
- **Real-time Monitoring**: Verbose mode for live attack monitoring
- **Safe Testing**: Built-in timeouts and graceful shutdown

## Installation

### Prerequisites
- Python 3.6 or higher
- No external dependencies required

### Setup
```bash
# Clone or download the script
git clone https://github.com/Saqralkalai/slowhttp-project.git
cd slowhttp-project

# Make the script executable (optional)
chmod +x slowhttp_attack.py
```

Usage

Basic Command

```bash
python slowhttp_attack.py -u http://target.com -c 100
```

Full Parameter Example

```bash
python slowhttp_attack.py -H -c 2000 -g -o slowhttp -i 10 -r 200 -t GET -u http://10.0.0.1/ -x 24 -p 3 -v
```
or 

```bash
python slowhttp-attack.py -H -c 2000 -g -o slowhttp -i 10 -r 200 -t GET -u http://10.0.0.1/ -x 24 -p 3 -v
```
Command Line Arguments

Argument Description Default
-H Use Slowloris attack (slow headers) -
-c, --connections Target number of connections 50
-g Generate statistics with socket state changes -
-o, --output Output file prefix "slowhttp"
-i, --interval Interval between followup data in seconds 10
-t, --verb HTTP verb to use in request "GET"
-r, --rate Connections per second 50
-u, --url Absolute URL of target Required
-x, --max-length Max length of randomized name/value pairs 32
-p, --timeout Timeout to wait for HTTP response in seconds 5
-v, --verbose Verbose mode for detailed output -

Output Files

When using the -g flag, the tool generates:

CSV File (slowhttp.csv)

Contains timestamped connection state changes:

· Timestamp
· Connection ID
· State (CONNECTED, HEADER_SENT, ERROR, CLOSED)
· Bytes Sent
· Bytes Received

HTML File (slowhttp.html)

Formatted report with the same data as CSV, suitable for web viewing.

How It Works

Slowloris Attack Mechanism

1. Connection Establishment: Creates multiple TCP connections to the target server
2. Partial Request Send: Sends an incomplete HTTP request with headers
3. Slow Header Injection: Periodically sends additional headers to keep connections alive
4. Connection Maintenance: Maintains connections without completing the request

Technical Details

· Uses Python's socket library for low-level network operations
· Implements multi-threading for concurrent connection management
· Generates random header names/values to avoid caching
· Monitors connection states in real-time

Example Scenarios

Basic Server Testing

```bash
python slowhttp_attack.py -u http://localhost:8080 -c 50 -i 5 -v
```

Advanced Load Testing

```bash
python slowhttp_attack.py -u https://example.com -c 500 -r 100 -i 2 -g -o load_test -p 10 -v
```

Quick Verification

```bash
python slowhttp_attack.py -u http://test-server.com -c 10 -i 1 -v
```

Security Considerations

⚠️ Important Legal Notice

This tool is designed for:

· Security research and education
· Authorized penetration testing
· System hardening and vulnerability assessment

Do NOT use this tool for:

· Unauthorized testing
· Malicious attacks
· Disrupting production systems

Always ensure you have explicit permission before testing any system.

Defense Mechanisms

Web servers can protect against Slowloris attacks by:

1. Limiting Connections: Restrict connections per IP address
2. Setting Timeouts: Configure short timeouts for incomplete requests
3. Using Load Balancers: Implement rate limiting and connection management
4. Web Application Firewalls: Deploy WAFs with Slowloris protection
5. Monitoring: Implement real-time connection monitoring

Troubleshooting

Common Issues

1. Connection Refused
   · Verify target URL and port
   · Check firewall settings
   · Ensure target server is running
2. Low Success Rate
   · Increase timeout value (-p)
   · Reduce connection rate (-r)
   · Check server capacity
3. Performance Issues
   · Reduce connection count (-c)
   · Increase intervals (-i)
   · Monitor system resources

Debug Tips

· Use -v flag for detailed output
· Start with small connection counts
· Test on local servers first
· Monitor system resource usage

Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for:

· Bug fixes
· New features
· Documentation improvements
· Performance enhancements

License

This tool is provided for educational and authorized testing purposes only. Users are responsible for complying with all applicable laws and regulations.

Disclaimer

The authors are not responsible for any misuse of this tool. Use responsibly and only on systems you own or have explicit permission to test.

---

Remember: With great power comes great responsibility. Always use security tools ethically and legally.

```

This README.md file provides comprehensive documentation for your SlowHTTPTest tool, including installation instructions, usage examples, security considerations, and troubleshooting tips. It's formatted in standard Markdown and can be easily viewed on GitHub or any Markdown viewer.
