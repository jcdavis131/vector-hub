# Lateral Thinking Pack — de Bono for your harness

> Your product isn't out of ideas. It's stuck in the obvious ones.
> MIT-licensed set from danium/lateral-thinking — 8 techniques + router

Covers: Getting unstuck creatively when brainstorming is predictable, constraints feel unbreakable, or you're solving the wrong problem.

## Skills Included (9)

All files live in `bundles/skills/*.md` and are sourced accurately:

- **lateral** — router. Diagnoses the symptom, picks exactly one technique, runs it inline. Never runs two in one pass. Triggers: "lateral thinking", "I'm stuck", "going in circles", "need fresh ideas", "different angle", "break out of the box", "ideas feel same"

- **random-stimulus** — when ideas all feel same / brainstorm predictable. Pull 8-12 unrelated objects across 5 categories, force-connect, keep only ideas you couldn't reach without stimulus. Abandon visibly. Ends with meta-pattern.

- **provocation** — when a rule feels unbreakable. 4-6 deliberately wrong Po statements (escape/reverse/exaggerate/distort/wishful). Extract movement (principle, moment-to-moment, what differs). Shape live threads.

- **inversion** — when requirements assume unquestioned things. List 5-8 assumptions, flip to strongest opposite, ask where flip already true + who profits. Develop survivors, mark dead flips dead.

- **concept-fan** — when you might be solving wrong problem. Ask "what is this a way of doing?" x2 to climb, fan out 3-4 alternative concepts per level, drop back to concrete implementations. Prune branches that are original in a coat.

- **analogy** — when solution works but feels derivative. One-sentence structure: actors/flows/bottleneck. 3-5 distant domains (mix biological + operational + social/cultural). Map roles, transfer mechanisms not aesthetics. Ends with meta-pattern.

- **scamper** — when you have one idea and need variations. 7 ops: Substitute/Combine/Adapt/Modify/Put-to-other-use/Eliminate/Reverse, 3-4 pointed Qs each, empty ops shown empty. Collect hits into variants.

- **six-hats** — when decision made too fast / everyone agrees. Six unblended passes White/Red/Black/Yellow/Green/Blue, green must include one premise-abandoning alternative, blue synthesizes with confidence.

- **worst-idea** — when everything feels timid/safe. Design 5-8 genuinely terrible but shippable ideas, name bad-making mechanism, invert mechanisms not ideas.

## Source provenance

- de Bono Lateral Thinking (1970), Po: Beyond Yes & No (1972), Serious Creativity (1992)
- de Bono Six Thinking Hats® (1985) — registered TM de Bono Group, indie educational implementation
- SCAMPER — Eberle (1971) from Osborn checklist
- Forced Analogy — Synectics, Gordon (1961)
- Assumption Inversion — Jacobi/Munger "invert, always invert" / dialectic
- Worst Idea — reverse brainstorm, d.school/IDEO

## Honesty Mechanics (carried over)

Every technique requires:
- Visible abandonments — if it produces nothing, show empty and move on
- No 7/7 hits is suspicious — pattern-matching on good-answer shape
- Meta-pattern scan after batch — name structural insight across hits+abandons
- Don't push user to decision — diverge, user converges

## When to Load

Any "stuck" signal:

- "we've tried that" / "everything feels same" / "need a different angle" / "constraint feels unbreakable" / "might be wrong problem to solve" / "timid ideas"
- Product direction, retention, positioning, naming, rituals — not debugging or code review
- Works best before building — use to find better product direction, not just another feature

Refuse: debugging, code review, implementation. Redesigning the *process* is in scope; doing the task is not.

## Combo

- Strategist (L1) for diagnosis: "what shape is our stuck?"
- Researcher/Deep-researcher for domain pool pull for analogy
- Synthesist to run Collect→Cluster→Conflict→Crystallize on divergent ideas
- Builder only after an idea survives visible honesty mechanics
- Critic with worst-idea to red-team before shipping

## Invocation

- "use the lateral skill" → router diagnoses
- "use random-stimulus for our retention problem"
- "try provocation on 'users must create account'"
- In Hatch: reads `bundles/skills/<technique>.md` and follows it inline, including honesty mechanics. Never invoke as separate agent.

## Safety

- Each skill is MIT, local-first, no network after install
- Condensed core loops in `lateral.md` handle partial installs — but full files give stimulus pools, question banks, worked examples, so keep all 9 siblings together
- npx: `npx skills add danium/lateral-thinking` (fails offline — use raw GH fallback like we did)
- Manual: we already copied into bundles

## Wiring into agentic-contacts TLPG

- Stage 2 Extract should NOT extract these as people — they are techniques (NodeClass: Thing)
- Stage 3 Resolution should not merge "analogy" with "Analogy Team" etc.
- ContactsHub can treat technique names as triggers if you want "my lateral" → concept-fan etc., but not needed — keep as thinking lenses for Scout only
