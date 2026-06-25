# Security Incident Response Reference
Use this for suspected exposure, active compromise, leaked secrets, suspicious access, or post-incident hardening.
## First Hour
Establish:

- what happened or what signal was observed
- affected assets and data classes
- start time and detection time
- current exposure
- whether attacker access may still be active
- who owns communications, operations, and evidence
## Containment
Prefer reversible containment:

- revoke or rotate exposed credentials
- disable compromised tokens or accounts
- block ingress or egress path
- disable vulnerable feature
- roll back or patch affected deployment
- increase logging retention before evidence expires

Do not destroy evidence while containing.
## Evidence
Preserve:

- logs
- audit events
- deployment history
- CI workflow runs
- container/image digests
- IAM changes
- database access records
- affected user/account lists
## Recovery
Confirm:

- credentials are rotated
- vulnerable path is fixed
- backdoors or unauthorized grants are removed
- production has the fix
- monitoring confirms no ongoing access
- customer/data impact is assessed
## Follow-Up
Produce:

- timeline
- root cause
- contributing factors
- missed detection
- durable controls
- regression tests or alerts
