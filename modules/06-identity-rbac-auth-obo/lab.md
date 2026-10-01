# Lab — Predicting OBO success or failure

This lab gives learners an **offline-safe** way to test the core identity rule for Session 6:

> OBO succeeds **only** when the caller is an **interactive signed-in user**, a **delegated user
> token** is present, and the principal type is **User**.

## Lab scenario

You are preparing the underwriting-risk-summarizer to call an isolated user-profile tool before an
authority-sensitive recommendation. Before attempting any live integration, you want to predict
which auth contexts should work.

## What you will use

- [`src/auth_context.py`](src/auth_context.py)
- [`tests/test_auth_context.py`](tests/test_auth_context.py)
- Python 3.10+ only; **no Azure SDK or live cloud access is needed for the classifier**

## Step 1 - Run the unit tests

From this module folder:

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

You should see all tests pass.

## Step 2 - Try the interactive user case

```powershell
python .\src\auth_context.py --interactive --has-user-token --principal-type User
```

Expected result:

- `will_succeed` is `true`
- the reason explains that an interactive signed-in user and delegated token are present

## Step 3 - Try an application/service-principal case

```powershell
python .\src\auth_context.py --principal-type ServicePrincipal
```

Expected result:

- `will_succeed` is `false`
- the reason explains that application/service-principal identities do not provide the required
  interactive user token for OBO

## Step 4 - Try a non-interactive user

```powershell
python .\src\auth_context.py --has-user-token --principal-type User
```

Expected result:

- `will_succeed` is `false`
- the reason explains that a user token alone is not enough without an **interactive** signed-in
  context

## Step 5 - Try a missing-user-token case

```powershell
python .\src\auth_context.py --interactive --principal-type User
```

Expected result:

- `will_succeed` is `false`
- the reason explains that there is no delegated user token to exchange

## Step 6 - Record the rule in your own words

Answer this question:

> Why would a hosted background job that uses only managed identity fail against a user-delegated
> OBO connection even if its RBAC is otherwise correct?

Suggested answer:

- because OBO is not about the agent having broad access
- it is about the platform forwarding the **signed-in user's delegated token**
- without that user token, the exchange cannot happen

## Done-when checklist

- [ ] I ran `python -m unittest discover -s tests -p "test_*.py"` successfully.
- [ ] I verified that an interactive `User` with a user token predicts success.
- [ ] I verified that a `ServicePrincipal` predicts failure.
- [ ] I verified that a non-interactive user context predicts failure.
- [ ] I verified that a missing user token predicts failure.
- [ ] I can explain why OBO and managed identity are not interchangeable.

## Stretch discussion

- Which parts of my insurance workflow should stay on managed identity?
- Which parts genuinely need user-scoped authorization?
- How does toolbox isolation reduce operational risk?
