"use strict";
const $ = (selector) => document.querySelector(selector);
const esc = (value) => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const token = $('meta[name="pojia-local-token"]').content;
let state = null;
let busy = new Set();
const advancedProfiles = new Set();
let toastTimer;

// The supplied movie plays once; decoding failures cannot trap the app on startup.
const startupVideo = $('#startup-video');
window.startupStatus = {playing: false, completed: false, reason: null, elapsed: 0, duration: 0};
let startupFinished = false;
let startupTimer;
async function finishStartup(reason) {
  if (startupFinished) return;
  startupFinished = true;
  clearTimeout(startupTimer);
  Object.assign(window.startupStatus, {completed: true, reason,
    elapsed: startupVideo.currentTime, duration: startupVideo.duration || 0});
  startupVideo.pause();
  try {
    const frame = await api('finish_startup');
    window.startupStatus.native_frame_restored = frame.restored;
  } catch (error) {
    window.startupStatus.frame_error = error.message;
  }
  $('#startup').classList.add('leaving');
  setTimeout(() => {
    $('#startup').hidden = true;
    $('#app-shell').inert = false;
    document.documentElement.classList.remove('starting');
    document.body.classList.remove('starting');
  }, 200);
}
startupVideo.addEventListener('playing', () => { window.startupStatus.playing = true; });
startupVideo.addEventListener('ended', () => finishStartup('ended'));
startupVideo.addEventListener('error', () => finishStartup('media-error'));
startupVideo.addEventListener('loadedmetadata', () => {
  window.startupStatus.duration = startupVideo.duration;
  clearTimeout(startupTimer);
  startupTimer = setTimeout(() => finishStartup('playback-timeout'),
    Math.max(15000, (startupVideo.duration + 8) * 1000));
});
startupTimer = setTimeout(() => finishStartup('load-timeout'), 15000);
startupVideo.muted = true;
startupVideo.play().catch(() => finishStartup('playback-unavailable'));

async function api(command, args = {}) {
  const response = await fetch('/api', {method: 'POST', headers: {'Content-Type': 'application/json', 'X-Pojia-Local': token}, body: JSON.stringify({command, args})});
  const value = await response.json();
  if (!value.ok) throw new Error(value.error || '本地操作未完成');
  return value.data;
}
function toast(message) {
  $('#toast').textContent = message;
  $('#toast').hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { $('#toast').hidden = true; }, 6000);
}
function modal(title, body) {
  $('#modal-title').textContent = title;
  $('#modal-body').innerHTML = body;
  if (!$('#modal').open) $('#modal').showModal();
}
$('#modal-close').onclick = () => $('#modal').close();
$('#modal').addEventListener('click', event => { if (event.target === $('#modal')) $('#modal').close(); });

