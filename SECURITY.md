# Security Notes

Canvas Backup handles Canvas and Google credentials.

## Never Commit These Files

- `.env`
- `config.local.toml`
- `secrets/google-client-secret.json`
- `secrets/google-token.json`
- Any file containing Canvas or Google tokens.

The repository `.gitignore` excludes these by default.

## Canvas Token

Prefer storing the Canvas token in `.env`:

```env
CANVAS_TOKEN=your-token
```

Do not paste the token into documentation, screenshots, GitHub issues, or pull requests.

## Google Credentials

The Google client secret and token are local machine credentials. Keep them in `secrets/`.

If credentials are exposed, revoke them in Google Cloud Console and regenerate them.

## GitHub Publishing Check

Before pushing:

```powershell
git status --short --ignored
```

Only source, docs, tests, and examples should be tracked.
