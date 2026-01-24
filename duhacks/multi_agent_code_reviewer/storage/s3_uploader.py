"""
S3 Uploader - REAL AWS S3 Integration
Utility to upload code to Amazon S3.
"""

import boto3
import os
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError, NoCredentialsError
from storage.aws_config import aws_config
from utils.logger import Logger


class S3Uploader:
    """
    Uploads code snapshots to S3.
    Complements S3Reader for complete S3 workflow.
    Supports both real AWS S3 and mock mode for testing.
    """
    
    def __init__(self, bucket_name: Optional[str] = None):
        """
        Initialize S3 uploader.
        
        Args:
            bucket_name: Optional S3 bucket name (uses config default if not provided)
        """
        self.logger = Logger("S3Uploader")
        self.bucket_name = bucket_name or aws_config.s3_bucket_name
        
        # Initialize S3 client
        self._init_s3_client()
    
    def _init_s3_client(self):
        """Initialize boto3 S3 client"""
        try:
            boto3_config = aws_config.get_boto3_config()
            
            # Create S3 client
            self.s3_client = boto3.client('s3', **boto3_config)
            
            # Verify bucket exists
            self._verify_bucket()
            
            self.use_mock = False
            self.logger.info(f"✅ S3 uploader initialized for bucket: {self.bucket_name}")
        
        except NoCredentialsError:
            self.logger.warning("⚠️ AWS credentials not found - using MOCK mode")
            self.s3_client = None
            self.use_mock = True
        
        except Exception as e:
            self.logger.warning(f"⚠️ S3 initialization failed: {e} - using MOCK mode")
            self.s3_client = None
            self.use_mock = True
    
    def _verify_bucket(self):
        """Verify bucket exists, create if auto_create is enabled"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            self.logger.info(f"✅ Bucket '{self.bucket_name}' exists and is accessible")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                if aws_config.auto_create_bucket:
                    self.logger.info(f"Bucket '{self.bucket_name}' not found, creating...")
                    self._create_bucket()
                else:
                    self.logger.error(f"❌ Bucket '{self.bucket_name}' does not exist")
                    self.logger.info("💡 Tip: Bucket should already exist. Check S3_BUCKET_NAME setting.")
                    raise ValueError(f"Bucket '{self.bucket_name}' not found")
            else:
                raise
    
    def _create_bucket(self):
        """Create S3 bucket"""
        try:
            region = aws_config.aws_region
            
            if region == 'us-east-1':
                self.s3_client.create_bucket(Bucket=self.bucket_name)
            else:
                self.s3_client.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': region}
                )
            
            self.logger.info(f"✅ Created bucket: {self.bucket_name}")
        except Exception as e:
            self.logger.error(f"❌ Failed to create bucket: {e}")
            raise
    
    def upload_directory(self, local_dir: str, analysis_id: str) -> str:
        """
        Upload directory to S3.
        
        Args:
            local_dir: Local directory path
            analysis_id: Analysis identifier for S3 path
        
        Returns:
            S3 path where files were uploaded
        """
        s3_prefix = f"{aws_config.s3_prefix}{analysis_id}/"
        s3_path = f"s3://{self.bucket_name}/{s3_prefix}"
        
        if self.use_mock:
            self.logger.warning(f"⚠️ MOCK mode - simulating upload to {s3_path}")
            return s3_path
        
        try:
            uploaded_count = 0
            skipped_count = 0
            
            self.logger.info(f"Uploading directory '{local_dir}' to {s3_path}")
            
            # Walk through directory and upload each file
            for root, dirs, files in os.walk(local_dir):
                # Skip hidden directories and common non-code directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in 
                          ['node_modules', '__pycache__', 'venv', 'env', '.git']]
                
                for file in files:
                    # Skip hidden files and non-code files
                    if file.startswith('.') or file.endswith(('.pyc', '.pyo', '.so', '.dll')):
                        skipped_count += 1
                        continue
                    
                    local_file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(local_file_path, local_dir)
                    s3_key = f"{s3_prefix}{relative_path.replace(os.sep, '/')}"
                    
                    # Check file size (skip files > 10MB)
                    file_size = os.path.getsize(local_file_path)
                    if file_size > 10 * 1024 * 1024:
                        self.logger.warning(f"⚠️ Skipping large file: {relative_path} ({file_size} bytes)")
                        skipped_count += 1
                        continue
                    
                    # Upload file
                    try:
                        self.s3_client.upload_file(
                            local_file_path,
                            self.bucket_name,
                            s3_key,
                            ExtraArgs={'ContentType': self._get_content_type(file)}
                        )
                        uploaded_count += 1
                        self.logger.debug(f"✅ Uploaded: {relative_path}")
                    
                    except Exception as e:
                        self.logger.error(f"❌ Failed to upload {relative_path}: {e}")
                        skipped_count += 1
            
            self.logger.info(f"✅ Upload complete: {uploaded_count} files uploaded, {skipped_count} skipped")
            self.logger.info(f"S3 Path: {s3_path}")
        
        except Exception as e:
            self.logger.error(f"❌ Upload failed: {e}")
            raise RuntimeError(f"Failed to upload to S3: {e}")
        
        return s3_path

    def upload_project_structure(self, local_dir: str, project_name: str, analysis_id: str) -> str:
        """
        Upload project with structured hierarchy:
        project_name/
           ├── source_code/
           ├── analysis_id/
           └── snippets/
               ├── security/
               ├── logic/
               └── quality/

        Args:
            local_dir: Local repository path
            project_name: Name of the project
            analysis_id: Unique analysis ID

        Returns:
            Base S3 path for the project
        """
        # Upload source code to a shared source folder
        s3_source_prefix = f"{project_name}/source_code/"
        source_path = f"s3://{self.bucket_name}/{s3_source_prefix}"
        
        self.logger.info(f"Uploading source code to structured path: {source_path}")
        
        # We reuse the logic but point to the new prefix
        # This iterates and uploads files to project_name/source_code/...
        self._upload_folder_contents(local_dir, s3_source_prefix)
        
        return f"s3://{self.bucket_name}/{project_name}/"

    def _upload_folder_contents(self, local_dir: str, s3_prefix: str):
        """Helper to upload folder contents to a specific S3 prefix"""
        if self.use_mock:
            return

        for root, dirs, files in os.walk(local_dir):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', '.git']]
            
            for file in files:
                if file.startswith('.') or file.endswith(('.pyc', '.pyo')):
                    continue
                
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, local_dir)
                s3_key = f"{s3_prefix}{relative_path.replace(os.sep, '/')}"
                
                try:
                    self.s3_client.upload_file(
                        local_path, 
                        self.bucket_name, 
                        s3_key,
                        ExtraArgs={'ContentType': self._get_content_type(file)}
                    )
                except Exception as e:
                    self.logger.error(f"Failed to upload {file}: {e}")

    def upload_categorized_snippets(self, snippets: Dict[str, Any], project_name: str, analysis_id: str):
        """
        Upload snippets into categorized folders.
        
        Structure:
        project_name/snippets/security/snippet_1.json
        project_name/snippets/logic/snippet_2.json
        ...
        
        Args:
            snippets: Dictionary of snippet lists {'security': [...], 'logic': [...]}
            project_name: Project name
            analysis_id: Analysis ID (for metadata linking)
        """
        import json
        from dataclasses import asdict, is_dataclass
        
        base_prefix = f"{project_name}/snippets/"
        
        for category, snippet_list in snippets.items():
            # e.g. project_name/snippets/security/
            category_prefix = f"{base_prefix}{category}/"
            
            for idx, snippet in enumerate(snippet_list):
                # Ensure snippet is a dict
                if is_dataclass(snippet):
                    data = asdict(snippet)
                elif hasattr(snippet, 'to_dict'):
                    data = snippet.to_dict()
                else:
                    data = snippet
                
                # Add metadata
                if isinstance(data, dict):
                    data['analysis_id'] = analysis_id
                
                # Create a meaningful filename or use ID
                file_name = f"{category}_snippet_{idx+1}.json"
                s3_key = f"{category_prefix}{file_name}"
                
                self.upload_json(data, s3_key)
                
        self.logger.info(f"✅ Uploaded categorized snippets to {base_prefix}")
    
    def upload_file(self, local_file: str, s3_key: str) -> str:
        """
        Upload single file to S3.
        
        Args:
            local_file: Local file path
            s3_key: S3 object key
        
        Returns:
            S3 URI
        """
        s3_uri = f"s3://{self.bucket_name}/{s3_key}"
        
        if self.use_mock:
            self.logger.warning(f"⚠️ MOCK mode - simulating upload to {s3_uri}")
            return s3_uri
        
        try:
            # Check file exists
            if not os.path.exists(local_file):
                raise FileNotFoundError(f"File not found: {local_file}")
            
            # Upload file
            self.s3_client.upload_file(
                local_file,
                self.bucket_name,
                s3_key,
                ExtraArgs={'ContentType': self._get_content_type(local_file)}
            )
            
            self.logger.info(f"✅ Uploaded file to {s3_uri}")
        
        except ClientError as e:
            self.logger.error(f"❌ File upload failed: {e}")
            raise RuntimeError(f"Failed to upload file: {e}")
        
        return s3_uri
    
    def upload_string(self, content: str, s3_key: str, content_type: str = 'text/plain') -> str:
        """
        Upload string content to S3.
        
        Args:
            content: String content to upload
            s3_key: S3 object key
            content_type: MIME type
        
        Returns:
            S3 URI
        """
        s3_uri = f"s3://{self.bucket_name}/{s3_key}"
        
        if self.use_mock:
            self.logger.warning(f"⚠️ MOCK mode - simulating upload to {s3_uri}")
            return s3_uri
        
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=content.encode('utf-8'),
                ContentType=content_type
            )
            
            self.logger.info(f"✅ Uploaded content to {s3_uri}")
        
        except ClientError as e:
            self.logger.error(f"❌ Content upload failed: {e}")
            raise RuntimeError(f"Failed to upload content: {e}")
        
        return s3_uri
    
    def delete_path(self, s3_prefix: str) -> bool:
        """
        Delete all objects under an S3 prefix.
        
        Args:
            s3_prefix: S3 prefix to delete
        
        Returns:
            True if successful
        """
        if self.use_mock:
            self.logger.warning(f"⚠️ MOCK mode - simulating delete of {s3_prefix}")
            return True
        
        try:
            # List all objects with prefix
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.bucket_name, Prefix=s3_prefix)
            
            delete_count = 0
            for page in pages:
                if 'Contents' not in page:
                    continue
                
                # Prepare delete request
                objects_to_delete = [{'Key': obj['Key']} for obj in page['Contents']]
                
                # Delete objects
                self.s3_client.delete_objects(
                    Bucket=self.bucket_name,
                    Delete={'Objects': objects_to_delete}
                )
                
                delete_count += len(objects_to_delete)
            
            self.logger.info(f"✅ Deleted {delete_count} objects from s3://{self.bucket_name}/{s3_prefix}")
            return True
        
        except Exception as e:
            self.logger.error(f"❌ Delete failed: {e}")
            return False
    
    def _get_content_type(self, filename: str) -> str:
        """
        Determine content type from filename.
        
        Args:
            filename: File name or path
        
        Returns:
            MIME type string
        """
        ext = os.path.splitext(filename)[1].lower()
        
        content_types = {
            '.py': 'text/x-python',
            '.js': 'application/javascript',
            '.java': 'text/x-java',
            '.cpp': 'text/x-c++src',
            '.c': 'text/x-csrc',
            '.h': 'text/x-chdr',
            '.cs': 'text/x-csharp',
            '.go': 'text/x-go',
            '.rs': 'text/x-rustsrc',
            '.rb': 'text/x-ruby',
            '.php': 'text/x-php',
            '.html': 'text/html',
            '.css': 'text/css',
            '.json': 'application/json',
            '.xml': 'application/xml',
            '.md': 'text/markdown',
            '.txt': 'text/plain',
            '.sh': 'application/x-sh',
            '.yml': 'text/yaml',
            '.yaml': 'text/yaml',
        }
        
        return content_types.get(ext, 'application/octet-stream')
    
    def upload_json(self, data: dict, s3_key: str) -> str:
        """
        Upload JSON object to S3.
        
        Args:
            data: Dictionary to upload as JSON
            s3_key: S3 object key
        
        Returns:
            S3 URI
        """
        import json
        json_content = json.dumps(data, indent=2)
        return self.upload_string(json_content, s3_key, content_type='application/json')
    
    def count_files_in_directory(self, directory: str) -> int:
        """
        Count total files in a directory.
        
        Args:
            directory: Directory path
        
        Returns:
            Total file count
        """
        total_files = 0
        try:
            for _, _, files in os.walk(directory):
                total_files += len(files)
        except Exception as e:
            self.logger.warning(f"Could not count files: {e}")
        
        return total_files
