# Security Policy

## Privacy & Data Protection

Memory Mirror processes sensitive personal data including facial images and personal information.

### ⚠️ DO NOT Commit to Public Repositories

**Never commit:**
- `known_faces/*/` - Personal face images
- `data/caregiver_data.json` - Personal information
- `.env` - Sensitive configuration
- Generated audio files
- Log files

### ✅ Safe to Commit

- Source code in `src/`
- Configuration templates
- Documentation files
- Requirements files

## Best Practices

1. Always use example/template files
2. Keep personal data separate from code
3. Use `.gitignore` properly
4. Review commits before pushing

## Legal Compliance

Users must comply with:
- GDPR (EU)
- CCPA (California)
- BIPA (Illinois)
- Local biometric data regulations

Obtain explicit consent before collecting facial data.
