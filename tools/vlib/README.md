# Visual Library (vlib)
Standard: tools/CONTENT_STANDARD.md → "Visual Library rules".
- Plan (syllabus tree, phases, every planned visual): `tools/vlib/plan.py`
- Lessons: `vlib/<area>/<ID>.json` — keys: id, checked, lead, vis, explain[3-7], conn[2-6 {to: VL id or syllabus id, t}], memory[1-3], apply[2-5], mcq[5-10 {q, st?, o[4], a, why}], refs[1-6 {t, u https}]; every text is {en, te}.
- Visual types (`vis.type`): hub {c, cs?, nodes[3-10]}, flow {items}, timeline {items with y}, compare {h[2-3], rows[{k, v[], n?}]}, tree {levels[[node with p = parent index]]}. Nodes: {t, s?, items?, n (tap note), c? colour}. Optional `cap`.
- Build/validate: `python3 tools/vlib/build.py` (fails on missing Telugu, MCQ count, bad refs, unknown syllabus ids) → writes `vlib/index.json`.
- Page: `visuals.html?v=<ID>`; MCQ revision ids `v:<ID>:<i>`; question bank and syllabus page read `vlib/index.json`.
