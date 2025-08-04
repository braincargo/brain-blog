# 🔑 API Key Authentication Guide

## 📋 **Overview**

Your blog generation system now supports **secure API key authentication** for programmatic access to protected endpoints. This prevents unauthorized access to your blog generation, synchronization, and rebuild functions.

---

## 🔒 **Protected Endpoints**

The following endpoints now require API key authentication:

| Endpoint | Method | Purpose | Rate Limit |
|----------|--------|---------|------------|
| `/generate` | POST | Generate blog posts | 5 requests / 5 minutes |
| `/blog/sync` | POST | Sync blog indexes | 2 requests / 5 minutes |
| `/blog/rebuild` | POST | Rebuild blog index | 1 request / 10 minutes |

**Note**: The `/webhook` endpoint uses Twilio signature validation instead of API keys.

---

## 🔐 **How API Key Authentication Works**

### **1. Configuration Check**
- System checks if `API_KEY_REQUIRED=true`
- Validates that `API_ACCESS_KEY` environment variable is set
- If disabled or misconfigured, requests pass through

### **2. Header Validation**
- Extracts API key from request headers
- Supports multiple header formats (see below)
- Uses constant-time comparison to prevent timing attacks

### **3. Access Control**
- Valid API key → Request processed
- Invalid/missing key → 401 Unauthorized response
- Configuration error → 500 Internal Server Error

---

## 🛠️ **Generating an API Key**

### **Option 1: Secure Random Generation (Recommended)**

```bash
# Generate a cryptographically secure 32-character API key
python3 -c "
import secrets
import string

# Generate 32-character alphanumeric key
alphabet = string.ascii_letters + string.digits
api_key = ''.join(secrets.choice(alphabet) for _ in range(32))
print(f'Generated API Key: {api_key}')
print(f'Length: {len(api_key)} characters')
"
```

### **Option 2: Using OpenSSL**

```bash
# Generate base64-encoded random key
openssl rand -base64 32 | tr -d "=+/" | cut -c1-32
```

### **Option 3: Using UUID**

```bash
# Generate UUID-based key (remove dashes for 32 chars)
python3 -c "import uuid; print(str(uuid.uuid4()).replace('-', ''))"
```

### **Example Output:**
```
Generated API Key: K8mQ2vX9nR4tF7jL5cW1pE6yH3zN8sB4
Length: 32 characters
```

---

## ⚙️ **Setting Up Your API Key**

### **1. Set Environment Variable**

**For Local Development (.env file):**
```bash
API_ACCESS_KEY=K8mQ2vX9nR4tF7jL5cW1pE6yH3zN8sB4
API_KEY_REQUIRED=true
```

**For Docker Compose:**
```yaml
services:
  braincargo-blog-service:
    environment:
      - API_ACCESS_KEY=K8mQ2vX9nR4tF7jL5cW1pE6yH3zN8sB4
      - API_KEY_REQUIRED=true
```

**For Kubernetes:**
```bash
# Create or update the secret
kubectl create secret generic braincargo-blog-secrets \
  --from-literal=API_ACCESS_KEY="K8mQ2vX9nR4tF7jL5cW1pE6yH3zN8sB4" \
  --dry-run=client -o yaml | kubectl apply -f -
```

### **2. Restart Your Service**
```bash
# Docker Compose
docker-compose restart braincargo-blog-service

# Kubernetes
kubectl rollout restart deployment/braincargo-blog-service
```

---

## 📡 **Using Your API Key**

### **Header Format Options**

The system supports **3 different header formats**:

#### **Option 1: X-API-Key Header (Recommended)**
```bash
curl -X POST https://yourdomain.com/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: K8mQ2vX9nR4tF7jL5cW1pE6yH3zN8sB4" \
  -d '{"url": "https://example.com/article"}'
```

#### **Option 2: Authorization Bearer**
```bash
curl -X POST https://yourdomain.com/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer K8mQ2vX9nR4tF7jL5cW1pE6yH3zN8sB4" \
  -d '{"url": "https://example.com/article"}'
```

#### **Option 3: Authorization API-Key**
```bash
curl -X POST https://yourdomain.com/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: API-Key K8mQ2vX9nR4tF7jL5cW1pE6yH3zN8sB4" \
  -d '{"url": "https://example.com/article"}'
```

---

## 🐍 **Python Code Examples**

### **Using requests library:**

```python
import requests

API_KEY = "K8mQ2vX9nR4tF7jL5cW1pE6yH3zN8sB4"
BASE_URL = "https://yourdomain.com"

# Method 1: X-API-Key header
headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

# Generate a blog post
response = requests.post(
    f"{BASE_URL}/generate",
    headers=headers,
    json={"url": "https://example.com/article"}
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ Blog generated: {result['title']}")
else:
    print(f"❌ Error: {response.status_code} - {response.json()}")
```

### **Using Authorization Bearer:**

