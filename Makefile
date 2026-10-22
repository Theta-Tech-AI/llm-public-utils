check:
	cd .agents/skills/deslop && python3 scripts/check_reachability.py && python3 scripts/swarm_lenses.py --check && python3 scripts/check_principle_template.py && python3 -m py_compile scripts/*.py

.PHONY: check
