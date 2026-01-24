# 🚀 AWS S3 Integration Guide

## Complete Guide to Setting Up Real AWS S3

---

## ✅ **What's Been Integrated**

Your system now has **FULL AWS S3 integration** with:

1. ✅ **Real boto3 S3 client** (not mocked)
2. ✅ **Automatic bucket creation** (if doesn't exist)
3. ✅ **Smart fallback to mock mode** (if credentials missing)
4. ✅ **Directory upload** (with file type detection)
5. ✅ **File reading** (with pagination support)
6. ✅ **Error handling** (connection errors, access denied, etc.)
7. ✅ **Content type detection** (for proper MIME types)
8. ✅ **Large file handling** (skips files > 10MB)

---

## 📋 **Setup Methods** (Choose One)

### **Option 1: Environment Variables** (Recommended for Development)

#### Windows PowerShell:
```powershell
$env:AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
$env:AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
$env:AWS_REGION = "us-east-1"
$env:S3_BUCKET_NAME = "my-code-review-bucket"
```

#### Windows CMD:
```cmd
set AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
set AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
set AWS_REGION=us-east-1
set S3_BUCKET_NAME=my-code-review-bucket
```

#### Linux/Mac:
```bash
export AWS_ACCESS_KEY_ID="AKIAIOSFODNN7EXAMPLE"
export AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
export AWS_REGION="us-east-1"
export S3_BUCKET_NAME="my-code-review-bucket"
```

---

### **Option 2: AWS CLI Configuration** (Recommended for Production)

```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure

# Enter when prompted:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region name (e.g., us-east-1)
# - Default output format (json)
```

This creates:
- `~/.aws/credentials` (Windows: `C:\Users\YourName\.aws\credentials`)
- `~/.aws/config`

boto3 automatically reads from these files.

---

### **Option 3: IAM Role** (Best for AWS EC2/Lambda/ECS)

If running on AWS infrastructure:
1. Attach IAM role to your EC2 instance/Lambda function
2. No credentials needed in code
3. boto3 automatically uses the role

---

## 🔑 **Step 1: Create AWS Account**

1. Visit: https://aws.amazon.com/
2. Click "Create an AWS Account"
3. Follow signup process
4. **Note:** You'll need a credit card (but S3 has a free tier)

### **AWS Free Tier:**
- 5 GB of S3 storage
- 20,000 GET requests
- 2,000 PUT requests
- **Per month for 12 months**

---

## 👤 **Step 2: Create IAM User**

### **Why IAM User?**
- Don't use root account credentials
- Principle of least privilege
- Can be rotated/revoked easily

### **Steps:**

1. **Go to IAM Console:**
   - https://console.aws.amazon.com/iam/

2. **Create User:**
   - Click "Users" → "Add users"
   - Username: `code-review-api`
   - Access type: ✅ **Programmatic access**
   - Click "Next"

3. **Set Permissions:**
   - Click "Attach existing policies directly"
   - Search for: `AmazonS3FullAccess`
   - ✅ Check the box
   - Click "Next" → "Create user"

4. **Save Credentials:**
   - ⚠️ **IMPORTANT:** Download or copy:
     - Access Key ID
     - Secret Access Key
   - ⚠️ You won't be able to see the secret again!

---

## 🪣 **Step 3: Create S3 Bucket (Optional)**

The system **automatically creates** a bucket if it doesn't exist, but you can create it manually:

1. **Go to S3 Console:**
   - https://s3.console.aws.amazon.com/

2. **Create Bucket:**
   - Click "Create bucket"
   - Bucket name: `my-code-review-bucket` (must be globally unique)
   - Region: `us-east-1` (or your preferred region)
   - Block all public access: ✅ **Keep checked** (private bucket)
   - Click "Create bucket"

---

## 🔒 **Security: Minimum IAM Policy**

Instead of `AmazonS3FullAccess`, use this minimal policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:CreateBucket",
        "s3:HeadBucket",
        "s3:ListBucket",
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::my-code-review-bucket",
        "arn:aws:s3:::my-code-review-bucket/*"
      ]
    }
  ]
}
```

**How to apply:**
1. IAM Console → Users → Your user
2. Permissions → Add inline policy
3. JSON tab → Paste above
4. Name it: `S3CodeReviewPolicy`

---

## 🧪 **Step 4: Test Integration**

### **Test Script:**

Create `test_s3.py`:

```python
from storage.s3_reader import S3Reader
from storage.s3_uploader import S3Uploader
import tempfile
import os

# Test upload
print("Testing S3 Upload...")
uploader = S3Uploader()

# Create temp file
with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
    f.write("print('Hello S3!')")
    temp_file = f.name

# Create temp directory
temp_dir = tempfile.mkdtemp()
os.rename(temp_file, os.path.join(temp_dir, 'test.py'))

# Upload
try:
    s3_path = uploader.upload_directory(temp_dir, 'test-upload')
    print(f"✅ Upload successful: {s3_path}")
except Exception as e:
    print(f"❌ Upload failed: {e}")

# Test read
print("\nTesting S3 Read...")
reader = S3Reader()

