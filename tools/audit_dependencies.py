"""Inventory application Python dependencies and bundled npm versions; query OSV."""
from pathlib import Path
import argparse
import ast
import importlib.metadata as metadata
import json
import re
import platform
import urllib.request
import zipfile
from datetime import datetime, timezone
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

parser = argparse.ArgumentParser()
parser.add_argument('--out',type=Path,required=True)
args = parser.parse_args()
SRC = Path(__file__).resolve().parents[1]
args.out.mkdir(parents=True,exist_ok=True)
runtime = json.loads((SRC/'runtime/manifest.json').read_text('utf-8'))
pins = [Requirement(line) for line in (SRC/'requirements.txt').read_text('utf-8').splitlines() if line.strip() and not line.startswith('#')]
python_components = {}
queue = [requirement.name for requirement in pins if canonicalize_name(requirement.name) != 'pyinstaller']
unknown = []
while queue:
    name = queue.pop(0)
    key = canonicalize_name(name)
    if key in python_components:continue
    try:distribution = metadata.distribution(name)
    except metadata.PackageNotFoundError:
        unknown.append({'name':name,'reason':'Not installed in the build environment'});continue
    dependencies=[]
    for specification in distribution.requires or []:
        dependency = Requirement(specification)
        if dependency.marker and not dependency.marker.evaluate({'extra':''}):continue
        dependencies.append(str(dependency))
        queue.append(dependency.name)
    python_components[key]={'name':distribution.metadata['Name'],'version':distribution.version,
        'ecosystem':'PyPI','dependencies':dependencies,'evidence':'Build-environment metadata of declared application dependency closure'}

npm = {}
with zipfile.ZipFile(SRC/'runtime'/runtime['archive']) as bundle:
    for name in bundle.namelist():
        if not re.search(r'/node_modules/(?:@[^/]+/)?[^/]+/package\.json$',name):continue
        value=json.loads(bundle.read(name))
        if not isinstance(value.get('name'),str) or not isinstance(value.get('version'),str):
            unknown.append({'path':name,'reason':'Package metadata lacks name or version'});continue
        key=(value['name'],value['version'])
        row=npm.setdefault(key,{'name':value['name'],'version':value['version'],'ecosystem':'npm',
            'package_manifests':[],'evidence':'Packaged runtime ZIP bytes'})
        row['package_manifests'].append(name)
components=sorted(python_components.values(),key=lambda row:row['name'])+sorted(npm.values(),key=lambda row:(row['name'],row['version']))
source_ast=ast.parse((SRC/'backend.py').read_text('utf-8'))
version=next(node.value.value for node in source_ast.body if isinstance(node,ast.Assign)
    and any(isinstance(target,ast.Name) and target.id=='VERSION' for target in node.targets))
sbom={'schema':1,'application_version':version,'generated_utc':datetime.now(timezone.utc).isoformat(),
    'python_runtime':platform.python_version(),'node_runtime':runtime.get('node_version'),'rea_version':runtime.get('rea_version'),
    'python_components':len(python_components),'npm_components':len(npm),'components':components,
    'unknown_components':unknown,'limitations':['Python closure uses the corresponding build environment; optional dependencies and unlisted native code are not a complete binary SBOM.',
        'Node runtime and OS-provided native libraries are outside the PyPI/npm OSV query scope.']}
(args.out/'dependency-sbom.json').write_text(json.dumps(sbom,ensure_ascii=False,indent=2),'utf-8')
queries=[{'package':{'name':row['name'],'ecosystem':row['ecosystem']},'version':row['version']} for row in components]
request=urllib.request.Request('https://api.osv.dev/v1/querybatch',data=json.dumps({'queries':queries}).encode('utf-8'),
    headers={'Content-Type':'application/json','User-Agent':'AISkillLibrary-Security-Audit'})
result={'service':'OSV','queried_utc':datetime.now(timezone.utc).isoformat(),'queried_components':len(queries),'query_complete':False,'findings':[]}
try:
    with urllib.request.urlopen(request,timeout=60) as response:answers=json.loads(response.read())
    assert len(answers['results'])==len(components)
    for component,answer in zip(components,answers['results']):
        if answer.get('next_page_token'):
            result['pagination_required']=True
        if answer.get('vulns'):
            result['findings'].append({'component':component['name'],'version':component['version'],
                'ecosystem':component['ecosystem'],'advisory_ids':[row['id'] for row in answer['vulns']]})
    result['query_complete']=not result.get('pagination_required',False)
except Exception as exc:
    result['error']=type(exc).__name__+': '+str(exc)
result['limitations']='Database matches are candidate known-advisory matches; product reachability and exploitability are not established. No-match is not a security guarantee.'
(args.out/'dependency-osv.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf-8')
print(json.dumps({'python_components':len(python_components),'npm_components':len(npm),
    'osv_query_complete':result['query_complete'],'matched_components':len(result['findings']),'error':result.get('error')},ensure_ascii=False),flush=True)
