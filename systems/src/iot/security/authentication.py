import hashlib
import hmac
import base64
import os
import time
import uuid
import logging
from typing import Dict, Optional, Any, Tuple

logger = logging.getLogger(__name__)

class AuthenticationManager:
    """
    Authentication manager for IoT devices and users.
    Implements various authentication methods for secure IoT communication.
    """
    def __init__(self):
        """Initialize authentication manager."""
        self.api_keys = {}  # device_id -> api_key
        self.tokens = {}  # token -> {device_id, expiry}
        self.shared_secrets = {}  # device_id -> shared_secret
        
    def register_device(self, device_id: str, shared_secret: Optional[str] = None) -> str:
        """
        Register a new device with the authentication system.
        
        Args:
            device_id: Unique device identifier
            shared_secret: Optional pre-shared secret, generated if not provided
            
        Returns:
            The device's shared secret
        """
        if not shared_secret:
            # Generate a secure random shared secret
            shared_secret = base64.b64encode(os.urandom(32)).decode('utf-8')
            
        self.shared_secrets[device_id] = shared_secret
        logger.info(f"Registered device {device_id} for authentication")
        return shared_secret
        
    def generate_api_key(self, device_id: str) -> Optional[str]:
        """
        Generate API key for a device.
        
        Args:
            device_id: Device identifier
            
        Returns:
            API key or None if device not registered
        """
        if device_id not in self.shared_secrets:
            logger.warning(f"Cannot generate API key: device {device_id} not registered")
            return None
            
        # Generate a secure API key using the shared secret
        api_key = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.api_keys[device_id] = api_key
        
        logger.info(f"Generated API key for device {device_id}")
        return api_key
        
    def verify_api_key(self, device_id: str, api_key: str) -> bool:
        """
        Verify API key for a device.
        
        Args:
            device_id: Device identifier
            api_key: API key to verify
            
        Returns:
            True if valid, False otherwise
        """
        return (device_id in self.api_keys and 
                self.api_keys[device_id] == api_key)
                
    def generate_token(self, device_id: str, ttl: int = 3600) -> Optional[str]:
        """
        Generate a temporary authentication token.
        
        Args:
            device_id: Device identifier
            ttl: Time to live in seconds (default 1 hour)
            
        Returns:
            Authentication token or None if device not registered
        """
        if device_id not in self.shared_secrets:
            logger.warning(f"Cannot generate token: device {device_id} not registered")
            return None
            
        # Generate a unique token
        token = str(uuid.uuid4())
        expiry = int(time.time()) + ttl
        
        # Store token with expiry
        self.tokens[token] = {
            'device_id': device_id,
            'expiry': expiry
        }
        
        logger.info(f"Generated token for device {device_id}, expires in {ttl} seconds")
        return token
        
    def verify_token(self, token: str) -> Optional[str]:
        """
        Verify an authentication token.
        
        Args:
            token: Token to verify
            
        Returns:
            Device ID if valid, None otherwise
        """
        if token not in self.tokens:
            return None
            
        token_data = self.tokens[token]
        
        # Check if token has expired
        if int(time.time()) > token_data['expiry']:
            # Clean up expired token
            del self.tokens[token]
            return None
            
        return token_data['device_id']
        
    def generate_hmac(self, device_id: str, message: str) -> Optional[str]:
        """
        Generate HMAC for a message using device's shared secret.
        
        Args:
            device_id: Device identifier
            message: Message to sign
            
        Returns:
            Base64-encoded HMAC or None if device not registered
        """
        if device_id not in self.shared_secrets:
            logger.warning(f"Cannot generate HMAC: device {device_id} not registered")
            return None
            
        # Generate HMAC using SHA-256
        secret = self.shared_secrets[device_id].encode('utf-8')
        signature = hmac.new(secret, message.encode('utf-8'), hashlib.sha256).digest()
        return base64.b64encode(signature).decode('utf-8')
        
    def verify_hmac(self, device_id: str, message: str, signature: str) -> bool:
        """
        Verify HMAC signature for a message.
        
        Args:
            device_id: Device identifier
            message: Original message
            signature: Base64-encoded HMAC to verify
            
        Returns:
            True if valid, False otherwise
        """
        if device_id not in self.shared_secrets:
            logger.warning(f"Cannot verify HMAC: device {device_id} not registered")
            return False
            
        expected_signature = self.generate_hmac(device_id, message)
        if not expected_signature:
            return False
            
        # Constant-time comparison to prevent timing attacks
        return hmac.compare_digest(expected_signature, signature)
        
    def cleanup_expired_tokens(self):
        """Remove all expired tokens."""
        current_time = int(time.time())
        expired_tokens = [token for token, data in self.tokens.items() 
                         if current_time > data['expiry']]
                         
        for token in expired_tokens:
            del self.tokens[token]
            
        if expired_tokens:
            logger.info(f"Cleaned up {len(expired_tokens)} expired tokens")


class SecureConnectionManager:
    """
    Manages secure connections for IoT devices.
    Handles TLS certificate management and validation.
    """
    def __init__(self, ca_cert_path: Optional[str] = None, 
                cert_dir: str = "certificates"):
        """
        Initialize secure connection manager.
        
        Args:
            ca_cert_path: Path to CA certificate
            cert_dir: Directory for certificate storage
        """
        self.ca_cert_path = ca_cert_path
        self.cert_dir = cert_dir
        self.device_certs = {}  # device_id -> certificate info
        
        # Ensure certificate directory exists
        if not os.path.exists(cert_dir):
            os.makedirs(cert_dir)
            
    def register_device_cert(self, device_id: str, cert_data: str, 
                           key_data: Optional[str] = None) -> bool:
        """
        Register device certificate.
        
        Args:
            device_id: Device identifier
            cert_data: PEM-encoded certificate data
            key_data: Optional PEM-encoded private key data
            
        Returns:
            Success status
        """
        try:
            # Save certificate to file
            cert_path = os.path.join(self.cert_dir, f"{device_id}.crt")
            with open(cert_path, 'w') as f:
                f.write(cert_data)
                
            # Save key if provided
            key_path = None
            if key_data:
                key_path = os.path.join(self.cert_dir, f"{device_id}.key")
                with open(key_path, 'w') as f:
                    f.write(key_data)
                    
            # Store certificate info
            self.device_certs[device_id] = {
                'cert_path': cert_path,
                'key_path': key_path,
                'registered_at': int(time.time())
            }
            
            logger.info(f"Registered certificate for device {device_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to register certificate for device {device_id}: {e}")
            return False
            
    def validate_device_cert(self, device_id: str) -> Tuple[bool, Optional[str]]:
        """
        Validate device certificate against CA.
        
        Args:
            device_id: Device identifier
            
        Returns:
            Tuple of (valid, error_message)
        """
        if device_id not in self.device_certs:
            return False, "Device certificate not registered"
            
        cert_path = self.device_certs[device_id]['cert_path']
        
        if not self.ca_cert_path:
            logger.warning("CA certificate path not set, skipping validation")
            return True, None
            
        # In a real implementation, this would use OpenSSL to validate
        # the certificate chain. For this example, we'll just check if
        # the files exist.
        if not os.path.exists(cert_path):
            return False, "Certificate file not found"
            
        if not os.path.exists(self.ca_cert_path):
            return False, "CA certificate file not found"
            
        logger.info(f"Validated certificate for device {device_id}")
        return True, None
        
    def get_device_cert_info(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a device certificate.
        
        Args:
            device_id: Device identifier
            
        Returns:
            Certificate information or None if not found
        """
        return self.device_certs.get(device_id)
