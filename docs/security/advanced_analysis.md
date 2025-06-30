# Advanced Security Analysis and Penetration Techniques

This guide covers advanced security analysis, ethical hacking, and penetration testing techniques for AI systems.

## 1. Cryptography and Data Protection

### Secure Encryption/Decryption

```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

def generate_key(password: str, salt: bytes = None) -> bytes:
    """Generate a secure encryption key from a password"""
    if salt is None:
        salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_message(message: str, key: bytes) -> bytes:
    """Encrypt a message using Fernet symmetric encryption"""
    f = Fernet(key)
    return f.encrypt(message.encode())

def decrypt_message(encrypted_message: bytes, key: bytes) -> str:
    """Decrypt a message using Fernet symmetric encryption"""
    f = Fernet(key)
    return f.decrypt(encrypted_message).decode()

# Example usage
password = "secure_password_123"
key = generate_key(password)
message = "Sensitive data to encrypt"
encrypted = encrypt_message(message, key)
decrypted = decrypt_message(encrypted, key)
```

## 2. Network Security Analysis

### Port Scanning with Python

```python
import socket
from concurrent.futures import ThreadPoolExecutor
from typing import List, Tuple

def scan_port(ip: str, port: int) -> Tuple[int, bool]:
    """Check if a port is open on the given IP"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((ip, port))
            return port, result == 0
    except Exception:
        return port, False

def port_scan(target: str, ports: List[int], max_workers: int = 100) -> None:
    """Scan multiple ports on a target IP"""
    print(f"Scanning {target}...")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(lambda p: scan_port(target, p), ports))
    
    open_ports = [port for port, is_open in results if is_open]
    if open_ports:
        print("Open ports:", ", ".join(map(str, sorted(open_ports))))
    else:
        print("No open ports found")

# Example usage
# port_scan("192.168.1.1", range(1, 1025))
```

## 3. Web Application Security

### Basic Vulnerability Scanner

```python
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

class SimpleScanner:
    def __init__(self, target_url):
        self.target_url = target_url
        self.session = requests.Session()
        self.vulnerabilities = []

    def scan_xss_vulnerabilities(self):
        """Check for potential XSS vulnerabilities in forms"""
        try:
            response = self.session.get(self.target_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for form in soup.find_all('form'):
                form_details = {
                    'action': form.get('action'),
                    'method': form.get('method', 'get').lower(),
                    'inputs': [input_tag.get('name', '') for input_tag in form.find_all('input')]
                }
                
                if form_details['inputs']:
                    self.vulnerabilities.append({
                        'type': 'XSS',
                        'form': form_details,
                        'risk': 'Medium',
                        'description': 'Potential XSS vulnerability in form submission'
                    })
                    
        except Exception as e:
            print(f"Error during XSS scan: {str(e)}")

    def run_scan(self):
        """Run all security scans"""
        print(f"Starting security scan for {self.target_url}")
        self.scan_xss_vulnerabilities()
        # Add more scan methods here
        
        if self.vulnerabilities:
            print("\nVulnerabilities found:")
            for i, vuln in enumerate(self.vulnerabilities, 1):
                print(f"\n{i}. {vuln['type']} - {vuln['risk']} Risk")
                print(f"   Description: {vuln['description']}")
        else:
            print("\nNo vulnerabilities found.")

# Example usage
# scanner = SimpleScanner("http://example.com")
# scanner.run_scan()
```

## 4. AI-Specific Security

### Model Poisoning Detection

```python
import numpy as np
from sklearn.ensemble import IsolationForest

class ModelPoisoningDetector:
    def __init__(self, contamination=0.1):
        self.detector = IsolationForest(contamination=contamination, random_state=42)
        self.is_fitted = False
    
    def fit(self, training_data):
        """Fit the detector on clean training data"""
        self.detector.fit(training_data)
        self.is_fitted = True
        return self
    
    def detect_anomalies(self, new_data, threshold=0.5):
        """Detect potential poisoned data points"""
        if not self.is_fitted:
            raise ValueError("Detector not fitted. Call fit() first.")
        
        # Get anomaly scores (the lower, the more anomalous)
        scores = -self.detector.score_samples(new_data)
        
        # Convert to binary predictions
        predictions = (scores > threshold).astype(int)
        
        return {
            'scores': scores,
            'predictions': predictions,
            'anomalous_indices': np.where(predictions == 1)[0]
        }

# Example usage
# detector = ModelPoisoningDetector()
# detector.fit(clean_training_data)
# results = detector.detect_anomalies(suspicious_data)
```

## 5. Ethical Considerations

When performing security analysis:

1. **Legal Compliance**: Always obtain proper authorization before testing
2. **Responsible Disclosure**: Report vulnerabilities to the appropriate parties
3. **Privacy Protection**: Handle any discovered data with care
4. **Documentation**: Keep detailed records of all testing activities

## Integration with AI Systems

See [Multilingual Understanding](../ai/guides/multilingual_understanding.md) for information on:
- Secure multilingual communication
- Privacy-preserving NLP
- Ethical AI practices

## References

- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [MITRE ATT&CK Framework](https://attack.mitre.org/)
- [AI Security Best Practices](https://oecd.ai/en/ai-principles)

---
*Last updated: June 30, 2025*
