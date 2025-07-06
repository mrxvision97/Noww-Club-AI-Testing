# Google OAuth Setup Instructions

## 🔧 Update Google Cloud Console Settings

Since you've already set up Google OAuth but the redirect URI is incorrect, you need to update it:

### Step 1: Go to Google Cloud Console
1. Visit: https://console.cloud.google.com/
2. Select your project (or create one if needed)

### Step 2: Configure OAuth 2.0
1. Go to **APIs & Services** > **Credentials**
2. Find your OAuth 2.0 Client ID: `729016876840-vc75rdlgt77bvg7b4vr20mv5q9toeb7p.apps.googleusercontent.com`
3. Click on it to edit

### Step 3: Update Authorized Redirect URIs
**Remove:**
- `http://localhost:5000`

**Add:**
- `http://localhost:8501`

### Step 4: Save Changes
Click **Save** to update the configuration.

## 🚀 Test the OAuth Flow

1. **Restart your Streamlit app** (important after .env changes):
   ```bash
   # Stop the current app (Ctrl+C)
   # Then restart:
   streamlit run app.py
   ```

2. **Access the app**: http://localhost:8501

3. **Try Google OAuth**:
   - Click "Sign in with Google"
   - You should be redirected to Google
   - After authorization, you should be redirected back to your app
   - You should automatically be logged in and see the main chat interface

## 🔍 Debugging

If it still doesn't work, check the browser console for errors:
1. Open browser Developer Tools (F12)
2. Check the Console tab for any JavaScript errors
3. Check the Network tab to see if the OAuth requests are being made

## ✅ Expected Flow

1. User clicks "Sign in with Google"
2. Redirected to Google OAuth page
3. User authorizes the app
4. Google redirects back to `http://localhost:8501?code=...`
5. App processes the OAuth code
6. User is logged in and sees the main interface

The .env file has been updated with the correct API key name and redirect URI.
