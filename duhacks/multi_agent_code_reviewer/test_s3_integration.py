"""
Test AWS S3 Integration
Quick test to verify S3 is working
"""

from storage.s3_reader import S3Reader
from storage.s3_uploader import S3Uploader
from storage.aws_config import aws_config
import tempfile
import os
import shutil


def test_configuration():
    """Test AWS configuration"""
    print("\n" + "="*60)
    print("1️⃣ Testing AWS Configuration")
    print("="*60)
    
    print(f"AWS Region: {aws_config.aws_region}")
    print(f"S3 Bucket: {aws_config.s3_bucket_name}")
    print(f"S3 Prefix: {aws_config.s3_prefix}")
    
    if aws_config.aws_access_key_id:
        print(f"Access Key: {aws_config.aws_access_key_id[:4]}...{aws_config.aws_access_key_id[-4:]}")
        print("✅ Credentials found")
    else:
        print("⚠️ No credentials - MOCK mode will be used")
    
    print(f"Use Mock: {aws_config.use_mock}")


def test_s3_upload():
    """Test S3 upload functionality"""
    print("\n" + "="*60)
    print("2️⃣ Testing S3 Upload")
    print("="*60)
    
    # Create temporary directory with test files
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create sample Python file
        test_file1 = os.path.join(temp_dir, 'main.py')
        with open(test_file1, 'w') as f:
            f.write('print("Hello from S3 test!")\n')
        
        # Create sample JavaScript file
        test_file2 = os.path.join(temp_dir, 'app.js')
        with open(test_file2, 'w') as f:
            f.write('console.log("Testing S3 integration");\n')
        
        # Create subdirectory
        sub_dir = os.path.join(temp_dir, 'utils')
        os.makedirs(sub_dir)
        
        test_file3 = os.path.join(sub_dir, 'helper.py')
        with open(test_file3, 'w') as f:
            f.write('def test():\n    return "S3 works!"\n')
        
        print(f"Created test directory: {temp_dir}")
        print(f"Files created: 3")
        
        # Upload to S3
        uploader = S3Uploader()
        s3_path = uploader.upload_directory(temp_dir, 'test-integration')
        
        print(f"\n✅ Upload completed!")
        print(f"S3 Path: {s3_path}")
        
        return s3_path
    
    except Exception as e:
        print(f"\n❌ Upload failed: {e}")
        return None
    
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
        print(f"Cleaned up temp directory")


def test_s3_read(s3_path):
    """Test S3 read functionality"""
    print("\n" + "="*60)
    print("3️⃣ Testing S3 Read")
    print("="*60)
    
    if not s3_path:
        print("⚠️ No S3 path provided, skipping read test")
        return
    
    try:
        reader = S3Reader()
        files = reader.read_code_snapshot(s3_path)
        
        print(f"\n✅ Read completed!")
        print(f"Files found: {len(files)}")
        
        for filename, content in files.items():
            print(f"\n📄 {filename}:")
            print(f"   Size: {len(content)} bytes")
            print(f"   Preview: {content[:50]}...")
        
        return True
    
    except Exception as e:
        print(f"\n❌ Read failed: {e}")
        return False


def test_single_file_upload():
    """Test single file upload"""
    print("\n" + "="*60)
    print("4️⃣ Testing Single File Upload")
    print("="*60)
    
    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a test file for S3 integration\n")
        f.write("Testing single file upload\n")
        temp_file = f.name
    
    try:
        uploader = S3Uploader()
        s3_uri = uploader.upload_file(temp_file, 'test-files/single-test.txt')
        
        print(f"✅ File uploaded!")
        print(f"S3 URI: {s3_uri}")
        
        return True
    
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False
    
    finally:
        os.unlink(temp_file)


def test_string_content():
    """Test string content upload"""
    print("\n" + "="*60)
    print("5️⃣ Testing String Content Upload")
    print("="*60)
    
    try:
        content = """
# Test Configuration
{
    "version": "1.0",
    "test": true,
    "s3_integration": "working"
}
"""
        
        uploader = S3Uploader()
        s3_uri = uploader.upload_string(
            content,
            'test-files/config.json',
            content_type='application/json'
        )
        
        print(f"✅ Content uploaded!")
        print(f"S3 URI: {s3_uri}")
        
        return True
    
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False


def main():
    """Run all S3 integration tests"""
    print("\n" + "🚀"*30)
    print("AWS S3 INTEGRATION TEST SUITE")
    print("🚀"*30)
    
    # Test 1: Configuration
    test_configuration()
    
    # Test 2: Directory upload
    s3_path = test_s3_upload()
    
    # Test 3: Read from S3
    test_s3_read(s3_path)
    
    # Test 4: Single file upload
    test_single_file_upload()
    
    # Test 5: String content upload
    test_string_content()
    
    # Summary
    print("\n" + "="*60)
    print("✅ TEST SUITE COMPLETED")
    print("="*60)
    
    if aws_config.use_mock:
        print("\n⚠️ MOCK MODE WAS USED")
        print("To use real S3:")
        print("  1. Set AWS credentials (see S3_INTEGRATION_GUIDE.md)")
        print("  2. Run this test again")
    else:
        print("\n✅ REAL S3 WAS USED")
        print("All operations completed successfully!")
    
    print("\n📚 For more information:")
    print("  - S3_INTEGRATION_GUIDE.md")
    print("  - .env.example")


if __name__ == "__main__":
    main()
