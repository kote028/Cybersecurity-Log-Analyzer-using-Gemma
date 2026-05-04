import time
import random
from datetime import datetime

# Sample log templates
LOG_TEMPLATES = [
    "Failed login {count} times from {ip} for user {username}",
    "Successful login from {ip} for user {username}",
    "Multiple 404 errors from {ip} on paths: /admin, /wp-login.php, /config.php",
    "SQL injection attempt detected: ' OR '1'='1 in parameter 'id' from {ip}",
    "Unusual outbound traffic detected from internal IP {internal_ip} to external IP {ip} on port {port}",
    "Antivirus alert: Malware payload 'Trojan.Win32.Generic' blocked on host {hostname}",
    "Excessive bandwidth usage detected for user {username} from {ip}",
    "Firewall rule match: Blocked connection from {ip} to port {port} (DROP)",
    "Privilege escalation attempt: user {username} executing sudo commands repeatedly from {ip}",
    "DDoS pattern detected: 10,000+ requests per second from subnet {subnet}"
]

IP_ADDRESSES = [
    "192.168.1.10", "192.168.1.15", "10.0.0.5", "172.16.0.100",
    "45.33.22.11", "104.22.11.99", "8.8.8.8", "185.22.33.44",
    "203.0.113.5", "198.51.100.20"
]

USERNAMES = ["admin", "root", "johndoe", "guest", "service_account", "backup_user"]
HOSTNAMES = ["server-01", "db-primary", "web-node-3", "jump-host", "dev-workstation"]

def generate_log():
    template = random.choice(LOG_TEMPLATES)
    
    log = template.format(
        count=random.randint(3, 50),
        ip=random.choice(IP_ADDRESSES),
        internal_ip=f"10.0.0.{random.randint(2, 254)}",
        subnet=f"{random.choice(IP_ADDRESSES).rsplit('.', 1)[0]}.0/24",
        username=random.choice(USERNAMES),
        port=random.choice([22, 80, 443, 3306, 8080, 445]),
        hostname=random.choice(HOSTNAMES)
    )
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"[{timestamp}] {log}"

def main():
    print("Starting Real-Time Log Generator...")
    print("Writing logs to 'live_logs.txt'. Press Ctrl+C to stop.")
    
    log_file = "live_logs.txt"
    
    # Optional: Clear file on start
    with open(log_file, "w") as f:
        f.write("")
        
    try:
        while True:
            log_entry = generate_log()
            print(f"Generated: {log_entry}")
            
            with open(log_file, "a") as f:
                f.write(log_entry + "\n")
                
            # Wait for a random time between 2 and 8 seconds
            time.sleep(random.uniform(2.0, 8.0))
            
    except KeyboardInterrupt:
        print("\nLog generation stopped.")

if __name__ == "__main__":
    main()
