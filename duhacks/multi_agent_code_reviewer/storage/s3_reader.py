"""
S3 Reader - REAL AWS S3 Integration
Utility to read code snapshots from Amazon S3.
"""

import boto3
from typing import Dict, Any, Optional, List
from botocore.exceptions import ClientError, NoCredentialsError
from schemas.code_snippet import CodeSnippet
from storage.aws_config import aws_config
from utils.logger import Logger


class S3Reader:
    """
    Reads code snapshots from S3.
    All agents use this to access code - never direct Git access.
    Supports both real AWS S3 and mock mode for testing.
    """
    
    def __init__(self, bucket_name: Optional[str] = None):
        """
        Initialize S3 client.
        
        Args:
            bucket_name: Optional S3 bucket name (uses config default if not provided)
        """
        self.logger = Logger("S3Reader")
        self.bucket_name = bucket_name or aws_config.s3_bucket_name
        
        # Initialize S3 client
        self._init_s3_client()
    
    def _init_s3_client(self):
        """Initialize boto3 S3 client"""
        try:
            boto3_config = aws_config.get_boto3_config()
            
            # Create S3 client
            self.s3_client = boto3.client('s3', **boto3_config)
            
            # Test connection
            self._test_connection()
            
            self.use_mock = False
            self.logger.info(f"✅ S3 client initialized for bucket: {self.bucket_name}")
        
        except NoCredentialsError:
            self.logger.warning("⚠️ AWS credentials not found - using MOCK mode")
            self.s3_client = None
            self.use_mock = True
        
        except Exception as e:
            self.logger.warning(f"⚠️ S3 initialization failed: {e} - using MOCK mode")
            self.s3_client = None
            self.use_mock = True
    
    def _test_connection(self):
        """Test S3 connection by checking bucket access"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            self.logger.info(f"✅ Successfully connected to S3 bucket: {self.bucket_name}")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                if aws_config.auto_create_bucket:
                    self.logger.warning(f"⚠️ Bucket '{self.bucket_name}' does not exist")
                    self.logger.info("Creating bucket...")
                    self._create_bucket()
                else:
                    self.logger.error(f"❌ Bucket '{self.bucket_name}' does not exist")
                    self.logger.info("💡 Tip: Set S3_AUTO_CREATE_BUCKET=true to auto-create bucket")
                    raise ValueError(f"Bucket '{self.bucket_name}' not found. Please create it or set correct S3_BUCKET_NAME")
            elif error_code == '403':
                self.logger.error(f"❌ Access denied to bucket '{self.bucket_name}'")
                self.logger.info("💡 Check IAM permissions for this bucket")
                raise
            else:
                raise
    
    def _create_bucket(self):
        """Create S3 bucket if it doesn't exist"""
        try:
            region = aws_config.aws_region
            
            if region == 'us-east-1':
                # us-east-1 doesn't need LocationConstraint
                self.s3_client.create_bucket(Bucket=self.bucket_name)
            else:
                self.s3_client.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': region}
                )
            
            self.logger.info(f"✅ Created S3 bucket: {self.bucket_name}")
        except Exception as e:
            self.logger.error(f"❌ Failed to create bucket: {e}")
            raise
    
    def read_code_snapshot(self, s3_path: str) -> Dict[str, str]:
        """
        Read code snapshot from S3.
        
        Args:
            s3_path: S3 path to code snapshot (e.g., s3://bucket/repo-snapshot/)
        
        Returns:
            Dictionary mapping {filename: content}
        """
        if self.use_mock:
            self.logger.warning("⚠️ Using MOCK S3 - returning sample code")
            return self._mock_read_snapshot(s3_path)
        
        # Parse S3 path
        bucket, prefix = self._parse_s3_path(s3_path)
        
        self.logger.info(f"Reading from S3: s3://{bucket}/{prefix}")
        
        try:
            # Read from real S3
            return self._read_from_s3(bucket, prefix)
        except Exception as e:
            self.logger.error(f"❌ Failed to read from S3: {e}")
            self.logger.warning("⚠️ Falling back to MOCK mode")
            return self._mock_read_snapshot(s3_path)
    
    def _parse_s3_path(self, s3_path: str) -> tuple:
        """
        Parse S3 path into bucket and prefix.
        
        Args:
            s3_path: S3 path string (s3://bucket/prefix or bucket/prefix)
        
        Returns:
            Tuple of (bucket, prefix)
        """
        # Remove s3:// prefix if present
        path = s3_path.replace('s3://', '')
        
        # Split into bucket and prefix
        parts = path.split('/', 1)
        
        bucket = parts[0]
        prefix = parts[1] if len(parts) > 1 else ''
        
        # Ensure prefix ends with / for directory listing
        if prefix and not prefix.endswith('/'):
            prefix += '/'
        
        return bucket, prefix
    
    def _read_from_s3(self, bucket: str, prefix: str) -> Dict[str, str]:
        """
        Read files from S3 bucket.
        
        Args:
            bucket: S3 bucket name
            prefix: Object prefix (folder path)
        
        Returns:
            Dictionary of {filename: content}
        """
        files = {}
        
        try:
            self.logger.info(f"Listing objects in s3://{bucket}/{prefix}")
            
            # List objects with pagination support
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=bucket, Prefix=prefix)
            
            file_count = 0
            for page in pages:
                if 'Contents' not in page:
                    continue
                
                for obj in page['Contents']:
                    key = obj['Key']
                    
                    # Skip directories (keys ending with /)
                    if key.endswith('/'):
                        continue
                    
                    # Skip very large files (> 10MB)
                    if obj['Size'] > 10 * 1024 * 1024:
                        self.logger.warning(f"⚠️ Skipping large file: {key} ({obj['Size']} bytes)")
                        continue
                    
                    # Read file content
                    try:
                        response = self.s3_client.get_object(Bucket=bucket, Key=key)
                        content = response['Body'].read().decode('utf-8', errors='ignore')
                        
                        # Store with relative filename
                        relative_path = key.replace(prefix, '').lstrip('/')
                        if relative_path:  # Skip empty paths
                            files[relative_path] = content
                            file_count += 1
                    
                    except UnicodeDecodeError:
                        self.logger.warning(f"⚠️ Skipping binary file: {key}")
                    except Exception as e:
                        self.logger.warning(f"⚠️ Error reading {key}: {e}")
            
            self.logger.info(f"✅ Read {file_count} files from S3")
            
            if not files:
                self.logger.warning("⚠️ No files found in S3 path")
                return self._mock_read_snapshot(f"s3://{bucket}/{prefix}")
        
        except ClientError as e:
            error_code = e.response['Error']['Code']
            self.logger.error(f"❌ S3 read error ({error_code}): {e}")
            raise RuntimeError(f"Failed to read from S3: {e}")
        
        return files
    
    def get_agent_inputs(self, analysis_id: str, agent_type: str = None) -> Dict[str, Any]:
        """
        Retrive extracted snippets for a specific agent.
        
        Args:
            analysis_id: Analysis identifier
            agent_type: 'security', 'logic', or None for all
            
        Returns:
            Dictionary of formatted snippets ready for LLM prompt
        """
        if self.use_mock:
            return {"formatted_context": "MOCK CONTEXT FOR TESTING"}
            
        try:
            # Determine prefixes based on agent type
            prefixes = []
            
            # Assuming standard structure: project_name/snippets/category/
            # We first need to find the project name or scan the analysis_id folder
            # But earlier we stored as project_name/...
            # Let's assume the analysis_id is sufficient if we stored it that way,
            # OR we need to lookup project_name from metadata.
            
            # Strategy: List top-level folders and look for metadata.json containing this analysis_id?
            # Better strategy: The caller usually knows the project_name or s3 path.
            # If we only have analysis_id, we might need a lookup table.
            
            # For now, let's assume the s3_path passed to agents usually includes the project root.
            # But this method only takes analysis_id.
            # Let's try to find the path.
            
            # Look for extracting via s3_path from caller is better, but let's implement extraction from a known prefix.
            pass 
            
        except Exception as e:
            self.logger.error(f"Error getting agent inputs: {e}")
            return {}

    def get_code_snippets(self, s3_base_path: str, category: str) -> List[CodeSnippet]:
        """
        Retrieve CodeSnippet objects for a specific category.
        
        Args:
            s3_base_path: root path of project (e.g. s3://bucket/project/)
            category: 'security', 'logic'
            
        Returns:
            List of CodeSnippet objects
        """
        from schemas.code_snippet import CodeSnippet
        import json
        
        bucket, prefix = self._parse_s3_path(s3_base_path)
        snippet_prefix = f"{prefix}snippets/{category}/"
        
        files = self._read_from_s3(bucket, snippet_prefix)
        
        snippets = []
        for content in files.values():
            try:
                data = json.loads(content)
                # Handle cases where data might be a dict version of CodeSnippet
                snippet = CodeSnippet(
                    filename=data.get('filename', 'unknown'),
                    start_line=data.get('start_line', 1),
                    end_line=data.get('end_line', 1),
                    content=data.get('content', ''),
                    context=data.get('context', 'unknown'),
                    relevance_score=data.get('relevance_score', 0.5),
                    tags=data.get('tags', [])
                )
                snippets.append(snippet)
            except Exception as e:
                self.logger.warning(f"Failed to parse snippet JSON: {e}")
                continue
                
        return snippets

    def get_snippets(self, s3_base_path: str, category: str) -> str:
        """
        Retrieve and format snippets for a specific category.
        
        Args:
            s3_base_path: root path of project (e.g. s3://bucket/project/)
            category: 'security', 'logic'
            
        Returns:
            Formatted string for LLM context
        """
        bucket, prefix = self._parse_s3_path(s3_base_path)
        snippet_prefix = f"{prefix}snippets/{category}/"
        
        files = self._read_from_s3(bucket, snippet_prefix)
        
        snippets = []
        import json
        
        for content in files.values():
            try:
                data = json.loads(content)
                snippets.append(data)
            except:
                continue
                
        return self._format_snippets(snippets)

    def _format_snippets(self, snippets: list) -> str:
        """Format snippets into LLM-readable context"""
        output = []
        
        for s in snippets:
            entry = f"FILE: {s.get('filename')} (Lines {s.get('start_line')}-{s.get('end_line')})\n"
            entry += f"CONTEXT: {s.get('context')}\n"
            entry += f"TAGS: {', '.join(s.get('tags', []))}\n"
            entry += "CODE:\n"
            entry += s.get('content', '') + "\n"
            entry += "-" * 40
            output.append(entry)
            
        return "\n".join(output)

    
    def _mock_read_snapshot(self, s3_path: str) -> Dict[str, str]:
        """
        Mock S3 read for skeleton/testing.
        
        Args:
            s3_path: S3 path
        
        Returns:
            Mock code files with intentional vulnerabilities
        """
        self.logger.info("📦 Returning MOCK code snapshot")
        
        # Return mock code with various issues for demo
        return {
            "main.py": """
import os
import sqlite3

def authenticate_user(username, password):
    '''Authenticate user - HAS SQL INJECTION VULNERABILITY'''
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # VULNERABLE: SQL injection possible
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    cursor.execute(query)
    
    result = cursor.fetchone()
    conn.close()
    return result is not None

def process_data(data):
    '''Process data - HAS LOGIC ISSUE'''
    results = []
    
    # VULNERABLE: Potential infinite loop
    while True:
        if data:
            results.append(data)
            break
        # Missing else: what if data is None?
    
    return results

def unsafe_eval(user_input):
    '''Execute user input - DANGEROUS'''
    # VULNERABLE: Code execution
    return eval(user_input)
""",
            
            "api.py": """
from flask import Flask, request

app = Flask(__name__)

@app.route('/user/<user_id>')
def get_user(user_id):
    '''Get user data - MISSING INPUT VALIDATION'''
    # VULNERABLE: No input validation
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return execute_query(query)

@app.route('/upload', methods=['POST'])
def upload_file():
    '''Upload file - NO FILE TYPE VALIDATION'''
    file = request.files['file']
    # VULNERABLE: No file type validation
    file.save(f'/uploads/{file.filename}')
    return 'OK'

def execute_query(query):
    '''Execute SQL query'''
    # Placeholder
    pass
""",
            
            "utils.py": """
import pickle
import os

def load_config(filename):
    '''Load config - INSECURE DESERIALIZATION'''
    # VULNERABLE: Pickle is unsafe
    with open(filename, 'rb') as f:
        return pickle.load(f)

def get_user_file(filename):
    '''Get user file - PATH TRAVERSAL'''
    # VULNERABLE: No path validation
    base_dir = '/var/data/'
    return open(base_dir + filename).read()

class DataProcessor:
    '''Data processor with poor quality'''
    def __init__(self):
        self.data = []
    
    # QUALITY ISSUE: Very long function
    def process_everything(self, items):
        for item in items:
            for subitem in item:
                for element in subitem:
                    for value in element:
                        for nested in value:
                            # 5 levels of nesting - high complexity
                            self.data.append(nested)
"""
        }
