# Implementation Readiness Check

Run this silent audit before telling the user that interview prerequisites are covered or ready for an implementation SPEC. If any material check fails, withhold closure-signaling phrasing and ask the smallest targeted question (or present a concrete recommendation with tradeoffs) needed to close the gap.

## Readiness checklist

1. **Open-decision surfacing**: Have all architecture-shaping questions noticed during reasoning (structure, navigation, base choice, storage, `Ingest` / `Query` / `Lint` mechanisms, permissions, historical provenance, migration, backup, connection route) been surfaced to the user rather than answered silently by Agent inference?
2. **Decision provenance and reserved boundaries**: Does every high-impact `settled` decision trace to `user-explicit`, `user-accepted-recommendation`, `verified-environment-fact`, `user-deferred`, or `not-applicable`? Are environment observations (such as the current working directory or an existing `.git` folder) kept strictly as facts until the user chooses or accepts them as the KB destination or versioning mechanism? Are user-reserved runtime choices preserved without hidden defaults?
3. **Decision depth**: For each architecture-shaping choice, do you know the real workflow, the user's priority or tradeoff, and at least one concrete future scenario?
4. **Conditional references loaded**:
   - Was [human-navigation.md](human-navigation.md) read and satisfied (entry point, primary dimensions, old-knowledge retrieval at scale, physical vs virtual split) if people will browse or operate the base directly?
   - Was [base-discovery.md](base-discovery.md) read and verified from primary sources if a third-party software or service base is selected?
   - Was [research-contract.md](research-contract.md) read and verified whenever external or current facts were researched?
5. **Exact destination**: Is the concrete local path, database location, or remote workspace/container known (or explicitly scheduled for selection during an approved connection step), with zero invented paths?
6. **Maintenance entry point and operational mechanisms**:
   - Is it clear where future Agent sessions will discover the authoritative operating rules in the chosen base?
   - Does every core workflow (`Ingest`, `Query`, `Lint`, plus export, backup, and migration when applicable) have a concrete executor (Agent following rules, base-native feature, CLI/API/MCP call, script, or user action) rather than vague capability prose?
   - Are historical provenance expectations (`YYYY-MM-DD` / `repo@commit` anchors and `superseded` history handling) clear for the base's content?
7. **Migration, backup guarantees, and permissions**:
   - If existing material exists, are source locations, untouched boundaries, and migration rules clear?
   - Is backup responsibility explicit, and is the assurance level labeled accurately (`offline snapshot`, `portable export`, or `recoverable backup`) without unrequested Git initialization?
   - Are Agent autonomy boundaries (write, update, `superseded` marking, move, delete, restructure) explicit?
8. **Connection scope and pre-approval hygiene**:
   - If CLI, MCP, connector, or SDK setup is needed, is project vs global scope identified (with global changes flagged for explicit SPEC approval) and is secret intake safe without chat or CLI-argument pasting?
   - Has the target KB destination remained untouched pre-approval, with any research evidence isolated in `.scratch/` or session scratch?

## Outcome

When every applicable item passes, inform the user that design and implementation prerequisites are covered and invite them to ask more questions, revise any choice, request further research, or explicitly end the interview to generate the SPEC.