```python
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# Sync blog indexes
response = requests.post(
    f"{BASE_URL}/blog/sync",
    headers=headers,
    json={}
)
```

---

## ⚠️ **Security Best Practices**

### **🔒 API Key Security**

1. **Strong Generation**: Use cryptographically secure random generation
2. **Minimum Length**: 32+ characters recommended
3. **Character Set**: Mix of letters, numbers, and symbols
4. **Rotation**: Rotate keys periodically (monthly/quarterly)
5. **Storage**: Never commit keys to code repositories

### **🛡️ Environment Security**

```bash
# ✅ Good: Environment variable
export API_ACCESS_KEY="secure_key_here"

# ❌ Bad: Hardcoded in script
api_key = "K8mQ2vX9nR4tF7jL5cW1pE6yH3zN8sB4"  # DON'T DO THIS
```

### **📋 Access Logging**

The system logs authentication attempts:

```bash
# Successful authentication
✅ Valid API key authentication from IP: 192.168.1.100

# Failed attempts
🚫 Missing API key from IP: 192.168.1.101
🚫 Invalid API key from IP: 192.168.1.102
```

---

## 🚨 **Troubleshooting**

### **Common Issues & Solutions**

#### **❌ "API key required" Error**
```json
{
  "success": false,
  "error": "API key required. Provide via X-API-Key header or Authorization: Bearer <key>"
}
```
**Solution**: Add API key to request headers

#### **❌ "Invalid API key" Error**
```json
{
  "success": false,
  "error": "Invalid API key"
}
```
**Solutions**:
- Verify key matches `API_ACCESS_KEY` environment variable
- Check for extra spaces or characters
- Ensure key wasn't truncated

#### **❌ "API authentication not properly configured" Error**
```json
{
  "success": false,
  "error": "API authentication not properly configured"
}
```
**Solution**: Set `API_ACCESS_KEY` environment variable

### **🔍 Debugging Steps**

1. **Check Configuration**:
   ```bash
   # Verify environment variables are set
   echo $API_ACCESS_KEY
   echo $API_KEY_REQUIRED
   ```

2. **Test with curl**:
   ```bash
   # Test with your actual API key
   curl -v -X POST http://localhost:8080/generate \
     -H "Content-Type: application/json" \
     -H "X-API-Key: YOUR_ACTUAL_KEY" \
     -d '{"url": "https://example.com"}'
   ```

3. **Check Logs**:
   ```bash
   # Look for authentication messages
   docker-compose logs braincargo-blog-service | grep -E "API key|authentication"
   ```

---

## 🔄 **Rotating API Keys**

### **Step-by-Step Key Rotation**

1. **Generate New Key**:
   ```bash
   NEW_KEY=$(python3 -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32)))")
   echo "New key: $NEW_KEY"
   ```

2. **Update Environment**:
   ```bash
   # Update environment variable
   export API_ACCESS_KEY="$NEW_KEY"
   
   # Or update .env file
   sed -i "s/API_ACCESS_KEY=.*/API_ACCESS_KEY=$NEW_KEY/" .env
   ```

3. **Restart Service**:
   ```bash
   docker-compose restart braincargo-blog-service
   ```

4. **Update Clients**:
   ```bash
   # Update any scripts or applications using the old key
   ```

5. **Verify**:
   ```bash
   # Test with new key
   curl -X POST http://localhost:8080/generate \
     -H "X-API-Key: $NEW_KEY" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com"}'
   ```

---

## 📊 **Testing Your Setup**

### **Quick Test Script**

```bash
#!/bin/bash
# test_api_key.sh

API_KEY="K8mQ2vX9nR4tF7jL5cW1pE6yH3zN8sB4"  # Replace with your key
BASE_URL="http://localhost:8080"

echo "🧪 Testing API Key Authentication..."

# Test 1: Valid API key
echo "Test 1: Valid API key"
curl -s -X POST "$BASE_URL/generate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"topic": "test"}' | jq .

# Test 2: Missing API key
echo -e "\nTest 2: Missing API key (should fail)"
curl -s -X POST "$BASE_URL/generate" \
  -H "Content-Type: application/json" \
  -d '{"topic": "test"}' | jq .

# Test 3: Invalid API key
echo -e "\nTest 3: Invalid API key (should fail)"
curl -s -X POST "$BASE_URL/generate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: invalid_key" \
  -d '{"topic": "test"}' | jq .

echo -e "\n✅ API Key testing complete!"
```

---

## 🎯 **Production Deployment**

For production environments, ensure:

1. **✅ Strong API Key**: 32+ characters, cryptographically random
2. **✅ Environment Variables**: Never hardcode keys
3. **✅ HTTPS Only**: Encrypt API key transmission
4. **✅ Access Logging**: Monitor authentication attempts
5. **✅ Rate Limiting**: Enabled to prevent abuse
6. **✅ Regular Rotation**: Schedule periodic key updates

**Ready to use your secure API! 🚀** 