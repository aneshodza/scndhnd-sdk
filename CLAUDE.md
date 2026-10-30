# scndhnd-sdk

Python SDKs for Swiss second-hand marketplaces.

## Architecture

- Every platform is its **own GitHub repo and PyPI package**: `<platform>-sdk`, imported as `<platform>_sdk`. Repos live under `github.com/aneshodza/`, and local clones sit side by side in `~/private/`.
- **This repo is only the umbrella.** `scndhnd-sdk` depends on the published platform SDKs from PyPI and re-exports their clients. It is not a monorepo. Platform code never lives here.
- When a platform shares a backend with an existing SDK, depend on that SDK instead of copying code. Example: `anibis-sdk` is `tutti-sdk` with anibis's host and client identity.

| Platform | Package | State |
| --- | --- | --- |
| tutti.ch | `tutti-sdk` (`~/private/tutti-sdk`) | Released. Full client, including messaging with a session token |
| anibis.ch | `anibis-sdk` (`~/private/anibis-sdk`) | Released. Read-only, built on tutti-sdk via anibis's web GraphQL |
| ricardo.ch | none | **Parked.** The official API shut down on 2026-09-01, and every web/app host is behind a Cloudflare challenge |
| trovas.ch | `trovas-sdk` (`~/private/trovas-sdk`) | **Local only, not on GitHub yet.** Reads public HTML: search (pages 1–2, per robots.txt) and listing details. No seller names or phone numbers, at least 1 s between requests, honest User-Agent |

Ruled out (checked 2026-10-29):
- **petitesannonces.ch:** `robots.txt` disallows search (`/s/`) and blocks `anthropic-ai` entirely. Don't fetch it.
- **Galaxus resale:** 403 to scripts.
- **Depop:** Cloudflare 403, even on `robots.txt`.
- **Shpock:** no Swiss locale.
- **Vinted:** not available in Switzerland.
- **Facebook Marketplace:** login required, scraping forbidden.

No other candidates are known yet.

## Open items (need the user)

- `trovas-sdk`: decide whether to publish. If yes, follow the new repo checklist, then add it to the umbrella's dependencies.
- `scndhnd-sdk` stays off PyPI until it covers more marketplaces than tutti.ch and anibis.ch (user, 2026-10-30). Leave release PR #1 unmerged; scndhnd-dashboard pins it by git commit.
- filippofinke/tutti-api #9 (the select fix) is open upstream.

## Hard rules

- **Never get around bot protection.** No solving or replaying Cloudflare/Turnstile challenges, no reusing `cf_clearance` cookies, no stealth or headless tricks to look human, no forging an app's request signatures, no guessing or spoofing an unknown app identity, no getting around certificate pinning. Third-party code that does any of this is off-limits too. If a host challenges scripts, stop, write it down and move on.
- Prefer official or documented interfaces. Respect `robots.txt` unless the user decides otherwise; anibis's `/api/` was the user's explicit call.
- Keep live traffic small: a dozen or so requests per check, no load or stress tests.
- Credentials (session tokens, cookies) never go into tracked files or command output. Session stores (`.tutti-sessions/` etc.) are gitignored, with file mode 0600.
- Only the user publishes to PyPI (trusted publisher setup), deletes repos and force-pushes `main`.

## User preferences

- Conventional Commits (`feat:`, `fix:`, `chore:`, `refactor:`, `ci:`, `docs:`). Versions come from release-please.
- **No** `Co-Authored-By: Claude` trailer and **no** "Generated with Claude Code" footer, on commits or PRs.
- No history comments in code ("this used to send X…"). Put the reasoning in the commit or PR description.
- Small, surgical changes and no speculative features. Plain, short docs.
- Contributing upstream: push a branch to the user's fork and hand over the compare link and PR text. The user opens and reviews the PR.
- Python naming: install name `foo-sdk`, import name `foo_sdk`.

## Per-SDK repo template (copy from `~/private/tutti-sdk`)

- uv project with src layout, hatchling, `requires-python >=3.11`, httpx. Dev group: pytest, ruff, pdoc.
- `uv run pytest` runs the offline tests (mocked `httpx.MockTransport`). `uv run pytest -m live` hits the real site; the `live` marker is excluded by default via `addopts`.
- `uv run ruff check . && uv run ruff format --check .`, line length 100.
- Docstrings in reStructuredText, with `__docformat__ = "restructuredtext"` in the package `__init__`. API docs come from pdoc.
- `.github/workflows/ci.yml` runs lint and tests on Python 3.11 and 3.14 with `uv sync --locked`.
- `.github/workflows/release.yml` runs release-please. When a release is created, it publishes to PyPI (trusted publishing, environment `pypi`) and deploys the pdoc docs to GitHub Pages.
- `release-please-config.json`: `release-type: python`, `initial-version: 0.1.0`, `bump-minor-pre-major`, `include-component-in-tag: false`. Add an `extra-files` toml updater for `uv.lock` with jsonpath `$.package[?(@.name.value==='<name>')].version`; the `.value` matters. The manifest starts as `{}`.
- `astral-sh/setup-uv` has no floating major tag, so pin the full version (e.g. `v10.3.3`).
- New repo checklist:
  1. Run `gh repo create --public`.
  2. Enable Pages: `gh api -X POST repos/O/R/pages -f build_type=workflow`.
  3. Allow Actions to open PRs: `PUT repos/O/R/actions/permissions/workflow` with `can_approve_pull_request_reviews=true`.
  4. Create the environment: `PUT repos/O/R/environments/pypi`.
  5. Push.
  6. The user adds a PyPI pending publisher: project, owner `aneshodza`, repo, workflow `release.yml`, environment `pypi`.
  7. Merge the release PR. The user used a merge commit for tutti-sdk.
- Release PRs are opened by the workflow's own token, so CI doesn't run on them. That's expected.

## Platform notes

- **tutti**
  - API: GraphQL at `https://api.tutti.ch/v10/graphql`, using the Android app's identity headers.
  - Login: the API token (`X-Tutti-Auth`) is the web cookie `mp_session_id` (`mc1x…`), and the account ID is in `mp_account_info`. The headless Auth0 login is broken by Turnstile.
  - Minting new tokens: `__app_session` → `www.tutti.ch/auth/access-token` → `/account/authenticateJWT`. This only works shortly after a web login.
  - Select filters send `strings: [{key, value: [...]}]`. Upstream fix: filippofinke/tutti-api #9.
- **anibis**
  - Same Next.js frontend and GraphQL schema as tutti.
  - `api.anibis.ch` rejects tutti's app identity. The website's GraphQL (`https://www.anibis.ch/api/v10/graphql`) works with client id `web/1.0.0+env-anibis.git-<hash>` and a browser UA.
  - Only okkdev/chuko (Elixir, unlicensed) existed before; it was used as a reference, not copied.
- **ricardo**
  - Old partner API docs: `ws.ricardo.ch`, now dead.
  - Help center readable via `https://help.ricardo.ch/api/v2/help_center/<locale>/articles/<id>.json`.
  - Don't revisit until ricardo offers a new API.

## Environment quirks

- A shell wrapper rewrites some commands. `cat a b` with several files, `find` with `-not`/`-exec`, `npx` (use `node_modules/.bin/…`) and `echo ===` (zsh) misbehave, so use single files, Python or `grep -rl` instead.
- Running Python from inside `src/tutti_sdk/` shadows the stdlib `types` module. Run from the repo root.
