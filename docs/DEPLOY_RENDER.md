# Deploy the assessment on Render (reviewer-facing demo)

**This step requires your Render account; the assistant cannot create a live URL on your behalf.**
Render persistent disks are a **paid** feature. Review the price before creating the service.
This is a single-instance assessment demo containing only synthetic employee records.

## Preparation (Windows Command Prompt)

From your local `ACME-Salary-Manager` folder, after applying the update patch:

```cmd
npm install
npm run build
python -m pytest -q
git status
git add .
git commit -m "fix: upgrade React, simplify authentication and prepare deployment"
git push origin main
```

If `npm` is not installed, install a current Node.js LTS version from https://nodejs.org/ .
The package setup uses React 19.3.1 and a local esbuild bundle; the output `frontend/dist/` is deliberately not committed. `npm install` generates a package-lock.json; commit it as well so future builds can use `npm ci`.

## Render setup

1. Go to https://dashboard.render.com/ and sign in using GitHub.
2. Select **New → Blueprint**. Connect `Crystal42610/Incubyte_ACME_Salary_Manager`.
3. Render reads `render.yaml`, creates one Docker web service and a **persistent disk** at `/data`. Review the paid Starter plan before approving it.
4. Supply the secret `ACME_ADMIN_PASSWORD` (at least 16 unique characters) in the Blueprint setup or the service Environment page. **Never use the README/example password.**
5. Wait for build and deploy to finish, then open the HTTPS `https://…onrender.com/` URL shown on the Render service page. The first boot seeds 10,000 synthetic employees.
6. Open `https://…onrender.com/api/health`, which should show `{"status":"ok"}`; open the homepage and sign in using `hr-admin` and your secret password.
7. Test employee search (`EMP-00042`), salary edit with reason, audit history, analytics currency selection and refreshing after an edit. Restart/redeploy the service and verify the change persists.
8. Run `python scripts/check_live.py` locally after setting `ACME_DEMO_URL` to your Render HTTPS URL and `ACME_ADMIN_USER`/`ACME_ADMIN_PASSWORD` to your private credentials. This is a read-only verification; it will not edit salary records.
9. Copy the actual live URL into README (Demo link), then commit and push that change. Provide reviewer credentials **privately** in the email, not in GitHub.

## Security limits

- The HTTPS URL protects credentials in transit; the demo still uses one administrator with Basic credentials.
- The system does **not** meet enterprise HR compliance, role-based permissions, SSO, disaster recovery or backup requirements. Only synthetic records are acceptable.
- `render.yaml` deliberately defines a persistent disk; don't remove it without switching to a managed relational database.
- Rotating `ACME_ADMIN_PASSWORD` in Render does not require a source-code change.
- Disable or destroy the demo after review if you don't want it exposed online.

## Failure checks

- **Deploy fails while building Node:** read Render build logs under the service. `npm install` requires internet access and package registry availability.
- **Application starts but login fails:** confirm that `ACME_ADMIN_PASSWORD` was set; the container refuses known example passwords.
- **Database resets:** ensure the `/data` disk is attached and `ACME_DB_PATH=/data/acme.db`.
- **No browser popup:** the API intentionally omits the `WWW-Authenticate` challenge; use only the page's sign-in form.