function render() {
  if (!state) return;
  $('.version').textContent = `v${state.version}`;
  $('#library-banner-title').textContent = '原版 / 精品技能，REA 已内置';
  $('#library-banner-summary').textContent = `关为原版 ${state.builtin_documents} 项，开为精品 ${state.premium_suite_documents} 项。每个客户端独立保存选择。`;
  $('#service-grid').innerHTML = state.providers.map(p => {
    const healthy = p.installed && p.verification.ok;
    const icon = p.icon === 'codex' ? '<span class="codex-icon">✺</span>' : `<img src="/assets/${esc(p.icon)}" class="pj-service-image-mark" alt="">`;
    const disabled = busy.has(p.key) ? 'disabled' : '';
    const selected = state.profiles.find(profile => profile.id === p.profile);
    const selectedName = selected?.name || p.profile;
    const premium = p.profile === 'premium' || p.profile.startsWith('premium-');
    const suiteProfile = premium ? 'premium' : 'builtin';
    const suiteName = state.profiles.find(profile => profile.id === suiteProfile)?.name || selectedName;
    return `<article class="pj-service-card" id="service-card-${p.key}">
      <header class="pj-service-head"><div class="pj-service-mark pj-service-mark--${p.key.split('_')[0]}">${icon}</div><div class="pj-service-title"><h3>${esc(p.name)}</h3><p>${p.instruction}</p></div><div class="edition-control"><button class="switch edition-switch ${premium ? 'on' : ''}" role="switch" aria-checked="${premium}" aria-label="${esc(p.name)} 精品技能" title="关为原版技能，开为精品技能" data-action="toggle-edition" data-provider="${p.key}" ${disabled}></button><span>${premium ? '精品技能' : '原版技能'}</span></div><span class="status-badge ${healthy ? 'good' : p.installed ? 'warning' : ''}">${healthy ? '已写入' : p.installed ? '需检查' : '未安装'}</span></header>
      <div class="pj-service-activation"><span class="pj-activation-word">hi</span><span class="pj-activation-arrow">→</span><span class="pj-activation-reply">在新会话确认技能读取</span></div>
      <div class="path-row"><span class="path-label">配置目录</span><span class="path-value" title="${esc(p.path)}">${esc(p.path)}</span><button class="path-button" data-action="directory" data-provider="${p.key}" ${disabled}>设置</button></div>
      <div class="profile-summary"><span>${p.installed ? '当前使用' : '待启用'}：${esc(selectedName)}</span>${p.needs_skill_update ? `<button class="text-button" data-action="use-suite" data-provider="${p.key}" data-profile="${esc(p.profile)}" ${disabled}>更新当前方案</button>` : p.profile !== suiteProfile ? `<button class="text-button" data-action="use-suite" data-provider="${p.key}" data-profile="${suiteProfile}" ${disabled}>使用整套${premium ? '精品' : '原版'}技能</button>` : `<span class="edition-hint">${esc(suiteName.split(' · ')[1] || '')}</span>`}</div>
      <details class="profile-advanced" data-provider="${p.key}" ${advancedProfiles.has(p.key) ? 'open' : ''}><summary>高级选项</summary><div class="profile-row"><label for="profile-${p.key}">自定义方案</label><select id="profile-${p.key}" class="profile-select" data-provider="${p.key}" ${disabled}>${state.profiles.map(profile => `<option value="${profile.id}" ${profile.id === p.profile ? 'selected' : ''}>${esc(profile.name)}</option>`).join('')}</select></div></details>
      <div class="card-action"><div class="switch-group"><button class="switch ${p.installed ? 'on' : ''}" role="switch" aria-checked="${p.installed}" aria-label="${esc(p.name)} 技能" data-action="toggle" data-provider="${p.key}" ${disabled}></button><span>${busy.has(p.key) ? '处理中…' : p.installed ? '技能已开启' : '开启技能'}</span></div><div class="card-links"><button class="text-button" data-action="verify" data-provider="${p.key}" ${disabled}>检查</button><button class="text-button" data-action="open" data-provider="${p.key}" ${disabled}>打开目录</button></div></div>
      <div class="card-note">${esc(p.rea_recovery_available ? '发现本软件遗留的 REA 连接，可先备份再修复。' : p.installed ? p.verification.summary : '开启后自动准备 REA，首次写入自动备份。')}${p.rea_recovery_available ? ` <button class="text-button" data-action="repair-rea" data-provider="${p.key}" ${disabled}>修复并开启技能</button>` : p.installed && (!p.rea || p.rea_needs_update) ? ` <button class="text-button" data-action="prepare-rea" data-provider="${p.key}" ${disabled}>${p.rea_needs_update ? '更新 REA' : '启用 REA'}</button>` : ''}</div>
    </article>`;
  }).join('');
  renderLibrary();
  $('#runtime-info').innerHTML = `<dt>程序版本</dt><dd>${esc(state.version)}</dd><dt>REA</dt><dd>${esc(state.rea_runtime?.version || '未内置')} · 开启技能时自动准备</dd><dt>网络模式</dt><dd>安装过程离线完成 · 仅本机界面通信</dd><dt>技能方案</dt><dd>开关关闭：原版；开关开启：精品；按客户端保存</dd><dt>数据目录</dt><dd>${esc(state.data_dir)}</dd><dt>验收范围</dt><dd>文件和 REA 启动测试；客户端连接需重启后确认</dd>`;
  const actions = {inject: '写入技能', revoke: '撤销技能', import: '导入技能'};
  $('#events').innerHTML = state.events.length ? state.events.map(event => `<div class="event"><time>${esc(event.time)}</time><span>${esc(actions[event.action] || event.action)}</span><span>${esc(state.providers.find(p => p.key === event.provider)?.name || event.detail)}</span></div>`).join('') : '<p class="footnote">暂无操作记录</p>';
}
function renderLibrary() {
  if (!state) return;
  const query = $('#skill-search').value.trim().toLowerCase();
  const category = $('#skill-category').value;
  const collection = $('#skill-collection').value;
  const recommended = new Map();
  for (const profile of state.profiles) {
    if (profile.skill_name && profile.collection === (collection === 'premium-suite' ? 'premium' : 'builtin')) recommended.set(profile.skill_name, profile);
  }
  const suiteCollection = collection === 'recommended' || collection === 'premium-suite';
  const candidates = suiteCollection
    ? [state.profiles.find(profile => profile.id === (collection === 'premium-suite' ? 'premium' : 'builtin')), ...recommended.values(), ...(collection === 'premium-suite' ? state.premium_missing.map(item => ({...item, name: item.name || item.skill_name, collection: 'premium', category: item.category || '其他', description: '服务器目录中存在，正文待取回', unavailable: true})) : [])]
    : state.profiles;
  const profiles = candidates.filter(p => (!category || (p.category || '其他') === category) &&
    (suiteCollection || !collection || (collection === 'other' ? !p.collection : p.collection === collection)) &&
    [p.name, p.skill_name || '', p.description, ...(p.keywords || [])].join(' ').toLowerCase().includes(query));
  $('#skill-library').innerHTML = profiles.map(profile => `<article class="library-card"><span class="chip">${profile.unavailable ? '待取回' : profile.collection === 'extension' ? '扩展技能 · ' + esc(profile.category) : profile.builtin ? esc(profile.category || '内置方案') : '已导入'}</span><h2>${esc(profile.name)}</h2>${profile.skill_name ? `<code>${esc(profile.skill_name)}</code>` : ''}<p>${esc(profile.description)}</p><button class="button" data-action="preview" data-profile="${esc(profile.id)}" ${profile.unavailable ? 'disabled' : ''}>${profile.unavailable ? '正文尚未取回' : '查看技能正文'}</button></article>`).join('');
  $('#skill-count').textContent = `显示 ${profiles.length} / ${candidates.length} 项`;
}
$('#skill-search').oninput = renderLibrary;
$('#skill-category').onchange = renderLibrary;
$('#skill-collection').onchange = renderLibrary;
async function refresh() {
  state = await api('status');
  render();
}
async function runProvider(key, action) {
  if (busy.has(key)) return;
  busy.add(key); render();
  const progressTimer = setInterval(async () => {
    try {
      const progress = await api('rea_progress');
      const note = $(`#service-card-${key} .card-note`);
      if (note && busy.has(key) && progress.message) note.textContent = `${progress.message} ${progress.percent ? progress.percent + '%' : ''}`;
    } catch (_) { /* The main action reports failures. */ }
  }, 500);
  try { await action(); await refresh(); } catch (error) { toast(error.message); }
  finally { clearInterval(progressTimer); busy.delete(key); render(); }
}
async function toggle(key) {
  const p = state.providers.find(p => p.key === key);
  if (p.installed) {
    modal(`撤销 ${p.name} 的技能`, '<div class="modal-content">移除本助手写入的管理段和技能文件，保留原有配置。外部修改会保留并报告冲突。</div><div class="modal-actions"><button id="confirm-revoke" class="button danger">确认撤销</button></div>');
    $('#confirm-revoke').onclick = () => { $('#modal').close(); runProvider(key, async () => { const result = await api('revoke', {provider: key}); toast(result.removed ? '已撤销，原有配置已保留' : `存在外部修改，已保留：${result.conflicts.join('；')}`); }); };
  } else {
    const profile = $(`#profile-${key}`).value;
    await runProvider(key, async () => { await api('inject', {provider: key, profile}); toast('技能和 REA 已准备好，重启客户端后即可使用'); });
  }
}
async function chooseProfile(key, profile) {
  await runProvider(key, async () => {
    const installed = state.providers.find(p => p.key === key).installed;
    await api('select_profile', {provider: key, profile});
    toast(installed ? '技能方案已切换，请新建客户端会话' : '技能方案已保存，开启技能后生效');
  });
}
function directory(key) {
  const p = state.providers.find(p => p.key === key);
  modal(`${p.name} · 配置目录`, `<div class="modal-content"><p>选择实际客户端读取的配置目录。目录切换前需撤销当前安装。</p><input class="field" id="directory-path" value="${esc(p.path)}" aria-label="配置目录"><p>将写入 ${esc(p.instruction)} 与 skills/ 内所选技能目录；已有同名文件会报告冲突。</p></div><div class="modal-actions"><button id="browse-directory" class="button">浏览文件夹</button><button id="default-directory" class="button">自动检测</button><button id="save-directory" class="button primary">保存目录</button></div>`);
  $('#browse-directory').onclick = async () => { try { const result = await api('pick_directory'); if (result.path) $('#directory-path').value = result.path; } catch (e) { toast(e.message); } };
  const save = async (path) => { try { await api('set_path', {provider: key, path}); $('#modal').close(); await refresh(); toast('目录已保存'); } catch (e) { toast(e.message); } };
  $('#save-directory').onclick = () => save($('#directory-path').value.trim());
  $('#default-directory').onclick = () => save('');
}
async function verify(key) {
  const p = state.providers.find(p => p.key === key);
  const result = await api('verify', {provider: key});
  modal(`${p.name} · 状态检查`, `<div class="modal-content"><p>${esc(result.summary)}</p>${result.checks.map(check => `<div class="check ${check.ok ? '' : 'failed'}"><b>${check.ok ? '✓' : '!'}</b><div>${esc(check.name)}<small>${esc(check.path || check.detail || '')}</small></div></div>`).join('')}<p>重启客户端后，直接说“使用技能”并描述任务即可，无需记住技能名称。REA 启动测试通过还不代表当前聊天已经连接；EXE/DLL 深度反编译仍需要相应分析引擎。</p></div>`);
}
document.addEventListener('click', async event => {
  const button = event.target.closest('[data-action]');
  if (!button || button.disabled) return;
  const key = button.dataset.provider;
  try {
    switch (button.dataset.action) {
      case 'toggle': await toggle(key); break;
      case 'toggle-edition': {
        const provider = state.providers.find(p => p.key === key);
        const premium = provider.profile === 'premium' || provider.profile.startsWith('premium-');
        await chooseProfile(key, premium ? 'builtin' : 'premium');
        break;
      }
      case 'use-suite': await chooseProfile(key, button.dataset.profile); break;
      case 'prepare-rea': await runProvider(key, async () => { await api('inject', {provider: key, profile: state.providers.find(p => p.key === key).profile}); toast('REA 已准备好，请退出并重新打开 AI 客户端'); }); break;
      case 'repair-rea': await runProvider(key, async () => { await api('repair_rea', {provider: key, profile: $(`#profile-${key}`).value}); toast('已备份并修复，请退出并重新打开 AI 客户端'); }); break;
      case 'directory': directory(key); break;
      case 'verify': await verify(key); break;
      case 'open': await api('open_directory', {provider: key}); break;
      case 'preview': { const result = await api('read_profile', {profile: button.dataset.profile}); modal('技能正文', `<pre class="skill-content">${esc(result.content)}</pre><p class="footnote">包含 ${result.files.length} 个资源文件。可编辑源码中的 skills/，或重新导入自己的技能。</p>`); break; }
    }
  } catch (error) { toast(error.message); }
});
document.addEventListener('change', async event => {
  if (!event.target.matches('.profile-select')) return;
  const key = event.target.dataset.provider;
  const profile = event.target.value;
  const p = state.providers.find(p => p.key === key);
  await chooseProfile(key, profile);
});
document.addEventListener('toggle', event => {
  const details = event.target;
  if (!details.matches?.('.profile-advanced') || !details.isConnected) return;
  if (details.open) advancedProfiles.add(details.dataset.provider);
  else advancedProfiles.delete(details.dataset.provider);
}, true);
document.querySelectorAll('[data-page]').forEach(button => { button.onclick = () => {
  document.querySelectorAll('[data-page]').forEach(b => b.classList.toggle('active', b === button));
  document.querySelectorAll('.page').forEach(page => { page.hidden = page.id !== `${button.dataset.page}-page`; });
  window.scrollTo(0, 0);
}; });
$('#refresh').onclick = async () => { try { await refresh(); toast('状态已刷新'); } catch (e) { toast(e.message); } };
$('#theme').onclick = () => { const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'; document.documentElement.dataset.theme = theme; localStorage.setItem('pojia-local-theme', theme); };
document.documentElement.dataset.theme = localStorage.getItem('pojia-local-theme') || 'light';
$('#guide').onclick = () => modal('使用技能', '<div class="modal-content"><p>1. 在客户端卡片上选择技能方案：上方开关关闭为原版技能，开启为精品技能。每个客户端独立保存选择。</p><p>2. 再开启下方“开启技能”开关。已安装时，切换上方方案会自动备份并替换该客户端的技能。</p><p>3. 等待“REA 已就绪”，退出并重新打开 AI 客户端，再新建会话。只有需要单项技能或导入方案时才展开高级选项。</p><p>4. 直接说“使用技能”并描述目标与文件位置。关闭下方技能开关可以撤销，原有配置和外部修改会保留。</p><p>REA 基础工具已内置；EXE/DLL 深度反编译需要相应分析引擎。实际加载需要在新会话确认。</p></div>');
$('#import').onclick = () => {
  modal('导入技能', '<div class="modal-content"><p>支持 Markdown 文件、含 SKILL.md 的文件夹或 ZIP。文件夹/ZIP 可包含 references/ 与 scripts/；每次导入一个技能。</p><input id="import-path" class="field" placeholder="填写技能文件或文件夹的完整路径" aria-label="技能路径"></div><div class="modal-actions"><button id="browse-skill-folder" class="button">选择文件夹</button><button id="browse-skill-file" class="button">选择文件</button><button id="confirm-import" class="button primary">导入</button></div>');
  const browse = async command => { try { const result = await api(command); if (result.path) $('#import-path').value = result.path; } catch (e) { toast(e.message); } };
  $('#browse-skill-folder').onclick = () => browse('pick_skill_directory');
  $('#browse-skill-file').onclick = () => browse('pick_skill');
  $('#confirm-import').onclick = async () => { try { const result = await api('import_skill', {path: $('#import-path').value.trim()}); $('#modal').close(); await refresh(); toast(`已导入：${result.name}`); } catch (e) { toast(e.message); } };
};
$('#export').onclick = async () => { try { const result = await api('export_diagnostics'); if (result.path) toast(`已保存：${result.path}`); else if (!result.cancelled) { const blob = new Blob([JSON.stringify(result, null, 2)], {type: 'application/json'}); const a = document.createElement('a'); const url = URL.createObjectURL(blob); a.href = url; a.download = 'ai技能库-诊断.json'; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000); } } catch (e) { toast(e.message); } };
refresh().catch(error => toast(`界面连接失败：${error.message}`));
