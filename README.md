# Flagpole

Feature flags with percentage rollouts and attribute targeting.

Create a flag, switch it on for 10% of users, then narrow it to the ones
whose plan is `pro` — without shipping again.

## How it works

1. **Define** — a flag belongs to a project and carries a rollout percentage
   and an ordered list of targeting rules.
2. **Evaluate** — an SDK posts a user key and that user's attributes; the API
   answers with every flag in the project decided for that user.
3. **Bucket** — rollout is deterministic. The user key is hashed together
   with the flag key, so the same user always gets the same answer, and a
   user in the first 10% of one flag is not automatically in the first 10%
   of every other.

## Layout

```
backend/
  app/
    routers/      flags (admin CRUD) and evaluate (the SDK endpoint)
    services/     bucketing (the hash) and rules (the matcher)
    models.py     Project, Flag, Rule
    auth.py       bearer token for anything that writes
frontend/
  src/
    components/   FlagList, FlagRow
    hooks/        useFlags
    api.ts        typed client
    types.ts      the shapes both ends agree on
```

## Running it

```bash
cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload
```

```bash
cd frontend && npm install && npm run dev
```

## Design notes

**Rules are AND, not OR.** Every rule on a flag must match. Combining with OR
is expressible by creating a second flag, and a single boolean per flag is
much easier to reason about when a rollout misbehaves.

**Rollout is applied last.** A user must pass the rules *and* fall inside the
percentage. Reversing that would mean the percentage was measured against the
whole population rather than the targeted one, which is not what anybody means
by "roll out to 10% of pro users".

**Evaluation is one request.** An SDK asks once and gets every flag, because a
request per flag turns a page load into a waterfall.
