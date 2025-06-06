# GitHub Secrets Update Required

The deployment workflow has been updated to use only required environment variables. You need to update your GitHub repository secrets to match.

## 🔧 REQUIRED UPDATE

**In GitHub Repository → Settings → Environments → `dev` and `prod`:**

### 1. Rename Existing Secret
- **Change**: `SECRET_KEY` → `DJANGO_SECRET_KEY`
- **Keep the same value** (your Django secret key)

### 2. Keep These Required Secrets ✅
- `HOST` (deployment server IP)
- `USERNAME` (deployment user: `deploy`)
- `SSH_KEY` (deployment private key)
- `DJANGO_SECRET_KEY` (renamed from SECRET_KEY)
- `DJANGO_ALLOWED_HOSTS` (your domain names)
- `DATABASE_URL` (Supabase connection string)
- `SUPABASE_PROJECT_ID`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_JWT_SECRET`

### 3. Remove These Unused Secrets 🗑️
*(These are now hardcoded in Django settings for better security)*
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `DB_HOST`
- `DB_PASSWORD`
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `CORS_ALLOWED_ORIGINS`
- `LOG_LEVEL` (hardcoded to INFO)
- `MVP_ALLOW_ANONYMOUS`
- `SUPABASE_SERVICE_ROLE_KEY` (optional, not used in runtime)
- All security header variables (hardcoded)
- File upload limit variables (hardcoded)

## ✅ What This Fixes

1. **SECRET_KEY Mismatch**: Django expects `DJANGO_SECRET_KEY` but workflow was using `SECRET_KEY`
2. **Cleaner Configuration**: Only 10 secrets instead of 25+ unused ones
3. **Better Security**: Sensitive settings hardcoded in Django, not in environment
4. **Simpler Maintenance**: Fewer secrets to manage and rotate
5. **Consistent Documentation**: All docs now show minimal required variables

## 🚀 Next Steps

1. Update GitHub Secrets as described above
2. Next deployment will generate clean `.env` with only required variables
3. Verify the application works correctly
4. Delete this file when update is complete

## 🔍 How to Check Current Secrets

Go to: GitHub Repository → Settings → Environments → `dev` (or `prod`) → Environment secrets

You should see only the 10 required secrets listed above after cleanup. 