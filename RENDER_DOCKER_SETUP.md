# 🐳 Render Docker Setup Guide

Since you are deploying a Docker-based service directly, here are the exact fields you need to fill out when creating a **New Web Service**.

## 1️⃣ Create New Web Service

1. Go to your **Render Dashboard**.
2. Click **New +** → **Web Service**.
3. Select your repository (`TrustLens` or similar).

## 2️⃣ Configure Service Fields (Important!)

Fill in these fields exactly as shown:

| Field | Value | Notes |
|-------|-------|-------|
| **Name** | `trustlens-backend` | Or any name you like |
| **Region** | `Oregon (US West)` | Or closest to you |
| **Branch** | `main` | Current working branch |
| **Root Directory** | `backend` | ⚠️ **Using 'backend' folder is CRITICAL** so it finds the Dockerfile |
| **Runtime** | **Docker** | ⚠️ Select **Docker**, NOT Python |
| **Instance Type** | **Free** | Or Starter ($7/mo) for better performance |

## 3️⃣ Advanced Settings (Environment Variables)

Scroll down to **Environment Variables** and double-check these are added:

| Key | Value (Example) |
|-----|-----------------|
| `PORT` | `10000` |
| `PYTHON_VERSION` | `3.9.18` |
| `GEMINI_API_KEY` | `AIzaSy...` (Your actual key) |
| `AWS_ACCESS_KEY_ID` | `AKIA...` (Your actual ID) |
| `AWS_SECRET_ACCESS_KEY` | `wJalr...` (Your actual Secret) |
| `AWS_REGION` | `us-east-1` |
| `S3_BUCKET_NAME` | `your-bucket-name` |

## 4️⃣ Deploy

1. Click **Create Web Service**.
2. Watch the logs. You should see steps like `Step 1/7: FROM python:3.9-slim`.
3. If you see `Running on http://0.0.0.0:10000`, it's working!

## ❓ Why "Root Directory" Matters

Because your `Dockerfile` is inside the `backend/` folder, setting the Root Directory to `backend` tells Render to look inside that folder to build the image. If you leave it blank (root), the build will fail because it won't find the Dockerfile.

## 🚀 Pro Tip: Use Blueprints Instead

If you use the `render.yaml` file (Blueprints), **all of this is done automatically** for you! You don't need to manually enter these fields.
