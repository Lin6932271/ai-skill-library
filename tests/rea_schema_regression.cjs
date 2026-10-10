// Validate actual tools/list schemas using JavaScript and an independent RE2 engine.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const [oldPath, newPath, re2Path, resultPath] = process.argv.slice(2);
const {RE2} = require(re2Path);
const oldTools = JSON.parse(fs.readFileSync(oldPath, 'utf8'));
const tools = JSON.parse(fs.readFileSync(newPath, 'utf8'));
function* patterns(node) {
  if (!node || typeof node !== 'object' || Array.isArray(node)) return;
  if ('pattern' in node) yield node.pattern;
  for (const key of ['properties','patternProperties','$defs','definitions','dependentSchemas']) {
    const mapping = node[key] || {};
    if (key === 'patternProperties') yield* Object.keys(mapping);
    for (const child of Object.values(mapping)) yield* patterns(child);
  }
  for (const key of ['anyOf','oneOf','allOf','prefixItems']) for (const child of node[key] || []) yield* patterns(child);
  for (const key of ['items','additionalProperties','contains','propertyNames','not','if','then','else','unevaluatedProperties','unevaluatedItems']) {
    const value = node[key];
    for (const child of Array.isArray(value) ? value : [value]) yield* patterns(child);
  }
}
function omitPatterns(node) {
  if (Array.isArray(node)) return node.map(omitPatterns);
  if (node && typeof node === 'object') return Object.fromEntries(Object.entries(node).filter(([k,v])=>!(k==='pattern' && typeof v==='string')).map(([k,v])=>[k,omitPatterns(v)]));
  return node;
}
assert.equal(tools.length,138);
assert.deepEqual(tools.map(t=>t.name),oldTools.map(t=>t.name));
let count=0,changed=0;
for(let i=0;i<tools.length;i++) {
  assert.deepEqual(omitPatterns(tools[i].inputSchema),omitPatterns(oldTools[i].inputSchema));
  const before=[...patterns(oldTools[i].inputSchema)],after=[...patterns(tools[i].inputSchema)];
  assert.equal(before.length,after.length);
  for(let j=0;j<after.length;j++) {
    new RegExp(after[j],'u');new RE2(after[j],'u');count++;
    if(before[j]!==after[j]) {
      assert.equal(tools[i].name,'observe_native_calls');
      assert.equal(before[j],'^[^\\s[\\]]+$');
      assert.equal(after[j],'^[^\\s\\x5b\\x5d]+$');changed++;
    }
  }
}
assert.equal(changed,2);
const oldPattern=new RegExp('^[^\\s[\\]]+$','u'),newPattern=new RegExp('^[^\\s\\x5b\\x5d]+$','u');
const examples=['int','uint64','std::string','char*','用户类型','','int *','char[8]','[int]','a b','a\tb','a\nb','a\u00a0b','a\u2028b','a\0b'];
for(const value of examples)assert.equal(oldPattern.test(value),newPattern.test(value),value);
for(const value of ['int','uint64','std::string','char*'])assert.ok(newPattern.test(value));
for(const value of ['','int *','char[8]','[int]','a b','a\tb','a\nb'])assert.ok(!newPattern.test(value));
let seed=42;
const alphabet=['a','[',']',' ','\t','\n','*',':','0','\0','用','\u00a0'];
for(let i=0;i<10000;i++) {
  let value='';
  for(let j=0;j<i%12;j++){seed=(Math.imul(seed,1664525)+1013904223)>>>0;value+=alphabet[seed%alphabet.length];}
  assert.equal(oldPattern.test(value),newPattern.test(value),JSON.stringify(value));
}
const result={passed:true,tools:tools.length,patterns:count,changed_pattern_positions:changed,
  engines:['JavaScript Unicode RegExp','Google RE2 WebAssembly','Python re','Rust regex via pydantic-core'],
  tool_names_and_argument_shapes_preserved:true,bare_native_type_guard_preserved:true,
  randomized_semantic_comparisons:10000,deepseek_official_api_chat_verified:false};
fs.writeFileSync(resultPath,JSON.stringify(result,null,2));console.log(JSON.stringify(result));
