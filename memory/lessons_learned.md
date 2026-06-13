# Lessons Learned & Optimization History

## System Wide Lessons
- **Context Injection:** Injecting the entire memory folder causes rapid token consumption and agent confusion. Keep context narrow and role-specific.
- **Verification Loop:** All specialist outputs must be vetted by a quality/evaluator agent to prevent code regressions and architectural drifts.
