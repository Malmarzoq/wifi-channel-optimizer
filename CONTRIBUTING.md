# Contributing

Contributions are welcome. Please keep changes focused and do not include router credentials, local IP addresses, host-key files, logs, or generated state files.

## Workflow

1. Create a branch from `main`.
2. Make the change and add or update tests when behavior changes.
3. Run the local checks:

   ```bash
   python -m compileall -q .
   python -m unittest discover -v
   ```

4. Open a pull request. CI must pass before it is merged.

## Router safety

- Use `DRY_RUN=true` while validating a new router or firmware version.
- Never test a channel-changing change against a production network without a rollback plan.
- Document firmware-specific command changes in the pull request.
