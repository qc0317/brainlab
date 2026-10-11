"""Refresh mechanical audit fields without promoting scientific review status."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / 'data/alzheimer/delivery-audit.json'
audit = json.loads(path.read_text())
program = json.loads((ROOT / 'data/alzheimer/program.json').read_text())
counts = json.loads((ROOT / 'data/alzheimer/word-count.json').read_text())
knowledge = json.loads((ROOT / 'data/knowledge.json').read_text())
studies = json.loads((ROOT / 'data/alzheimer/trial-extractions.json').read_text())['studies']
chapter_counts = {x['id']: x['han_chars'] for x in counts['chapters']}
drafted = set(program['drafted_record_ids'])
audit['chapter_count'] = len(drafted)
audit['part_counts'] = [dict(id=p['id'], title=p['title'], han_chars=sum(chapter_counts[c['id']] for c in p['chapters'])) for p in program['parts']]
audit['chapters_without_tables'] = [r['title'] for r in knowledge['records'] if r['id'] in drafted and not any(s.get('table') for s in r['sections'])]
audit['extraction_records'] = len(studies)
audit['verified_extraction_records'] = sum(s['audit_status'] == 'verified' for s in studies)
path.write_text(json.dumps(audit, ensure_ascii=False, indent=2))
report = ROOT / 'research-programs/alzheimer/DELIVERY-AUDIT.md'
text = report.read_text()
req_start = text.index('|要求|')
req_end = text.index('## 四部分正文规模')
requirements = '|要求|当前状态|核验依据与剩余工作|\n|---|---|---|\n'
requirements += ''.join('|'+r['requirement']+'|'+r['status']+'|'+r['evidence'].replace('|', '／')+'|\n' for r in audit['requirements'])
text = text[:req_start]+requirements+'\n'+text[req_end:]
start = text.index('## 四部分正文规模')
end = text.index('计数只取', start)
table = '## 四部分正文规模\n\n|阅读主线|计数汉字|\n|---|---|\n'
table += ''.join('|'+p['title']+'|'+format(p['han_chars'], ',')+'|\n' for p in audit['part_counts'])
report.write_text(text[:start]+table+'\n'+text[end:])

# Preserve the original acquisition snapshot separately from current source metadata.
literature_path = ROOT / 'data/alzheimer/literature-audit.json'
literature = json.loads(literature_path.read_text())
if 'historical_acquisition_snapshot' not in literature:
    literature['historical_acquisition_snapshot'] = {
        'date': literature.get('date'),
        'scope': literature.get('scope'),
        'items': literature.pop('items', []),
        'interpretation': 'Historical XML retrieval results; unavailable here does not describe current reading access.',
    }
literature['status'] = 'ongoing'
literature['scope'] = 'Current canonical access metadata plus dated historical acquisition snapshot; no full scientific review certification'
literature['current_source_metadata'] = [
    {k: source[k] for k in ('id', 'title', 'url', 'reviewed', 'access', 'note', 'license', 'license_url') if k in source}
    for source in knowledge['sources']
]
literature['metadata_refresh_rule'] = 'Regenerated from data/knowledge.json; reviewed dates and access scope retained, not upgraded by building.'
literature_path.write_text(json.dumps(literature, ensure_ascii=False, indent=2)+'\n')
