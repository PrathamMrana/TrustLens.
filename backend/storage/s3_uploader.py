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
        DEPRECATED: Use upload_only_snippets instead.
        This method is kept for backward compatibility but doesn't upload full code.
        
        Args:
            local_dir: Local directory path (not used)
            analysis_id: Analysis identifier for S3 path
        
        Returns:
            S3 path message
        """
        self.logger.warning("⚠️ upload_directory is deprecated. Use upload_only_snippets with extracted snippets instead.")
        return f"s3://{self.bucket_name}/{aws_config.s3_prefix}{analysis_id}/"

    def upload_only_snippets(
        self,
        project_name: str,
        analysis_id: str,
        snippets: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Hardened S3 Upload: Uses analysis_id for isolation and category batching.
        Structure:
        analysis_id/project_name/
           ├── metadata.json
           └── snippets/ (Batched category files)
        """
        from datetime import datetime
        
        # Isolation: Top-level prefix is analysis_id to prevent collisions
        base_prefix = f"{analysis_id}/{project_name}".replace("//", "/")
        base_path = f"s3://{self.bucket_name}/{base_prefix}/"
        
        self.logger.info(f"🚀 Isolated S3 Upload: {base_path}")
        
        try:
            # 1. Upload metadata
            if metadata:
                metadata['analysis_id'] = analysis_id
                metadata['uploaded_at'] = datetime.utcnow().isoformat()
                metadata_key = f"{base_prefix}/metadata.json"
                self.upload_json(metadata, metadata_key)
            
            # 2. Upload categorized snippets (In batches by category)
            if snippets:
                self.upload_categorized_snippets(snippets, base_prefix, analysis_id)
            
            return base_path
        
        except Exception as e:
            self.logger.error(f"❌ Snippet upload failed: {e}")
            raise RuntimeError(f"Failed to upload snippets: {e}")

    def upload_project_structure(self, local_dir: str, project_name: str, analysis_id: str) -> str:
        """
        DEPRECATED: This method previously uploaded full source code.
        Now use upload_only_snippets instead.
        
        Args:
            local_dir: Local repository path (not used)
            project_name: Name of the project
            analysis_id: Unique analysis ID

        Returns:
            Base S3 path message
        """
        self.logger.warning("⚠️ upload_project_structure is deprecated. Use upload_only_snippets with snippets dict instead.")
        return f"s3://{self.bucket_name}/{project_name}/"



    def upload_categorized_snippets(self, snippets: Dict[str, Any], base_prefix: str, analysis_id: str):
        """
        Hardened Upload: Batch snippets by category to reduce S3 API calls.
        """
        from dataclasses import asdict, is_dataclass
        
        for category, snippet_list in snippets.items():
            if not snippet_list: continue
            
            processed_snippets = []
            for idx, snippet in enumerate(snippet_list):
                if is_dataclass(snippet):
                    data = asdict(snippet)
                elif hasattr(snippet, 'to_dict'):
                    data = snippet.to_dict()
                else:
                    data = snippet
                
                if isinstance(data, dict):
                    data['analysis_id'] = analysis_id
                processed_snippets.append(data)
            
            # Batch upload category
            s3_key = f"{base_prefix}/snippets/{category}_batch.json"
            self.upload_json(processed_snippets, s3_key)
            self.logger.info(f"✅ Batched {len(processed_snippets)} {category} snippets to S3")
    
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
