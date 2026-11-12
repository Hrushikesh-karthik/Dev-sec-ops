# Secure remediation reference

This is the reference `app.py` for the remediation part of the workshop.

1. Copy `secure-solution/app.py` over the root `app.py`.
2. In `templates/search.html`, replace `{{ term | safe }}` with `{{ term }}`.
3. Remove the hardcoded demo token and weak secret key from the vulnerable root app (the secure reference already does not contain them).
4. Set a strong `FLASK_SECRET_KEY` as an environment variable. Do not commit it.
5. For a real application, never store plaintext passwords. Use a password-hashing library such as Werkzeug's `generate_password_hash` and `check_password_hash`.
6. Re-run the GitHub Actions workflow and review every scanner finding.

The workshop intentionally uses a simple plaintext demo password to keep the SQL injection exercise focused. This is not production-ready authentication.
