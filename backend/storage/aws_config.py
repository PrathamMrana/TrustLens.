"""
AWS Configuration
Centralized AWS configuration and credentials management
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from utils.logger import Logger

# Load .env file from project root - search up the directory tree
def load_env_file():
    """Find and load .env file from current or parent directories"""
    current = Path(__file__).parent
    # Search up to 5 levels up
    for _ in range(5):
        env_file = current / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            return
        current = current.parent

load_env_file()


class AWSConfig:
    """
    Manages AWS configuration and credentials.
    Supports multiple methods: environment variables, config file, IAM roles.
    """
    
    def __init__(self):
        self.logger = Logger("AWSConfig")
        self._load_config()
    
    def _load_config(self):
        """Load AWS configuration from environment or defaults"""
        
        # Helper to get env var with stripping
        def get_env(key, default=None):
            val = os.environ.get(key)
            if val is None:
                # Try lowercase version just in case
                val = os.environ.get(key.lower())
            return val.strip() if val else default

        # AWS Credentials (multiple sources)
        self.aws_access_key_id = get_env('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = get_env('AWS_SECRET_ACCESS_KEY')
        self.aws_session_token = get_env('AWS_SESSION_TOKEN')  # For temporary credentials
        
        # AWS Region
        self.aws_region = get_env('AWS_REGION', 'us-east-1')
        
        # S3 Configuration
        self.s3_bucket_name = get_env('S3_BUCKET_NAME', 'duhacks-s3-aicode')
        self.s3_prefix = get_env('S3_PREFIX', 'code-snapshots/')
        
        # Bucket creation - set to False if you have existing bucket
        auto_create = get_env('S3_AUTO_CREATE_BUCKET', 'false').lower()
        self.auto_create_bucket = auto_create == 'true'
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate AWS configuration"""
        
        # Check if credentials are provided
        if not self.aws_access_key_id or not self.aws_secret_access_key:
            self.logger.warning("⚠️ AWS credentials not found in environment variables")
            if not self.aws_access_key_id:
                self.logger.warning("   ❌ AWS_ACCESS_KEY_ID is MISSING")
            if not self.aws_secret_access_key:
                self.logger.warning("   ❌ AWS_SECRET_ACCESS_KEY is MISSING")
                
            self.logger.warning("Will attempt to use IAM role or AWS CLI configuration")
            self.logger.info("To set credentials on Render, add them to Environment Variables:")
            self.logger.info("  AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET_NAME")
        else:
            # Mask credentials for security
            masked_key = f"{self.aws_access_key_id[:4]}...{self.aws_access_key_id[-4:]}" if len(self.aws_access_key_id) > 8 else "****"
            self.logger.info(f"✅ AWS credentials loaded (ID: {masked_key}) for region: {self.aws_region}")
        
        # Log bucket info
        if self.s3_bucket_name == 'duhacks-s3-aicode' and not os.environ.get('S3_BUCKET_NAME'):
            self.logger.info(f"ℹ️ Using DEFAULT S3 Bucket: {self.s3_bucket_name}")
        else:
            self.logger.info(f"✅ S3 Bucket: {self.s3_bucket_name}")
    
    def get_boto3_config(self) -> Dict[str, Any]:
        """
        Get boto3 client configuration.
        
        Returns:
            Dictionary with boto3 configuration
        """
        config = {
            'region_name': self.aws_region
        }
        
        # Add credentials if provided
        if self.aws_access_key_id and self.aws_secret_access_key:
            config['aws_access_key_id'] = self.aws_access_key_id
            config['aws_secret_access_key'] = self.aws_secret_access_key
            
            if self.aws_session_token:
                config['aws_session_token'] = self.aws_session_token
        
        return config
    
    def get_s3_config(self) -> Dict[str, str]:
        """
        Get S3-specific configuration.
        
        Returns:
            Dictionary with S3 configuration
        """
        return {
            'bucket_name': self.s3_bucket_name,
            'prefix': self.s3_prefix,
            'region': self.aws_region
        }
    
    @property
    def use_mock(self) -> bool:
        """
        Determine if mock S3 should be used.
        
        Returns:
            True if credentials missing, False otherwise
        """
        # Use mock if no credentials and not using IAM role
        return not (self.aws_access_key_id and self.aws_secret_access_key)


# Global configuration instance
aws_config = AWSConfig()
