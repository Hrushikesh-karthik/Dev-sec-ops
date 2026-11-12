# Shift-Left DevSecOps Workshop Demo

A beginner-friendly Flask sample application for demonstrating security checks throughout a CI/CD workflow.

## What is included?

- A deliberately vulnerable Flask application (root `app.py`)
- A simple frontend (Jinja templates + CSS)
- A Dockerfile that runs as a non-root user
- GitHub Actions workflow: Gitleaks, Semgrep, Trivy, tests, Docker build and image scan
- A custom Semgrep rules file so the workshop has repeatable findings
- A reference remediation app in `secure-solution/`
- Basic application tests and local helper scripts

## Important safety note

This is a training application with intentionally insecure code. Run it only on your own laptop or an isolated workshop EC2 instance. Do not use real credentials, real personal data, or expose it publicly without restricting access. The demo account is `student` / `Password123!`. The fake token in the source is deliberately nonfunctional and exists only to trigger secret scanning.

## 1. Run locally

Requirements: Python 3.10+.

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

Try:
- Home: `/`
- Login: `/login`
- Demo login: `student` / `Password123!`
- Search: `/search?q=keyboard`
- Health: `/health`

## 2. Run with Docker

```bash
docker build -t devsecops-workshop .
docker run --rm -p 5000:5000 devsecops-workshop
```

Open `http://localhost:5000`.

## 3. Run tests

```bash
pip install -r requirements.txt
python -m unittest discover -s tests -v
```

## 4. Demonstrate Shift-Left checks

Push this repository to GitHub. The workflow is in `.github/workflows/devsecops.yml`.

It runs:
1. Gitleaks — finds the fake demo credential.
2. Semgrep — finds the intentionally unsafe SQL construction, debug mode and hardcoded secret pattern.
3. Trivy filesystem scan — checks dependencies, secrets and misconfiguration.
4. Unit tests.
5. Docker build and Trivy image scan, but only if the earlier job passes.

The starter workflow is intentionally expected to fail at security checks. This is the teaching moment: a security gate prevents an unsafe change from progressing.

### Local scanner commands

Install Gitleaks, Semgrep and Trivy on your machine, then run:

```bash
gitleaks detect --source . --no-git --verbose
semgrep scan --config .semgrep.yml .
trivy fs --scanners vuln,secret,misconfig .
```

Scanner output and exit codes can vary by tool version and rules database. Review the finding details rather than promising a particular number of findings.

## 5. Remediate

Use `secure-solution/README.md` and `secure-solution/app.py` as the reference:
- Replace unsafe SQL string concatenation with parameterized SQL.
- Remove the hardcoded token.
- Load Flask's secret key from an environment variable.
- Remove Flask debug mode.
- Let Jinja auto-escape user input; remove `|safe` in `templates/search.html`.

Then rerun scans and tests. Do not simply disable the scanners or change the pipeline to ignore findings.

For a classroom demonstration, you can first commit the vulnerable starter to a demo branch, show the failed checks, then commit the fixes and show the checks rerun.

## 6. Deploy to AWS EC2 (manual beginner route)

Use an Ubuntu EC2 instance in a workshop-only environment.

Security group:
- SSH (22): allow only the instructor's current public IP.
- App port (5000): do not open to the whole internet for the vulnerable demo. Prefer SSH port forwarding or restrict it to the workshop network.
- For a public demo, put a reverse proxy with TLS in front and deploy only the remediated app.

On the EC2 instance:

```bash
sudo apt-get update
sudo apt-get install -y docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"
```

Log out and reconnect so the group change takes effect. Then copy the project to EC2 or clone your Git repository and run:

```bash
docker build -t devsecops-workshop .
docker run -d --name devsecops-workshop \
  --restart unless-stopped \
  -p 127.0.0.1:5000:5000 \
  devsecops-workshop
```

The `127.0.0.1` binding prevents direct public access to the vulnerable app. To test from your laptop, create an SSH tunnel:

```bash
ssh -i your-key.pem -L 5000:127.0.0.1:5000 ubuntu@YOUR_EC2_PUBLIC_IP
```

Then browse to `http://127.0.0.1:5000` on your laptop.

## 7. OWASP ZAP baseline scan

Only scan your own workshop app, with permission. Run this from your laptop while the app is reachable:

```bash
docker run --rm -t ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t http://127.0.0.1:5000
```

For the EC2 SSH tunnel above, this target is also `http://127.0.0.1:5000`.

ZAP baseline performs passive checks. It does not prove the application is secure and it is not a substitute for a carefully scoped active test.

## Suggested 2-hour event flow

1. Explain DevSecOps and Shift Left (10 min).
2. Show the sample app and threat scenarios (15 min).
3. Push code and inspect Gitleaks/Semgrep findings (25 min).
4. Run Trivy filesystem/dependency scan (15 min).
5. Build and scan Docker image (20 min).
6. Deploy to isolated EC2 (20 min).
7. Run ZAP baseline and discuss findings (15 min).

## Limitations to explain to learners

- A scanner can produce false positives and false negatives.
- Passing a pipeline is not proof of perfect security.
- This sample uses plaintext demo passwords to keep the SQL injection demonstration simple. Real authentication must use secure password hashing, rate limiting, CSRF protection and other controls.
- A production deployment needs TLS, secure secret management, least-privilege IAM, hardened infrastructure, backups and ongoing monitoring.

docker run --rm \
  -t ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py \
  -t http://YOUR_EC2_PUBLIC_IP:5000