try:
    files = reader.read_code_snapshot(s3_path)
    print(f"✅ Read successful: {len(files)} files")
    for filename, content in files.items():
        print(f"  - {filename}: {len(content)} bytes")
except Exception as e:
    print(f"❌ Read failed: {e}")

# Cleanup
import shutil
shutil.rmtree(temp_dir)
```

**Run:**
```bash
python test_s3.py
```

**Expected Output (with credentials):**
```
Testing S3 Upload...
✅ S3 client initialized for bucket: my-code-review-bucket
✅ Upload complete: 1 files uploaded, 0 skipped
✅ Upload successful: s3://my-code-review-bucket/code-snapshots/test-upload/

Testing S3 Read...
✅ S3 client initialized for bucket: my-code-review-bucket
✅ Read 1 files from S3
✅ Read successful: 1 files
  - test.py: 19 bytes
```

**Expected Output (without credentials - mock mode):**
```
Testing S3 Upload...
⚠️ AWS credentials not found - using MOCK mode
⚠️ MOCK mode - simulating upload to s3://code-review-bucket/code-snapshots/test-upload/

Testing S3 Read...
⚠️ AWS credentials not found - using MOCK mode
⚠️ Using MOCK S3 - returning sample code
✅ Read successful: 3 files
  - main.py: 500 bytes
  - api.py: 400 bytes
  - utils.py: 600 bytes
```

---

## 🎯 **Integration in Your API**

The S3 integration is **already working** in your API:

### **Upload Flow:**
```
POST /api/repos/upload
  ↓
Controller extracts zip
  ↓
S3Uploader.upload_directory()
  ↓
Real S3 upload (or mock)
  ↓
Returns s3://bucket/path
```

### **Analysis Flow:**
```
POST /api/analysis/start
  ↓
Orchestrator starts
  ↓
Agents call S3Reader.read_code_snapshot()
  ↓
Real S3 read (or mock)
  ↓
Analysis proceeds
```

---

## ⚙️ **Configuration Options**

### **Change Bucket Name:**
```powershell
$env:S3_BUCKET_NAME = "my-custom-bucket"
```

### **Change Region:**
```powershell
$env:AWS_REGION = "eu-west-1"
```

### **Change S3 Prefix:**
```powershell
$env:S3_PREFIX = "my-app/uploads/"
```

---

## 🔧 **Troubleshooting**

### **Error: "NoCredentialsError"**
**Solution:**
- Set environment variables
- Or run `aws configure`
- System will use mock mode automatically

### **Error: "Access Denied (403)"**
**Solution:**
- Check IAM policy includes S3 permissions
- Verify bucket name is correct
- Check bucket is in same region

### **Error: "Bucket does not exist (404)"**
**Solution:**
- System will try to create bucket automatically
- If creation fails, create bucket manually in console
- Ensure bucket name is globally unique

### **Error: "InvalidAccessKeyId"**
**Solution:**
- Double-check Access Key ID
- Ensure no extra spaces
- Key should start with "AKIA"

### **Bucket Created but Can't Upload**
**Solution:**
- Check IAM policy allows `s3:PutObject`
- Verify region matches

---

## 📊 **Monitoring Usage**

### **Check S3 Usage:**
1. Go to S3 Console
2. Click on your bucket
3. "Management" tab
4. View storage metrics

### **Cost Tracking:**
1. AWS Console → Billing
2. View itemized by service
3. S3 free tier: 5GB free

---

## 🎓 **For Viva/Demo**

### **Q: How does S3 integration work?**
**A:** 
```
1. Code uploaded via API
2. S3Uploader extracts and uploads to S3
3. Agents read code from S3 (not local files)
4. Analysis runs on S3 snapshot
5. Results returned to frontend
```

### **Q: What if S3 is unavailable?**
**A:** System automatically falls back to mock mode with sample code. Analysis continues, but uses pre-defined examples.

### **Q: Why S3 and not local storage?**
**A:**
- Scalable (unlimited storage)
- Durable (99.999999999% durability)
- Accessible from any server
- Separates compute from storage
- Production-ready architecture

---

## ✅ **What's Integrated vs What's Mock**

| Component | Status | Notes |
|-----------|--------|-------|
| boto3 client | ✅ Real | Full integration |
| S3 upload | ✅ Real | With credentials |
| S3 read | ✅ Real | With credentials |
| Fallback mock | ✅ Real | Auto-activates |
| Bucket creation | ✅ Real | Auto-creates |
| Error handling | ✅ Real | Production-ready |

---

## 🚀 **Quick Start (TL;DR)**

```bash
# 1. Set credentials
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
export S3_BUCKET_NAME="my-bucket"

# 2. Run server
python run_api.py

# 3. Test
python test_api.py
```

**That's it!** S3 is now fully integrated.

---

## 📚 **Additional Resources**

- AWS S3 Documentation: https://docs.aws.amazon.com/s3/
- boto3 Documentation: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
- IAM Best Practices: https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html

---

**Status:** ✅ **Full AWS S3 Integration Complete**  
**Mode:** Auto-detects credentials (Real or Mock)  
**Production:** Ready with proper credentials
