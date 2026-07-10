from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'backend'))
from app.services.admin.admin_preview_enrichment import enrich_admin_preview

create=enrich_admin_preview({'domain':'items','normalizedDraft':{'name':'검','atk':10}},mode='create')
edit=enrich_admin_preview({'domain':'items','id':1,'acceptedChanges':[{'key':'atk','before':10,'after':12}]},mode='edit')
delete=enrich_admin_preview({'domain':'items','id':1,'changes':[{'key':'atk','after':12}]},mode='delete')
assert create['unifiedDiffCount']==2
assert edit['unifiedDiff'][0]['path']=='$.atk'
assert delete['rollbackSnapshot']['before']=={'atk':12}
assert delete['rollbackSnapshot']['after']=={}
assert create['previewSchemaVersion']==1
print('[OK] backend admin preview unified diff/snapshot integration')
