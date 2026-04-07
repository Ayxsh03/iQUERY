# iQuery — Render Deployment Guide

Follow these steps exactly to deploy iQuery to [Render.com](https://render.com) on the free tier. This setup uses two Render **Web Services**: one for the FastAPI backend, one for the Next.js frontend.

---

## 1. Prepare your GitHub Repository
Ensure your repository is pushed to GitHub and contains the `backend/` and `frontend/` directories along with their respective `Dockerfile`s.

---

## 2. Deploy the Backend (FastAPI)

1. Log into Render and click **New > Web Service**.
2. Connect your GitHub repository.
3. Configure the service:
   - **Name**: `iquery-api`
   - **Language**: Docker
   - **Root Directory**: `backend` *(⚠️ Critical! Leave empty if using the main docker-compose, but since Render free tier doesn't support docker-compose directly, we point straight to the backend folder)*.
   - **Region**: Choose closest to you.
   - **Instance Type**: Free
4. Open the **Advanced** section and add Environment Variables:
   - `LLM_PROVIDER` = `groq`
   - `GROQ_API_KEY` = `your_actual_key_here`
   - `FRONTEND_URL` = *(Leave blank for now, we will fill it in Step 4)*.
5. Click **Create Web Service**. Wait for it to build and deploy. Copy the deployed URL (e.g., `https://iquery-api.onrender.com`).

---

## 3. Deploy the Frontend (Next.js)

1. Click **New > Web Service** again.
2. Select the same GitHub repository.
3. Configure the service:
   - **Name**: `iquery-web`
   - **Language**: Docker
   - **Root Directory**: `frontend` *(⚠️ Critical!)*
   - **Instance Type**: Free
4. Open the **Advanced** section and add Environment Variables:
   - `NEXT_PUBLIC_API_URL` = `https://iquery-api.onrender.com` *(Paste the URL copied from Step 2)*.
5. Click **Create Web Service**. Wait for the build to finish. Copy the frontend URL (e.g., `https://iquery-web.onrender.com`).

---

## 4. Finalize CORS Settings

1. Go back to your **backend** service (`iquery-api`) on Render.
2. Go to **Environment**.
3. Edit `FRONTEND_URL` and set it to your frontend URL (e.g., `https://iquery-web.onrender.com`).
4. **Save Changes** (Render will auto-redeploy the backend).

---

## 5. Deployment Verification
1. Visit your frontend URL.
2. Go to the Admin page and upload a test PDF.
3. Go to the Chat page and ask a question.
4. Verify the response is generated and source cards appear.

> [!WARNING]
> On the free tier, Render will put your services to sleep after 15 minutes of inactivity. The first request after sleeping will take ~50 seconds to boot up.
> **Because free tier storage is ephemeral, your uploaded documents (ChromaDB + SQLite) will be wiped when the container sleeps.** You must upload fresh documents prior to your demo presentation.
