# Recipes

Each recipe is one decision request, stored as a JSON file in the [`recipes/`](https://github.com/mertkayacs/jevoss/tree/main/recipes) directory. Run it with the CLI, or open it in the [playground](https://jevoss.mertkayacs.com/playground/) and change it.

```bash
jevoss ask recipes/support_routing.json
```

## Support routing

Route a customer ticket to the right team, score how fast it needs a reply, and flag refund requests and churn threats.

- `team` (Choice): Which team should handle this ticket?
- `urgency` (Score): How quickly does this need a reply?
- `refund_requested` (Noul): Does the customer ask for money back?
- `churn_threat` (Noul): Does the customer say they may leave?

```bash
jevoss ask recipes/support_routing.json
```

Example answer from Deem-4B (measured 2026-10-01 on the public Space, reasoning off): `team` billing 0.95 (technical 0.03, account 0.01); `urgency` score 1.37, most likely level 1 (Within a day, 0.46); `refund_requested` yes 0.98; `churn_threat` yes 0.97.

## Content moderation

Choose an action for a forum post and check whether it attacks a person or strays off topic.

- `action` (Choice): What should moderation do with this post?
- `harassment` (Noul): Does the post target a specific person with abuse?
- `on_topic` (Noul): Is the post about the product?

```bash
jevoss ask recipes/content_moderation.json
```

Example answer from Deem-4B (measured 2026-10-01 on the public Space, reasoning off): `action` warn 0.57 (hide 0.20, allow 0.17); `harassment` yes 0.09; `on_topic` yes 0.97.

## Agent tool gating

Decide whether an agent may run a plan that deletes data, or should ask first.

- `next_step` (Choice): What should the agent runtime do before running the plan?
- `destructive` (Noul): Does the plan delete or overwrite data?
- `risk` (Score): How risky is running this plan without a human check?

```bash
jevoss ask recipes/agent_tool_gating.json
```

Example answer from Deem-4B (measured 2026-10-01 on the public Space, reasoning off): `next_step` confirm 0.62 (dry_run 0.27, run 0.08); `destructive` yes 0.96; `risk` score 2.02, most likely level 2 (Real risk of losing needed data, 0.65).

## LLM-as-judge

Compare two answers against a reference and grade one of them.

- `better` (Choice): Which answer is more accurate against the reference?
- `b_grounded` (Noul): Is answer B consistent with the reference?
- `a_quality` (Score): Rate answer A for correctness and completeness.

```bash
jevoss ask recipes/llm_judge.json
```

Example answer from Deem-4B (measured 2026-10-01 on the public Space, reasoning off): `better` a 0.95 (b 0.03, tie 0.02); `b_grounded` yes 0.03; `a_quality` score 2.81, most likely level 3 (Right and complete, 0.85).

## Invoice approval

Apply a payment policy to an invoice and check for a duplicate. Missing data comes back as unknown.

- `decision` (Choice): Under the policy, what should happen to the invoice?
- `possible_duplicate` (Noul): Could the invoice be a duplicate of a recent entry?

```bash
jevoss ask recipes/invoice_approval.json
```

Example answer from Deem-4B (measured 2026-10-01 on the public Space, reasoning off, unknown option on): `decision` reject 0.58 (approve 0.25, hold 0.14); `possible_duplicate` yes 0.56.

## Security triage

Rate an impossible-travel alert and pick the first step. The model reasons when it is unsure.

- `severity` (Score): How severe is this alert?
- `action` (Choice): What should the on-call analyst do first?
- `mfa_fatigue_possible` (Noul): Could the MFA approval be an accidental push approval?

```bash
jevoss ask recipes/security_triage.json
```

Example answer from Deem-4B (measured 2026-10-01 on the public Space, reasoning auto; no answer fell below the fitted thresholds, so none was reasoned): `severity` score 3.29, most likely level 4 (Critical, 0.50); `action` contact_user 0.68 (revoke_sessions 0.14, escalate 0.11); `mfa_fatigue_possible` yes 0.65.

## NPC decisions

Let a villager choose the morning job. The villagers in Emberwick decide this way.

- `action` (Choice): What should the villager do this morning?
- `share_food` (Noul): Should the villager share food with others?
- `urgency` (Score): How urgent is the first task?

```bash
jevoss ask recipes/npc_decision.json
```

Example answer from Deem-4B (measured 2026-10-01 on the public Space, reasoning off): `action` harvest 0.71 (help_mill 0.12, sow 0.11); `share_food` yes 0.28; `urgency` score 1.65, most likely level 2 (Right now, 0.68).
