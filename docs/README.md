# AIBeniq Documentation

This `docs/` directory consolidates previously scattered Markdown files. High-signal, maintained docs live here; ephemeral one-off implementation/fix notes are indexed under `archive/`.

## Core Guides

- Overview & Stack: See root `README.md` (will be trimmed to project intro + quickstart).
- Development Workflow: `development.md` (to be merged -> `docs/development.md`).
- Deployment (Docker Compose): `deployment.md` (to be merged -> `docs/deployment.md`).
- OpenShift / ROSA: Consolidate `OPENSHIFT_*` quickstarts -> `docs/openshift.md`.
- Security Policy: Move `SECURITY.md` -> `docs/security.md`.

## Planned Consolidation Tasks

1. Normalize environment naming (done: production/development).
2. Extract authoritative deployment instructions into `docs/deployment.md`.
3. Merge OpenShift setup + quickstart into `docs/openshift.md` (retain concise quick path + deep dive sections).
4. Move active operational scripts references (pause / deploy) into OpenShift doc.
5. Create `docs/changelog.md` summarizing major feature/fix waves; link detailed historical notes in `docs/archive/`.
6. De-duplicate backend/frontend READMEs; keep language/tooling specifics under `docs/backend.md` & `docs/frontend.md`.
7. Remove or archive one-off *FIX / *IMPLEMENTATION files after indexing.

## Archive Strategy

All files matching patterns:

- `*_FIX.md`
- `*_IMPLEMENTATION.md`
- `*SUMMARY.md`
- Point-in-time status reports (e.g. `FINAL_STATUS_REPORT.md`)

Will be moved to `docs/archive/` and referenced from a generated index table.

## Work In Progress

This initial commit creates the structure. Subsequent steps will migrate and prune root-level clutter.
