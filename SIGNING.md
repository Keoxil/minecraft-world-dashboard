# Code signing (removing the Windows SmartScreen warning)

Windows Defender already scans the installer as clean. The "Windows protected your PC" screen is **SmartScreen**, and it appears for any
downloaded program that is not **code-signed** by a publisher Windows trusts. A signature cannot be faked or self-issued: it needs a
certificate issued after an identity check. Options, from easiest to hardest:

## 1. Azure Artifact Signing (formerly Trusted Signing) - about 10 USD/month - recommended
Microsoft's own signing service. Individuals in the USA/Canada can validate their identity; the publisher name shown is the
**verified legal name** (or organization), not a brand name.

1. Create an Azure account and a *Trusted Signing / Artifact Signing* account, then complete **identity validation**.
2. Create a *certificate profile* (Public Trust).
3. Create an app registration (service principal) and give it the role *Trusted Signing Certificate Profile Signer* on that account.
4. In the GitHub repo go to *Settings -> Secrets and variables -> Actions* and add:
   `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_SIGNING_ENDPOINT`, `AZURE_SIGNING_ACCOUNT`, `AZURE_SIGNING_PROFILE`.
5. Push a new tag (`git tag v1.2.1 && git push --tags`). The workflow notices the secrets and signs the installer automatically.

## 2. SignPath Foundation - free for open-source projects
Apply at <https://signpath.org/>. Requires a public repository with an OSI license (this one is MIT) and takes a few days to approve.
The publisher shown is "SignPath Foundation".

## 3. Buy a certificate
An OV or EV code-signing certificate from a certificate authority (roughly 200-500 USD/year). EV gives instant SmartScreen reputation.

## What does NOT work
* **Self-signed certificates:** they only work on computers where you manually install that certificate as trusted. Your friends would still see the warning.
* Compressing, renaming or packing the program differently.

Even after signing, a brand-new certificate can show a milder warning for a short time until downloads build reputation.
