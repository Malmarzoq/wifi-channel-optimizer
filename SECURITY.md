# Security Policy

## Supported version

The latest release on `main` is the supported version.

## Reporting a vulnerability

Do not open a public issue for a vulnerability that could expose router access, credentials, local-network information, or command execution. Use GitHub's private security-advisory reporting for this repository when available, or contact the repository owner privately.

Include a clear description, affected version, reproduction steps, and any proposed mitigation. Do not include real credentials or host keys.

## Deployment guidance

- Keep `.env` local and protect it with restrictive file permissions.
- Use a dedicated router account with only the required privileges.
- Verify SSH host fingerprints through a trusted channel.
- Start with `DRY_RUN=true` and explicitly set it to `false` only after validation.
