"use strict";
const $ = (selector) => document.querySelector(selector);
const esc = (value) => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const token = $('meta[name="pojia-local-token"]').content;
let state = null;
let busy = new Set();
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
  $('#library-banner-title').textContent = `${state.builtin_documents} 项技能，REA 已内置`;
  $('#library-banner-summary').textContent = '开启技能时自动准备 REA 和连接；告诉 AI“使用技能”即可，无需自己配置。';
  $('#service-grid').innerHTML = state.providers.map(p => {
    const healthy = p.installed && p.verification.ok;
    const icon = p.icon === 'codex' ? '<span class="codex-icon">✺</span>' : `<img src="/assets/${esc(p.icon)}" class="pj-service-image-mark" alt="">`;
    const disabled = busy.has(p.key) ? 'disabled' : '';
    return `<article class="pj-service-card" id="service-card-${p.key}">
      <header class="pj-service-head"><div class="pj-service-mark pj-service-mark--${p.key.split('_')[0]}">${icon}</div><div class="pj-service-title"><h3>${esc(p.name)}</h3><p>${p.instruction}</p></div><span class="status-badge ${healthy ? 'good' : p.installed ? 'warning' : ''}">${healthy ? '已写入' : p.installed ? '需检查' : '未安装'}</span></header>
      <div class="pj-service-activation"><span class="pj-activation-word">hi</span><span class="pj-activation-arrow">→</span><span class="pj-activation-reply">在新会话确认技能读取</span></div>
      <div class="path-row"><span class="path-label">配置目录</span><span class="path-value" title="${esc(p.path)}">${esc(p.path)}</span><button class="path-button" data-action="directory" data-provider="${p.key}" ${disabled}>设置</button></div>
      <div class="profile-row"><label for="profile-${p.key}">技能方案</label><select id="profile-${p.key}" class="profile-select" data-provider="${p.key}" ${disabled}>${state.profiles.map(profile => `<option value="${profile.id}" ${profile.id === p.profile ? 'selected' : ''}>${esc(profile.name)}</option>`).join('')}</select></div>
      <div class="card-action"><div class="switch-group"><button class="switch ${p.installed ? 'on' : ''}" role="switch" aria-checked="${p.installed}" aria-label="${esc(p.name)} 技能" data-action="toggle" data-provider="${p.key}" ${disabled}></button><span>${busy.has(p.key) ? '处理中…' : p.installed ? '技能已开启' : '开启技能'}</span></div><div class="card-links"><button class="text-button" data-action="verify" data-provider="${p.key}" ${disabled}>检查</button><button class="text-button" data-action="open" data-provider="${p.key}" ${disabled}>打开目录</button></div></div>
      <div class="card-note">${esc(p.installed ? p.verification.summary : '开启后自动准备 REA，首次写入自动备份。')}${p.installed && !p.rea ? ` <button class="text-button" data-action="prepare-rea" data-provider="${p.key}" ${disabled}>启用 REA</button>` : ''}</div>
    </article>`;
  }).join('');
  renderLibrary();
  $('#runtime-info').innerHTML = `<dt>程序版本</dt><dd>${esc(state.version)}</dd><dt>REA</dt><dd>${esc(state.rea_runtime?.version || '未内置')} · 开启技能时自动准备</dd><dt>网络模式</dt><dd>安装过程离线完成 · 仅本机界面通信</dd><dt>技能方案</dt><dd>${state.profiles.length} 个</dd><dt>数据目录</dt><dd>${esc(state.data_dir)}</dd><dt>验收范围</dt><dd>文件和 REA 启动测试；客户端连接需重启后确认</dd>`;
  const actions = {inject: '写入技能', revoke: '撤销技能', import: '导入技能'};
  $('#events').innerHTML = state.events.length ? state.events.map(event => `<div class="event"><time>${esc(event.time)}</time><span>${esc(actions[event.action] || event.action)}</span><span>${esc(state.providers.find(p => p.key === event.provider)?.name || event.detail)}</span></div>`).join('') : '<p class="footnote">暂无操作记录</p>';
}
function renderLibrary() {
  if (!state) return;
  const query = $('#skill-search').value.trim().toLowerCase();
  const category = $('#skill-category').value;
  const collection = $('#skill-collection').value;
  const profiles = state.profiles.filter(p => (!category || (p.category || '其他') === category) &&
    (!collection || (collection === 'other' ? !p.collection : p.collection === collection)) &&
    [p.name, p.skill_name || '', p.description, ...(p.keywords || [])].join(' ').toLowerCase().includes(query));
  $('#skill-library').innerHTML = profiles.map(profile => `<article class="library-card"><span class="chip">${profile.collection === 'extension' ? '扩展技能 · ' + esc(profile.category) : profile.builtin ? esc(profile.category || '内置方案') : '已导入'}</span><h2>${esc(profile.name)}</h2>${profile.skill_name ? `<code>${esc(profile.skill_name)}</code>` : ''}<p>${esc(profile.description)}</p><button class="button" data-action="preview" data-profile="${esc(profile.id)}">查看技能正文</button></article>`).join('');
  $('#skill-count').textContent = `显示 ${profiles.length} / ${state.profiles.length} 项`;
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
      case 'prepare-rea': await runProvider(key, async () => { await api('inject', {provider: key, profile: state.providers.find(p => p.key === key).profile}); toast('REA 已准备好，请退出并重新打开 AI 客户端'); }); break;
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
  if (p.installed) await runProvider(key, async () => { await api('inject', {provider: key, profile}); toast('技能方案已切换，请新建客户端会话'); });
});
document.querySelectorAll('[data-page]').forEach(button => { button.onclick = () => {
  document.querySelectorAll('[data-page]').forEach(b => b.classList.toggle('active', b === button));
  document.querySelectorAll('.page').forEach(page => { page.hidden = page.id !== `${button.dataset.page}-page`; });
  window.scrollTo(0, 0);
}; });
$('#refresh').onclick = async () => { try { await refresh(); toast('状态已刷新'); } catch (e) { toast(e.message); } };
$('#theme').onclick = () => { const theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'; document.documentElement.dataset.theme = theme; localStorage.setItem('pojia-local-theme', theme); };
document.documentElement.dataset.theme = localStorage.getItem('pojia-local-theme') || 'light';
$('#guide').onclick = () => modal('使用技能', '<div class="modal-content"><p>1. 找到你使用的 AI 客户端，保留默认的“完整技能库”，点击开启技能。</p><p>2. 等待“REA 已就绪”。首次开启会自动释放内置环境、写入连接并完成启动测试，无需安装 Node 或配置 MCP。</p><p>3. 退出并重新打开 AI 客户端，直接说“使用技能分析这个软件”或“使用技能修复这个问题”，再说明文件位置和目标。</p><p>4. AI 会自动选择相关技能，你不用知道技能名称。关闭开关可以撤销技能和本软件的 REA 连接；原有配置和外部修改会保留。</p><p>REA 基础工具已内置；EXE/DLL 深度反编译需要另有 IDA/Ghidra，Android 等分析也有各自运行条件。不同客户端版本的实际加载需要在新会话确认。</p></div>');
$('#import').onclick = () => {
  modal('导入技能', '<div class="modal-content"><p>支持 Markdown 文件、含 SKILL.md 的文件夹或 ZIP。文件夹/ZIP 可包含 references/ 与 scripts/；每次导入一个技能。</p><input id="import-path" class="field" placeholder="填写技能文件或文件夹的完整路径" aria-label="技能路径"></div><div class="modal-actions"><button id="browse-skill-folder" class="button">选择文件夹</button><button id="browse-skill-file" class="button">选择文件</button><button id="confirm-import" class="button primary">导入</button></div>');
  const browse = async command => { try { const result = await api(command); if (result.path) $('#import-path').value = result.path; } catch (e) { toast(e.message); } };
  $('#browse-skill-folder').onclick = () => browse('pick_skill_directory');
  $('#browse-skill-file').onclick = () => browse('pick_skill');
  $('#confirm-import').onclick = async () => { try { const result = await api('import_skill', {path: $('#import-path').value.trim()}); $('#modal').close(); await refresh(); toast(`已导入：${result.name}`); } catch (e) { toast(e.message); } };
};
$('#export').onclick = async () => { try { const result = await api('export_diagnostics'); if (result.path) toast(`已保存：${result.path}`); else if (!result.cancelled) { const blob = new Blob([JSON.stringify(result, null, 2)], {type: 'application/json'}); const a = document.createElement('a'); const url = URL.createObjectURL(blob); a.href = url; a.download = 'ai技能库-诊断.json'; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000); } } catch (e) { toast(e.message); } };
refresh().catch(error => toast(`界面连接失败：${error.message}`));
