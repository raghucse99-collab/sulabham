"""Visual Library plan: syllabus tree, phases and every planned visual (id, title, syllabus topics, picture type).
Edit this file to add visuals; then run  python3 tools/vlib/build.py  (validates lessons, writes vlib/index.json)."""
def T(en, te): return {'en': en, 'te': te}

AREAS = [
 {'id': 'pol', 'em': '⚖️', 'phase': 1, 't': T('Indian Polity', 'భారత రాజ్యాంగం & రాజకీయ వ్యవస్థ'), 'subs': [
  {'id': 'con', 't': T('Constitution', 'రాజ్యాంగం'), 'items': [
   ('VL-POL-CON-01', T('Making of the Constitution', 'రాజ్యాంగ నిర్మాణం'), ['con-6-1'], 'timeline'),
   ('VL-POL-CON-02', T('Sources of the Constitution', 'రాజ్యాంగ ఆధారాలు'), ['con-6-1', 'con-6-2'], 'hub'),
   ('VL-POL-CON-03', T('Salient features', 'ముఖ్య లక్షణాలు'), ['con-6-2'], 'hub'),
   ('VL-POL-CON-04', T('The Preamble, word by word', 'ప్రవేశిక — పదం పదంగా'), ['con-6-3'], 'hub'),
   ('VL-POL-CON-05', T('Amendment of the Constitution (Art 368)', 'రాజ్యాంగ సవరణ (ప్రకరణ 368)'), ['con-6-7'], 'flow'),
   ('VL-POL-CON-06', T('Basic Structure — the case trail', 'మౌలిక స్వరూపం — కేసుల క్రమం'), ['con-6-8', 'con-6-7'], 'timeline')]},
  {'id': 'fr', 't': T('Rights, Directives & Duties', 'హక్కులు, ఆదేశిక సూత్రాలు & విధులు'), 'items': [
   ('VL-POL-FR-01', T('Fundamental Rights — the six groups', 'ప్రాథమిక హక్కులు — ఆరు వర్గాలు'), ['con-6-4'], 'hub'),
   ('VL-POL-FR-02', T('Article 19 — six freedoms', 'ప్రకరణ 19 — ఆరు స్వేచ్ఛలు'), ['con-6-4'], 'hub'),
   ('VL-POL-FR-03', T('The five writs', 'ఐదు రిట్లు'), ['con-6-4', 'con-7-4'], 'compare'),
   ('VL-POL-FR-04', T('Fundamental Rights vs Directive Principles', 'ప్రాథమిక హక్కులు vs ఆదేశిక సూత్రాలు'), ['con-6-5'], 'compare'),
   ('VL-POL-FR-05', T('Directive Principles — three groups', 'ఆదేశిక సూత్రాలు — మూడు వర్గాలు'), ['con-6-5'], 'hub'),
   ('VL-POL-FR-06', T('Fundamental Duties (Art 51A)', 'ప్రాథమిక విధులు (ప్రకరణ 51A)'), ['con-6-6'], 'hub')]},
  {'id': 'par', 't': T('Parliament & Executive', 'పార్లమెంట్ & కార్యనిర్వాహక వర్గం'), 'items': [
   ('VL-POL-PAR-01', T('Union Executive — who holds real power', 'కేంద్ర కార్యనిర్వాహక వర్గం — అసలు అధికారం ఎవరిది'), ['con-7-3', 'con-7-1'], 'tree'),
   ('VL-POL-PAR-02', T('Lok Sabha vs Rajya Sabha', 'లోక్‌సభ vs రాజ్యసభ'), ['con-7-1', 'con-7-2'], 'compare'),
   ('VL-POL-PAR-03', T('How a Bill becomes an Act', 'బిల్లు చట్టంగా ఎలా మారుతుంది'), ['con-7-1'], 'flow'),
   ('VL-POL-PAR-04', T('State legislatures — one House or two', 'రాష్ట్ర శాసనసభలు — ఒకటా రెండా సభలు'), ['con-7-2'], 'compare')]},
  {'id': 'jud', 't': T('Judiciary', 'న్యాయవ్యవస్థ'), 'items': [
   ('VL-POL-JUD-01', T('Integrated judiciary — the court ladder', 'ఏకీకృత న్యాయవ్యవస్థ — కోర్టుల నిచ్చెన'), ['con-7-4'], 'tree'),
   ('VL-POL-JUD-02', T('Judicial review, activism and PIL', 'న్యాయ సమీక్ష, న్యాయ క్రియాశీలత, PIL'), ['con-7-4'], 'compare')]},
  {'id': 'fed', 't': T('Federalism', 'సమాఖ్య వ్యవస్థ'), 'items': [
   ('VL-POL-FED-01', T('Seventh Schedule — three lists', 'ఏడో షెడ్యూల్ — మూడు జాబితాలు'), ['con-8-1'], 'compare'),
   ('VL-POL-FED-02', T('Centre–State relations', 'కేంద్ర–రాష్ట్ర సంబంధాలు'), ['con-8-2', 'con-9-1'], 'hub'),
   ('VL-POL-FED-03', T('Rajamannar, Sarkaria, Punchhi', 'రాజమన్నార్, సర్కారియా, పూంఛీ'), ['con-9-2', 'con-9-1'], 'timeline'),
   ('VL-POL-FED-04', T('Federal and unitary features', 'సమాఖ్య, ఏకకేంద్ర లక్షణాలు'), ['con-9-3'], 'compare')]},
  {'id': 'bod', 't': T('Constitutional & Other Bodies', 'రాజ్యాంగ & ఇతర సంస్థలు'), 'items': [
   ('VL-POL-BOD-01', T('Constitutional vs statutory bodies', 'రాజ్యాంగ సంస్థలు vs చట్టబద్ధ సంస్థలు'), ['con-8-3'], 'compare'),
   ('VL-POL-BOD-02', T('National Human Rights Commission', 'జాతీయ మానవ హక్కుల కమిషన్'), ['con-8-4'], 'tree'),
   ('VL-POL-BOD-03', T('Right to Information — the request path', 'సమాచార హక్కు — దరఖాస్తు దారి'), ['con-8-5'], 'flow'),
   ('VL-POL-BOD-04', T('Lokpal and Lokayukta', 'లోక్‌పాల్, లోకాయుక్త'), ['con-8-6'], 'hub')]},
  {'id': 'ele', 't': T('Elections & Parties', 'ఎన్నికలు & పార్టీలు'), 'items': [
   ('VL-POL-ELE-01', T('Party recognition — national vs state', 'పార్టీల గుర్తింపు — జాతీయ vs రాష్ట్ర'), ['con-9-4', 'con-9-5'], 'compare'),
   ('VL-POL-ELE-02', T('Anti-Defection Law (Tenth Schedule)', 'పార్టీ ఫిరాయింపుల నిరోధక చట్టం (పదో షెడ్యూల్)'), ['con-9-6'], 'flow')]},
  {'id': 'loc', 't': T('Local Government', 'స్థానిక ప్రభుత్వాలు'), 'items': [
   ('VL-POL-LOC-01', T('Panchayati Raj — from CDP to the 73rd Amendment', 'పంచాయతీరాజ్ — CDP నుంచి 73వ సవరణ వరకు'), ['con-10-1', 'con-10-2', 'con-10-3'], 'timeline'),
   ('VL-POL-LOC-02', T('73rd vs 74th Amendment', '73వ vs 74వ సవరణ'), ['con-10-4'], 'compare')]},
 ]},
 {'id': 'his', 'em': '🏺', 'phase': 2, 't': T('Indian History', 'భారతదేశ చరిత్ర'), 'subs': [
  {'id': 'anc', 't': T('Ancient', 'ప్రాచీన'), 'items': []}, {'id': 'med', 't': T('Medieval', 'మధ్యయుగ'), 'items': []}, {'id': 'mod', 't': T('Modern', 'ఆధునిక'), 'items': []}]},
 {'id': 'geo', 'em': '🌍', 'phase': 3, 't': T('Geography', 'భూగోళశాస్త్రం'), 'subs': [
  {'id': 'phy', 't': T('Physical', 'భౌతిక'), 'items': []}, {'id': 'ind', 't': T('Indian', 'భారత'), 'items': []}, {'id': 'apg', 't': T('Andhra Pradesh', 'ఆంధ్రప్రదేశ్'), 'items': []}]},
 {'id': 'eco', 'em': '💰', 'phase': 4, 't': T('Indian Economy', 'భారత ఆర్థిక వ్యవస్థ'), 'subs': [
  {'id': 'bas', 't': T('Basic Concepts', 'ప్రాథమిక భావనలు'), 'items': []}, {'id': 'ban', 't': T('Banking', 'బ్యాంకింగ్'), 'items': []},
  {'id': 'bud', 't': T('Budget', 'బడ్జెట్'), 'items': []}, {'id': 'dev', 't': T('Economic Development', 'ఆర్థికాభివృద్ధి'), 'items': []}]},
 {'id': 'sci', 'em': '🔬', 'phase': 4, 't': T('General Science', 'జనరల్ సైన్స్'), 'subs': [
  {'id': 'phy', 't': T('Physics', 'భౌతికశాస్త్రం'), 'items': []}, {'id': 'che', 't': T('Chemistry', 'రసాయనశాస్త్రం'), 'items': []}, {'id': 'bio', 't': T('Biology', 'జీవశాస్త్రం'), 'items': []}]},
 {'id': 'ap', 'em': '🏛️', 'phase': 5, 't': T('Andhra Pradesh', 'ఆంధ్రప్రదేశ్'), 'subs': [
  {'id': 'his', 't': T('History', 'చరిత్ర'), 'items': []}, {'id': 'cul', 't': T('Culture', 'సంస్కృతి'), 'items': []},
  {'id': 'geo', 't': T('Geography', 'భూగోళం'), 'items': []}, {'id': 'eco', 't': T('Economy', 'ఆర్థిక వ్యవస్థ'), 'items': []}]},
]
