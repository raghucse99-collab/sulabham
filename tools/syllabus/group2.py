"""Official APPSC Group 2 syllabus (Notification 37/2026, annexure) -> syllabus/group2.json for syllabus.html.
English topic text follows the official syllabus wording (obvious typos fixed: 'Vedicage' -> 'Vedic Age' etc.).
Each unit is split into trackable topics at the official ' - ' / ' – ' separators.
usage: python3 tools/syllabus/group2.py"""
import json, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
T = lambda en, te: {'en': en, 'te': te}

def unit(uid, en, te, topics, links=None):
    return {'id': uid, 'h': T(en, te), 'links': links or [], 't': [{'id': f'{uid}-{i+1}', **T(a, b)} for i, (a, b) in enumerate(topics)]}

PK = {'href': 'prelims.html', 't': T('Prelims Pack', 'ప్రిలిమ్స్ ప్యాక్')}
CA = {'href': 'current.html', 't': T('Current Affairs', 'కరెంట్ అఫైర్స్')}
TODAY = {'href': 'today.html', 't': T('Today in Sulabham', 'నేటి ప్రత్యేకం')}
MON = {'href': 'ca.html', 't': T('Monthly CA', 'నెలవారీ కరెంట్ అఫైర్స్')}

stages = [
 {'id': 'scr', 'h': T('Screening Test — General Studies & Mental Ability (150 marks)', 'స్క్రీనింగ్ టెస్ట్ — జనరల్ స్టడీస్ & మెంటల్ ఎబిలిటీ (150 మార్కులు)'),
  'sec': [
   {'id': 'scr-his', 'h': T('Indian History (30 marks)', 'భారతదేశ చరిత్ర (30 మార్కులు)'), 'u': [
     unit('his-anc', 'Ancient History', 'ప్రాచీన చరిత్ర', [
       ('Salient features of Indus Valley Civilization', 'సింధు లోయ నాగరికత ముఖ్య లక్షణాలు'),
       ('Vedic Age', 'వేద యుగం'),
       ('Emergence of Buddhism and Jainism', 'బౌద్ధ, జైన మతాల ఆవిర్భావం'),
       ('Mauryan Empire: administration, socio-economic and religious conditions, art and architecture, literature', 'మౌర్య సామ్రాజ్యం: పరిపాలన, సామాజిక-ఆర్థిక, మత పరిస్థితులు, కళలు-వాస్తుశిల్పం, సాహిత్యం'),
       ('Gupta Empire: administration, socio-economic and religious conditions, art and architecture, literature', 'గుప్త సామ్రాజ్యం: పరిపాలన, సామాజిక-ఆర్థిక, మత పరిస్థితులు, కళలు-వాస్తుశిల్పం, సాహిత్యం'),
       ('Harshavardhana and his achievements', 'హర్షవర్ధనుడు, ఆయన విజయాలు')], [PK]),
     unit('his-med', 'Medieval History', 'మధ్యయుగ చరిత్ర', [
       ('The Chola administrative system', 'చోళుల పరిపాలనా వ్యవస్థ'),
       ('Delhi Sultanate: administration, socio-economic and religious conditions, art and architecture, language and literature', 'ఢిల్లీ సుల్తానత్: పరిపాలన, సామాజిక-ఆర్థిక, మత పరిస్థితులు, కళలు-వాస్తుశిల్పం, భాష-సాహిత్యం'),
       ('Mughal Empire: administration, socio-economic and religious conditions, art and architecture, language and literature', 'మొఘల్ సామ్రాజ్యం: పరిపాలన, సామాజిక-ఆర్థిక, మత పరిస్థితులు, కళలు-వాస్తుశిల్పం, భాష-సాహిత్యం'),
       ('Bhakti and Sufi movements', 'భక్తి, సూఫీ ఉద్యమాలు'),
       ('Shivaji and the rise of the Maratha Empire', 'శివాజీ, మరాఠా సామ్రాజ్య ఆవిర్భావం'),
       ('Advent of Europeans', 'యూరోపియన్ల రాక')], [PK]),
     unit('his-mod', 'Modern History', 'ఆధునిక చరిత్ర', [
       ('1857 Revolt and its impact', '1857 తిరుగుబాటు, దాని ప్రభావం'),
       ('Rise and consolidation of British power in India', 'భారత్‌లో బ్రిటిష్ అధికార స్థాపన, సుస్థిరీకరణ'),
       ('Changes in administration, social and cultural spheres', 'పరిపాలన, సామాజిక, సాంస్కృతిక రంగాల్లో మార్పులు'),
       ('Social and religious reform movements in the 19th and 20th century', '19, 20 శతాబ్దాల సామాజిక, మత సంస్కరణ ఉద్యమాలు'),
       ('Indian National Movement: its stages, important contributors and contributions from different parts of the country', 'భారత జాతీయోద్యమం: దశలు, దేశంలోని వివిధ ప్రాంతాల ముఖ్య నాయకులు, వారి కృషి'),
       ('Post-independence consolidation and reorganization within the country', 'స్వాతంత్ర్యానంతర సుస్థిరీకరణ, దేశ పునర్వ్యవస్థీకరణ')], [PK, TODAY])]},
   {'id': 'scr-geo', 'h': T('Geography (30 marks)', 'భూగోళశాస్త్రం (30 మార్కులు)'), 'u': [
     unit('geo-phy', 'General and Physical Geography', 'సాధారణ, భౌతిక భూగోళశాస్త్రం', [
       ('The Earth in our Solar System', 'సౌర కుటుంబంలో భూమి'),
       ('Interior of the Earth', 'భూమి అంతర్భాగం'),
       ('Major landforms and their features', 'ప్రధాన భూస్వరూపాలు, వాటి లక్షణాలు'),
       ('Climate: structure and composition of the atmosphere', 'శీతోష్ణస్థితి: వాతావరణ నిర్మాణం, సంఘటనం'),
       ('Ocean water: tides, waves, currents', 'సముద్ర జలాలు: పోటుపాటులు, అలలు, ప్రవాహాలు'),
       ('India and AP: major physiographic features', 'భారత్, ఏపీ: ప్రధాన భౌతిక స్వరూపాలు'),
       ('India and AP: climate', 'భారత్, ఏపీ: శీతోష్ణస్థితి'),
       ('India and AP: drainage system', 'భారత్, ఏపీ: నదీ వ్యవస్థ'),
       ('India and AP: soils and vegetation', 'భారత్, ఏపీ: నేలలు, వృక్షసంపద'),
       ('Natural hazards and disasters and their management', 'ప్రకృతి ఉపద్రవాలు, విపత్తులు, వాటి నిర్వహణ')], [PK]),
     unit('geo-eco', 'Economic Geography of India and AP', 'భారత్, ఏపీ ఆర్థిక భూగోళశాస్త్రం', [
       ('Natural resources and their distribution', 'సహజ వనరులు, వాటి విస్తరణ'),
       ('Agriculture and agro-based activities', 'వ్యవసాయం, వ్యవసాయ ఆధారిత కార్యకలాపాలు'),
       ('Distribution of major industries and major industrial regions', 'ప్రధాన పరిశ్రమల విస్తరణ, ప్రధాన పారిశ్రామిక ప్రాంతాలు'),
       ('Transport, communication, tourism and trade', 'రవాణా, సమాచార వ్యవస్థ, పర్యాటకం, వాణిజ్యం')], [PK]),
     unit('geo-hum', 'Human Geography of India and AP', 'భారత్, ఏపీ మానవ భూగోళశాస్త్రం', [
       ('Human development', 'మానవాభివృద్ధి'),
       ('Demographics', 'జనాభా అంశాలు'),
       ('Urbanization and migration', 'పట్టణీకరణ, వలసలు'),
       ('Racial, tribal, religious and linguistic groups', 'జాతి, గిరిజన, మత, భాషా సమూహాలు')], [PK])]},
   {'id': 'scr-soc', 'h': T('Indian Society (30 marks)', 'భారతీయ సమాజం (30 మార్కులు)'), 'u': [
     unit('soc-str', 'Structure of Indian Society', 'భారతీయ సమాజ నిర్మాణం', [
       ('Family', 'కుటుంబం'), ('Marriage', 'వివాహం'), ('Kinship', 'బంధుత్వం'), ('Caste', 'కులం'), ('Tribe', 'తెగ'),
       ('Ethnicity', 'జాతీయత (ఎత్నిసిటీ)'), ('Religion', 'మతం'), ('Women', 'మహిళలు')]),
     unit('soc-iss', 'Social Issues', 'సామాజిక సమస్యలు', [
       ('Casteism', 'కులతత్వం'), ('Communalism', 'మతతత్వం'), ('Regionalisation', 'ప్రాంతీయతత్వం'), ('Crime against women', 'మహిళలపై నేరాలు'),
       ('Child abuse and child labour', 'బాలలపై వేధింపులు, బాల కార్మికులు'), ('Youth unrest and agitation', 'యువతలో అసంతృప్తి, ఆందోళనలు')], [TODAY]),
     unit('soc-wel', 'Welfare Mechanism', 'సంక్షేమ యంత్రాంగం', [
       ('Public policies and welfare programmes', 'ప్రభుత్వ విధానాలు, సంక్షేమ పథకాలు'),
       ('Constitutional and statutory provisions for Scheduled Castes and Scheduled Tribes', 'షెడ్యూల్డ్ కులాలు, తెగలకు రాజ్యాంగ, చట్టబద్ధ నిబంధనలు'),
       ('Constitutional and statutory provisions for Minorities and BCs', 'మైనారిటీలు, బీసీలకు రాజ్యాంగ, చట్టబద్ధ నిబంధనలు'),
       ('Constitutional and statutory provisions for Women, Disabled and Children', 'మహిళలు, దివ్యాంగులు, బాలలకు రాజ్యాంగ, చట్టబద్ధ నిబంధనలు')], [CA])]},
   {'id': 'scr-ca', 'h': T('Current Affairs (30 marks)', 'కరెంట్ అఫైర్స్ (30 మార్కులు)'), 'u': [
     unit('ca', 'Major current events and issues', 'ప్రధాన సమకాలీన సంఘటనలు, సమస్యలు', [
       ('International', 'అంతర్జాతీయ'), ('National', 'జాతీయ'), ('State of Andhra Pradesh', 'ఆంధ్రప్రదేశ్ రాష్ట్రం')], [CA, TODAY, MON])]},
   {'id': 'scr-men', 'h': T('Mental Ability (30 marks)', 'మెంటల్ ఎబిలిటీ (30 మార్కులు)'), 'u': [
     unit('men-log', 'Logical Reasoning (deductive, inductive, abductive)', 'తార్కిక వివేచన (డిడక్టివ్, ఇండక్టివ్, అబ్డక్టివ్)', [
       ('Statement and assumptions', 'ప్రకటన, ఊహలు'), ('Statement and argument', 'ప్రకటన, వాదన'),
       ('Statement and conclusion', 'ప్రకటన, నిర్ధారణ'), ('Statement and courses of action', 'ప్రకటన, చర్యా మార్గాలు')]),
     unit('men-abl', 'Mental Ability', 'మానసిక సామర్థ్యం', [
       ('Number series', 'సంఖ్యా శ్రేణి'), ('Letter series', 'అక్షర శ్రేణి'), ('Odd man out', 'భిన్నమైనది గుర్తించడం'),
       ('Coding–decoding', 'కోడింగ్–డీకోడింగ్'), ('Problems relating to relations', 'సంబంధాల సమస్యలు'), ('Shapes and their sub-sections', 'ఆకారాలు, వాటి ఉపభాగాలు')]),
     unit('men-num', 'Basic Numeracy and Data Analysis', 'ప్రాథమిక గణితం, దత్తాంశ విశ్లేషణ', [
       ('Number system and order of magnitude', 'సంఖ్యా వ్యవస్థ, పరిమాణ క్రమం'), ('Averages', 'సగటు'), ('Ratio and proportion', 'నిష్పత్తి, అనుపాతం'),
       ('Percentage', 'శాతం'), ('Simple and compound interest', 'సాధారణ, చక్రవడ్డీ'), ('Time and work', 'కాలం, పని'), ('Time and distance', 'కాలం, దూరం'),
       ('Data analysis: tables, bar diagram, line graph, pie chart', 'దత్తాంశ విశ్లేషణ: పట్టికలు, బార్ డయాగ్రమ్, లైన్ గ్రాఫ్, పై చార్ట్')])]}]},
 {'id': 'p1', 'h': T('Mains Paper I (150 marks)', 'మెయిన్స్ పేపర్ I (150 మార్కులు)'),
  'sec': [
   {'id': 'p1-a', 'h': T('Section A — Social and Cultural History of Andhra Pradesh (75 marks)', 'సెక్షన్ A — ఆంధ్రప్రదేశ్ సామాజిక, సాంస్కృతిక చరిత్ర (75 మార్కులు)'), 'u': [
     unit('aph-1', '1. Pre-historic cultures to Andhra Cholas', '1. చరిత్ర పూర్వ సంస్కృతుల నుంచి ఆంధ్ర చోళుల వరకు', [
       ('Pre-historic cultures', 'చరిత్ర పూర్వ సంస్కృతులు'),
       ('The Satavahanas: socio-economic and religious conditions, literature, art and architecture', 'శాతవాహనులు: సామాజిక-ఆర్థిక, మత పరిస్థితులు, సాహిత్యం, కళలు-వాస్తుశిల్పం'),
       ('The Ikshvakus: socio-economic and religious conditions, literature, art and architecture', 'ఇక్ష్వాకులు: సామాజిక-ఆర్థిక, మత పరిస్థితులు, సాహిత్యం, కళలు-వాస్తుశిల్పం'),
       ('The Vishnukundins', 'విష్ణుకుండినులు'),
       ('The Eastern Chalukyas of Vengi', 'వేంగి తూర్పు చాళుక్యులు'),
       ('Andhra Cholas: society, religion, Telugu language, art and architecture', 'ఆంధ్ర చోళులు: సమాజం, మతం, తెలుగు భాష, కళలు-వాస్తుశిల్పం')], [PK]),
     unit('aph-2', '2. Andhradesa between the 11th and 16th centuries AD', '2. క్రీ.శ. 11–16 శతాబ్దాల మధ్య ఆంధ్రదేశం', [
       ('Major and minor dynasties that ruled Andhradesa (11th–16th centuries)', 'ఆంధ్రదేశాన్ని పాలించిన ప్రధాన, చిన్న రాజవంశాలు (11–16 శతాబ్దాలు)'),
       ('Socio-religious and economic conditions', 'సామాజిక-మత, ఆర్థిక పరిస్థితులు'),
       ('Growth of Telugu language and literature', 'తెలుగు భాష, సాహిత్య వికాసం'),
       ('Art and architecture in Andhradesa (11th–16th centuries)', 'ఆంధ్రదేశంలో కళలు, వాస్తుశిల్పం (11–16 శతాబ్దాలు)')], [PK]),
     unit('aph-3', '3. Europeans to 1947 in Andhra', '3. యూరోపియన్ల రాక నుంచి 1947 వరకు ఆంధ్ర', [
       ('Advent of Europeans and trade centres', 'యూరోపియన్ల రాక, వాణిజ్య కేంద్రాలు'),
       ('Andhra under the Company', 'కంపెనీ పాలనలో ఆంధ్ర'),
       ('1857 Revolt and its impact on Andhra', '1857 తిరుగుబాటు, ఆంధ్రపై దాని ప్రభావం'),
       ('Establishment of British rule', 'బ్రిటిష్ పాలన స్థాపన'),
       ('Socio-cultural awakening; Justice Party / Self-Respect Movement', 'సామాజిక-సాంస్కృతిక చైతన్యం; జస్టిస్ పార్టీ / ఆత్మగౌరవ ఉద్యమం'),
       ('Growth of the Nationalist Movement in Andhra, 1885–1947', 'ఆంధ్రలో జాతీయోద్యమ వికాసం, 1885–1947'),
       ('Role of Socialists and Communists', 'సోషలిస్టులు, కమ్యూనిస్టుల పాత్ర'),
       ('Anti-Zamindari and Kisan movements', 'జమీందారీ వ్యతిరేక, కిసాన్ ఉద్యమాలు'),
       ('Nationalist poetry, revolutionary literature, Nataka Samasthalu and women\'s participation', 'జాతీయవాద కవిత్వం, విప్లవ సాహిత్యం, నాటక సమాజాలు, మహిళల భాగస్వామ్యం')]),
     unit('aph-4', '4. Andhra Movement and Andhra State (1953)', '4. ఆంధ్రోద్యమం, ఆంధ్ర రాష్ట్రం (1953)', [
       ('Origin and growth of the Andhra Movement', 'ఆంధ్రోద్యమ ఆవిర్భావం, వికాసం'),
       ('Role of Andhra Mahasabhas and prominent leaders', 'ఆంధ్ర మహాసభల పాత్ర, ప్రముఖ నాయకులు'),
       ('Events leading to the formation of Andhra State, 1953', '1953 ఆంధ్ర రాష్ట్ర ఏర్పాటుకు దారితీసిన సంఘటనలు'),
       ('Role of the press and newspapers in the Andhra Movement', 'ఆంధ్రోద్యమంలో పత్రికల పాత్ర'),
       ('Role of the Library Movement; folk and tribal culture', 'గ్రంథాలయ ఉద్యమ పాత్ర; జానపద, గిరిజన సంస్కృతి')], [TODAY]),
     unit('aph-5', '5. Formation of Andhra Pradesh and 1956–2014', '5. ఆంధ్రప్రదేశ్ ఏర్పాటు, 1956–2014', [
       ('Events leading to the formation of Andhra Pradesh State', 'ఆంధ్రప్రదేశ్ రాష్ట్ర ఏర్పాటుకు దారితీసిన సంఘటనలు'),
       ('Visalandhra Mahasabha', 'విశాలాంధ్ర మహాసభ'),
       ('States Reorganization Commission and its recommendations', 'రాష్ట్రాల పునర్వ్యవస్థీకరణ సంఘం, దాని సిఫార్సులు'),
       ('Gentlemen\'s Agreement', 'పెద్దమనుషుల ఒప్పందం'),
       ('Important social and cultural events, 1956–2014', 'ముఖ్య సామాజిక, సాంస్కృతిక సంఘటనలు, 1956–2014')])]},
   {'id': 'p1-b', 'h': T('Section B — Indian Constitution (75 marks)', 'సెక్షన్ B — భారత రాజ్యాంగం (75 మార్కులు)'), 'u': [
     unit('con-6', '6. Nature and basic features of the Constitution', '6. రాజ్యాంగ స్వభావం, మౌలిక లక్షణాలు', [
       ('Nature of the Indian Constitution and constitutional development', 'భారత రాజ్యాంగ స్వభావం, రాజ్యాంగ వికాసం'),
       ('Salient features of the Indian Constitution', 'భారత రాజ్యాంగ ముఖ్య లక్షణాలు'),
       ('Preamble', 'ప్రవేశిక'),
       ('Fundamental Rights', 'ప్రాథమిక హక్కులు'),
       ('Directive Principles of State Policy and their relationship with Fundamental Rights', 'ఆదేశిక సూత్రాలు, ప్రాథమిక హక్కులతో వాటి సంబంధం'),
       ('Fundamental Duties', 'ప్రాథమిక విధులు'),
       ('Amendment of the Constitution', 'రాజ్యాంగ సవరణ'),
       ('Basic Structure of the Constitution', 'రాజ్యాంగ మౌలిక స్వరూపం')]),
     unit('con-7', '7. Structure and functions of the Government', '7. ప్రభుత్వ నిర్మాణం, విధులు', [
       ('Legislature, Executive and Judiciary', 'శాసన, కార్యనిర్వాహక, న్యాయ వ్యవస్థలు'),
       ('Types of legislatures: unicameral, bicameral', 'శాసనసభల రకాలు: ఏకసభ, ద్విసభ'),
       ('Executive — parliamentary system', 'కార్యనిర్వాహక వర్గం — పార్లమెంటరీ వ్యవస్థ'),
       ('Judiciary, judicial review and judicial activism', 'న్యాయవ్యవస్థ, న్యాయ సమీక్ష, న్యాయ క్రియాశీలత')]),
     unit('con-8', '8. Union–State powers and constitutional bodies', '8. కేంద్ర–రాష్ట్ర అధికారాలు, రాజ్యాంగ సంస్థలు', [
       ('Distribution of legislative and executive powers between the Union and the States', 'కేంద్ర, రాష్ట్రాల మధ్య శాసన, కార్యనిర్వాహక అధికారాల పంపిణీ'),
       ('Legislative, administrative and financial relations between the Union and the States', 'కేంద్ర–రాష్ట్ర శాసన, పరిపాలనా, ఆర్థిక సంబంధాలు'),
       ('Powers and functions of constitutional bodies', 'రాజ్యాంగ సంస్థల అధికారాలు, విధులు'),
       ('Human Rights Commission', 'మానవ హక్కుల కమిషన్'),
       ('Right to Information (RTI)', 'సమాచార హక్కు (RTI)'),
       ('Lokpal and Lokayukta', 'లోక్‌పాల్, లోకాయుక్త')]),
     unit('con-9', '9. Centre–State relations, parties and elections', '9. కేంద్ర–రాష్ట్ర సంబంధాలు, పార్టీలు, ఎన్నికలు', [
       ('Centre–State relations and need for reforms', 'కేంద్ర–రాష్ట్ర సంబంధాలు, సంస్కరణల అవసరం'),
       ('Rajamannar Committee, Sarkaria Commission, M.M. Punchhi Commission', 'రాజమన్నార్ కమిటీ, సర్కారియా కమిషన్, ఎం.ఎం. పూంఛీ కమిషన్'),
       ('Unitary and federal features of the Indian Constitution', 'భారత రాజ్యాంగంలో ఏకకేంద్ర, సమాఖ్య లక్షణాలు'),
       ('Indian political parties and the party system; recognition of national and state parties', 'భారత రాజకీయ పార్టీలు, పార్టీ వ్యవస్థ; జాతీయ, రాష్ట్ర పార్టీల గుర్తింపు'),
       ('Elections and electoral reforms', 'ఎన్నికలు, ఎన్నికల సంస్కరణలు'),
       ('Anti-Defection Law', 'పార్టీ ఫిరాయింపుల నిరోధక చట్టం')]),
     unit('con-10', '10. Decentralization and local government', '10. వికేంద్రీకరణ, స్థానిక ప్రభుత్వాలు', [
       ('Centralization vs decentralization', 'కేంద్రీకరణ vs వికేంద్రీకరణ'),
       ('Community Development Programme', 'సామాజిక అభివృద్ధి కార్యక్రమం'),
       ('Balwant Rai Mehta and Ashok Mehta Committees', 'బల్వంత్‌రాయ్ మెహతా, అశోక్ మెహతా కమిటీలు'),
       ('73rd and 74th Constitutional Amendment Acts and their implementation', '73, 74వ రాజ్యాంగ సవరణ చట్టాలు, వాటి అమలు')])]}]},
 {'id': 'p2', 'h': T('Mains Paper II (150 marks)', 'మెయిన్స్ పేపర్ II (150 మార్కులు)'),
  'sec': [
   {'id': 'p2-a', 'h': T('Section A — Indian and AP Economy (75 marks)', 'సెక్షన్ A — భారత, ఏపీ ఆర్థిక వ్యవస్థ (75 మార్కులు)'), 'u': [
     unit('eco-1', '1. Structure of Indian Economy, planning and policy', '1. భారత ఆర్థిక వ్యవస్థ నిర్మాణం, ప్రణాళిక, విధానం', [
       ('National income: concept and measurement', 'జాతీయ ఆదాయం: భావన, గణన'),
       ('Occupational pattern and sectoral distribution of income in India', 'వృత్తి విధానం, ఆదాయ రంగాల వారీ పంపిణీ'),
       ('Economic growth and economic development', 'ఆర్థిక వృద్ధి, ఆర్థికాభివృద్ధి'),
       ('Strategy of planning in India', 'భారత్‌లో ప్రణాళికా వ్యూహం'),
       ('New Economic Reforms 1991', '1991 నూతన ఆర్థిక సంస్కరణలు'),
       ('Decentralization of financial resources', 'ఆర్థిక వనరుల వికేంద్రీకరణ'),
       ('NITI Aayog', 'నీతి ఆయోగ్')]),
     unit('eco-2', '2. Money, banking, public finance and foreign trade', '2. ద్రవ్యం, బ్యాంకింగ్, ప్రభుత్వ విత్తం, విదేశీ వాణిజ్యం', [
       ('Functions and measures of money supply', 'ద్రవ్య సరఫరా విధులు, కొలమానాలు'),
       ('RBI: functions, monetary policy and credit control', 'RBI: విధులు, ద్రవ్య విధానం, పరపతి నియంత్రణ'),
       ('Indian banking: structure, development and reforms', 'భారత బ్యాంకింగ్: నిర్మాణం, అభివృద్ధి, సంస్కరణలు'),
       ('Inflation: causes and remedies', 'ద్రవ్యోల్బణం: కారణాలు, నివారణలు'),
       ('Fiscal policy: fiscal imbalance, deficit finance, fiscal responsibility', 'కోశ విధానం: కోశ అసమతుల్యత, లోటు విత్తం, కోశ బాధ్యత'),
       ('Indian tax structure and GST', 'భారత పన్నుల నిర్మాణం, GST'),
       ('Recent Indian Budget', 'ఇటీవలి కేంద్ర బడ్జెట్'),
       ('Balance of Payments (BOP) and FDI', 'చెల్లింపుల శేషం (BOP), FDI')], [CA]),
     unit('eco-3', '3. Agriculture, industry and services in India', '3. భారత్‌లో వ్యవసాయ, పారిశ్రామిక, సేవా రంగాలు', [
       ('Indian agriculture: cropping pattern, production and productivity', 'భారత వ్యవసాయం: పంటల విధానం, ఉత్పత్తి, ఉత్పాదకత'),
       ('Agricultural finance and marketing: issues and initiatives', 'వ్యవసాయ విత్తం, మార్కెటింగ్: సమస్యలు, చొరవలు'),
       ('Agricultural pricing and policy: MSP, procurement, issue price, distribution', 'వ్యవసాయ ధరల విధానం: MSP, సేకరణ, జారీ ధర, పంపిణీ'),
       ('Industrial development in India: patterns and problems', 'భారత పారిశ్రామికాభివృద్ధి: విధానాలు, సమస్యలు'),
       ('New Industrial Policy 1991, disinvestment, Ease of Doing Business', '1991 నూతన పారిశ్రామిక విధానం, పెట్టుబడుల ఉపసంహరణ, సులభతర వాణిజ్యం'),
       ('Industrial sickness: causes, consequences, remedies', 'పారిశ్రామిక రుగ్మత: కారణాలు, పర్యవసానాలు, నివారణలు'),
       ('Services sector: growth and contribution; role of IT and ITES', 'సేవా రంగం: వృద్ధి, వాటా; IT, ITES పాత్ర')]),
     unit('eco-4', '4. Structure of AP economy and public finance', '4. ఏపీ ఆర్థిక వ్యవస్థ నిర్మాణం, ప్రభుత్వ విత్తం', [
       ('Structure and growth of AP economy: GSDP and sectoral contribution', 'ఏపీ ఆర్థిక వ్యవస్థ నిర్మాణం, వృద్ధి: GSDP, రంగాల వాటా'),
       ('AP per capita income (PCI)', 'ఏపీ తలసరి ఆదాయం (PCI)'),
       ('AP state revenue: tax and non-tax', 'ఏపీ ఆదాయం: పన్ను, పన్నేతర'),
       ('AP state expenditure, debts and interest payments', 'ఏపీ వ్యయం, అప్పులు, వడ్డీ చెల్లింపులు'),
       ('Central assistance and externally aided projects', 'కేంద్ర సహాయం, విదేశీ సహాయ ప్రాజెక్టులు'),
       ('Recent AP Budget', 'ఇటీవలి ఏపీ బడ్జెట్')], [CA]),
     unit('eco-5', '5. AP agriculture, industry and services', '5. ఏపీ వ్యవసాయ, పారిశ్రామిక, సేవా రంగాలు', [
       ('Production trends of agriculture and allied sectors; cropping pattern', 'వ్యవసాయ, అనుబంధ రంగాల ఉత్పత్తి ధోరణులు; పంటల విధానం'),
       ('Rural credit cooperatives and agricultural marketing', 'గ్రామీణ పరపతి సహకార సంఘాలు, వ్యవసాయ మార్కెటింగ్'),
       ('AP schemes for agriculture and allied sectors: horticulture, animal husbandry, fisheries, forests', 'వ్యవసాయ, అనుబంధ రంగాలకు ఏపీ పథకాలు: ఉద్యానవనాలు, పశుసంవర్ధకం, మత్స్య, అటవీ'),
       ('Growth and structure of industries; recent AP Industrial Development Policy', 'పరిశ్రమల వృద్ధి, నిర్మాణం; ఇటీవలి ఏపీ పారిశ్రామికాభివృద్ధి విధానం'),
       ('Single window mechanism, industrial incentives, MSMEs', 'సింగిల్ విండో విధానం, పారిశ్రామిక ప్రోత్సాహకాలు, MSMEలు'),
       ('Industrial corridors', 'పారిశ్రామిక కారిడార్లు'),
       ('Services sector in AP; IT, electronics and communications; recent AP IT Policy', 'ఏపీ సేవా రంగం; IT, ఎలక్ట్రానిక్స్, కమ్యూనికేషన్స్; ఇటీవలి ఏపీ IT విధానం')], [CA])]},
   {'id': 'p2-b', 'h': T('Section B — Science and Technology (75 marks)', 'సెక్షన్ B — సైన్స్ అండ్ టెక్నాలజీ (75 మార్కులు)'), 'u': [
     unit('st-1', '1. Technology missions, policies and applications', '1. సాంకేతిక మిషన్లు, విధానాలు, అనువర్తనాలు', [
       ('National S&T policy: recent STI policy, national strategies and missions, emerging technology frontiers', 'జాతీయ S&T విధానం: ఇటీవలి STI విధానం, జాతీయ వ్యూహాలు, మిషన్లు, నూతన సాంకేతికతలు'),
       ('Space technology: Indian launch vehicles, recent satellite launches and applications, space science missions', 'అంతరిక్ష సాంకేతికత: భారత ప్రయోగ వాహనాలు, ఇటీవలి ఉపగ్రహ ప్రయోగాలు, అనువర్తనాలు, అంతరిక్ష విజ్ఞాన మిషన్లు'),
       ('Defence technology: DRDO structure, vision, mission, technologies; IGMDP', 'రక్షణ సాంకేతికత: DRDO నిర్మాణం, లక్ష్యాలు, సాంకేతికతలు; IGMDP'),
       ('ICT: National Policy on IT, Digital India, e-governance programmes and services', 'ICT: జాతీయ IT విధానం, డిజిటల్ ఇండియా, ఈ-గవర్నెన్స్ కార్యక్రమాలు, సేవలు'),
       ('Cyber security concerns and National Cyber Security Policy', 'సైబర్ భద్రత సమస్యలు, జాతీయ సైబర్ భద్రత విధానం'),
       ('Nuclear technology: Indian reactors and power plants, applications of radioisotopes, India\'s nuclear programme', 'అణు సాంకేతికత: భారత రియాక్టర్లు, అణు విద్యుత్ కేంద్రాలు, రేడియో ఐసోటోపుల అనువర్తనాలు, భారత అణు కార్యక్రమం')], [CA, TODAY]),
     unit('st-2', '2. Energy management', '2. శక్తి నిర్వహణ', [
       ('Installed energy capacities and demand in India', 'భారత్‌లో స్థాపిత ఇంధన సామర్థ్యం, డిమాండ్'),
       ('National Energy Policy and National Policy on Biofuels', 'జాతీయ ఇంధన విధానం, జాతీయ జీవ ఇంధనాల విధానం'),
       ('Bharat Stage norms', 'భారత్ స్టేజ్ ప్రమాణాలు'),
       ('Non-renewable and renewable energy: sources and installed capacities', 'పునరుత్పాదకం కాని, పునరుత్పాదక ఇంధనాలు: వనరులు, స్థాపిత సామర్థ్యం'),
       ('New initiatives, programmes, schemes and achievements in renewable energy', 'పునరుత్పాదక ఇంధన రంగంలో కొత్త చొరవలు, పథకాలు, విజయాలు')], [CA]),
     unit('st-3', '3. Ecosystem and biodiversity', '3. పర్యావరణ వ్యవస్థ, జీవవైవిధ్యం', [
       ('Basic concepts of ecology; ecosystem: components and types', 'జీవావరణ శాస్త్ర ప్రాథమిక భావనలు; పర్యావరణ వ్యవస్థ: అంశాలు, రకాలు'),
       ('Biodiversity: meaning, components, hotspots', 'జీవవైవిధ్యం: అర్థం, అంశాలు, హాట్‌స్పాట్‌లు'),
       ('Loss and conservation of biodiversity: methods, plans, targets, conventions and protocols', 'జీవవైవిధ్య నష్టం, సంరక్షణ: పద్ధతులు, ప్రణాళికలు, లక్ష్యాలు, ఒప్పందాలు, ప్రోటోకాల్‌లు'),
       ('Wildlife conservation: CITES and endangered species of India', 'వన్యప్రాణి సంరక్షణ: CITES, భారత అంతరించిపోతున్న జాతులు'),
       ('Biosphere reserves', 'జీవావరణ రిజర్వులు (బయోస్ఫియర్ రిజర్వులు)'),
       ('Indian wildlife conservation efforts, projects, Acts and initiatives', 'భారత వన్యప్రాణి సంరక్షణ ప్రయత్నాలు, ప్రాజెక్టులు, చట్టాలు, చొరవలు')], [CA, TODAY]),
     unit('st-4', '4. Waste management and pollution control', '4. వ్యర్థాల నిర్వహణ, కాలుష్య నియంత్రణ', [
       ('Solid wastes: classification, disposal and management in India', 'ఘన వ్యర్థాలు: వర్గీకరణ, తొలగింపు, నిర్వహణ'),
       ('Environmental pollution: types, sources and impacts', 'పర్యావరణ కాలుష్యం: రకాలు, వనరులు, ప్రభావాలు'),
       ('Pollution control, regulation and alternatives: recent projects, Acts, initiatives', 'కాలుష్య నియంత్రణ, నియమాలు, ప్రత్యామ్నాయాలు: ఇటీవలి ప్రాజెక్టులు, చట్టాలు, చొరవలు'),
       ('Transgenics: impact on environment and regulation', 'ట్రాన్స్‌జెనిక్స్: పర్యావరణంపై ప్రభావం, నియంత్రణ'),
       ('Eco-friendly technologies in agriculture', 'వ్యవసాయంలో పర్యావరణ హిత సాంకేతికతలు'),
       ('Bioremediation: types and scope in India', 'బయోరెమిడియేషన్: రకాలు, భారత్‌లో అవకాశాలు')]),
     unit('st-5', '5. Environment and health', '5. పర్యావరణం, ఆరోగ్యం', [
       ('Global warming, climate change, acid rain, ozone depletion, ocean acidification', 'భూతాపం, వాతావరణ మార్పు, ఆమ్ల వర్షం, ఓజోన్ క్షీణత, సముద్ర ఆమ్లీకరణ'),
       ('International initiatives, protocols and conventions on climate change; India\'s role', 'వాతావరణ మార్పుపై అంతర్జాతీయ చొరవలు, ప్రోటోకాల్‌లు, ఒప్పందాలు; భారత్ పాత్ర'),
       ('Sustainable development: meaning, nature, scope, components and goals', 'సుస్థిరాభివృద్ధి: అర్థం, స్వభావం, పరిధి, అంశాలు, లక్ష్యాలు'),
       ('Health: recent trends in disease burden; epidemic and pandemic challenges in India', 'ఆరోగ్యం: వ్యాధి భారంలో ఇటీవలి ధోరణులు; భారత్‌లో అంటువ్యాధులు, మహమ్మారి సవాళ్లు'),
       ('Preparedness and response: healthcare delivery and outcomes; recent public health initiatives', 'సన్నద్ధత, ప్రతిస్పందన: ఆరోగ్య సేవలు, ఫలితాలు; ఇటీవలి ప్రజారోగ్య కార్యక్రమాలు')], [CA])]}]}]

out = {'exam': T('APPSC Group 2', 'APPSC గ్రూప్ 2'),
       'src': T('Official syllabus annexed to APPSC Notification No. 37/2026 (dated 13/10/2026)', 'APPSC నోటిఫికేషన్ నం. 37/2026 (13/10/2026) కు జతచేసిన అధికారిక సిలబస్'),
       'pdf': 'Group2_Notification_37_2026.pdf', 'stages': stages}
os.makedirs(os.path.join(ROOT, 'syllabus'), exist_ok=True)
json.dump(out, open(os.path.join(ROOT, 'syllabus', 'group2.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
n = sum(len(u['t']) for s in stages for sec in s['sec'] for u in sec['u'])
print('topics', n, 'units', sum(len(sec['u']) for s in stages for sec in s['sec']))
