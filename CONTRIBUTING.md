
---

## Bonus: `CONTRIBUTING.md`

```markdown
# Contributing to Prime Languages Hub

Thank you for wanting to expand language support! Here's the fastest path.

## Quick Contribution Checklist

- [ ] Engine server written and tested standalone (`nc localhost <port>` or similar)
- [ ] Follows length-prefixed JSON protocol (4-byte big-endian length + JSON body)
- [ ] Python adapter created, inherits `PooledSocketAdapter`
- [ ] Registered in `engines_config.py`
- [ ] Registered in `cli/adapter_registry.py`
- [ ] Language confirmed present in `data/languages_*.json` with correct `category`/`tier`
- [ ] Tested via `prime-hub call <source> <your_language> <function> --args '{...}'`


