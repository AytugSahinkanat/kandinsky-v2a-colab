'use strict';
const study = JSON.parse(document.getElementById('study').textContent);
const $ = id => document.getElementById(id);
const sceneById = new Map(study.scenes.map(scene => [scene.id, scene]));
const storageKey = 'kandinsky-v2a-review-v2:' + study.study_id;
let state;

function uid() {
  const bytes = new Uint8Array(16);
  crypto.getRandomValues(bytes);
  return [...bytes].map(value => value.toString(16).padStart(2, '0')).join('');
}
function shuffle(values) {
  const result = [...values];
  for (let i = result.length - 1; i > 0; i--) {
    const bytes = new Uint32Array(1);
    crypto.getRandomValues(bytes);
    const j = bytes[0] % (i + 1);
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
}
function newAnswer(sceneId) {
  return { scene_id: sceneId, audio_id: sceneById.get(sceneId).audio_id,
    event_fit: null, sync: null, audio_quality: null, artifact_severity: null,
    unwanted_music_or_speech: null, would_use: null, note: '' };
}
function fresh() {
  return { schema: 'kandinsky-v2a-listening-response-v2', study_id: study.study_id,
    participant_id: uid(), alias: '', device: 'unspecified', consent_acknowledged: false,
    scene_order: shuffle(study.scenes.map(scene => scene.id)), index: 0,
    updated_at: new Date().toISOString(), answers: study.scenes.map(scene => newAnswer(scene.id)) };
}
function validate(value) {
  if (!value || value.schema !== 'kandinsky-v2a-listening-response-v2' || value.study_id !== study.study_id)
    throw Error('This response file belongs to a different study.');
  const ids = new Set(study.scenes.map(scene => scene.id));
  if (!/^[a-f0-9]{32}$/.test(value.participant_id) || !Array.isArray(value.scene_order) ||
      value.scene_order.length !== ids.size || new Set(value.scene_order).size !== ids.size ||
      value.scene_order.some(id => !ids.has(id))) throw Error('Invalid participant or scene order.');
  if (!Array.isArray(value.answers) || value.answers.length !== ids.size ||
      new Set(value.answers.map(answer => answer.scene_id)).size !== ids.size ||
      value.answers.some(answer => !ids.has(answer.scene_id))) throw Error('Scene answers are missing or duplicated.');
  for (const scene of study.scenes) {
    const answer = value.answers.find(item => item.scene_id === scene.id);
    if (answer.audio_id !== scene.audio_id) throw Error('The audio reference for a scene is invalid.');
    for (const key of ['event_fit', 'sync', 'audio_quality', 'artifact_severity']) {
      if (answer[key] !== null && (!Number.isInteger(answer[key]) || answer[key] < 1 || answer[key] > 5))
        throw Error('Ratings must be from 1 to 5.');
    }
    if (answer.unwanted_music_or_speech !== null && typeof answer.unwanted_music_or_speech !== 'boolean')
      throw Error('Unwanted-sound answer is invalid.');
    if (answer.would_use !== null && !['yes', 'after_edit', 'no'].includes(answer.would_use))
      throw Error('Use decision is invalid.');
    if (typeof answer.note !== 'string' || answer.note.length > 1000) throw Error('Scene note is invalid.');
  }
  if (typeof value.alias !== 'string' || value.alias.length > 60 ||
      !['unspecified', 'headphones', 'speakers', 'phone'].includes(value.device) ||
      typeof value.consent_acknowledged !== 'boolean' || !Number.isInteger(value.index) ||
      value.index < 0 || value.index >= ids.size) throw Error('Participant details are invalid.');
  return value;
}
try { state = validate(JSON.parse(localStorage.getItem(storageKey) || 'null')); }
catch { state = fresh(); }

function currentId() { return state.scene_order[state.index]; }
function answerFor(sceneId = currentId()) { return state.answers.find(answer => answer.scene_id === sceneId); }
function complete(answer) {
  return ['event_fit', 'sync', 'audio_quality', 'artifact_severity', 'unwanted_music_or_speech', 'would_use']
    .every(key => answer[key] !== null);
}
function save() {
  state.updated_at = new Date().toISOString();
  try { localStorage.setItem(storageKey, JSON.stringify(state)); $('saved').textContent = 'Saved in this browser'; }
  catch { $('saved').textContent = 'Browser storage unavailable — download JSON to keep your work'; }
}
function options(select, entries) {
  const first = document.createElement('option'); first.value = ''; first.textContent = 'Select'; select.append(first);
  for (const [value, label] of entries) {
    const option = document.createElement('option'); option.value = value; option.textContent = label; select.append(option);
  }
}
function rating(label, key, answer, entries) {
  const wrapper = document.createElement('div'), title = document.createElement('label'), select = document.createElement('select');
  title.textContent = label; select.setAttribute('aria-label', label); options(select, entries);
  select.value = answer[key] === null ? '' : String(answer[key]);
  select.onchange = () => {
    answer[key] = select.value === '' ? null :
      key === 'unwanted_music_or_speech' ? select.value === 'yes' :
      key === 'would_use' ? select.value : Number(select.value);
    save(); refresh();
  };
  wrapper.append(title, select); return wrapper;
}
function stopMedia() { $('video').pause(); $('audio').pause(); }
function render() {
  stopMedia();
  const sceneId = currentId(), scene = sceneById.get(sceneId), answer = answerFor(sceneId);
  $('position').textContent = 'SCENE ' + String(state.index + 1).padStart(2, '0') + ' / ' + study.scenes.length;
  $('sceneTitle').textContent = scene.label; $('alias').value = state.alias; $('device').value = state.device;
  $('consent').checked = state.consent_acknowledged; $('sceneNote').value = answer.note;
  $('video').src = new URL(scene.video, document.baseURI).href;
  $('audio').src = new URL(scene.audio, document.baseURI).href;
  $('sceneNote').oninput = () => { answer.note = $('sceneNote').value; save(); };
  $('ratings').replaceChildren(
    rating('Scene fit', 'event_fit', answer, [[1, '1 · Poor fit'], [2, '2'], [3, '3 · Fair'], [4, '4'], [5, '5 · Excellent fit']]),
    rating('Audio-video timing', 'sync', answer, [[1, '1 · Poor'], [2, '2'], [3, '3 · Fair'], [4, '4'], [5, '5 · Excellent']]),
    rating('Sound quality', 'audio_quality', answer, [[1, '1 · Poor'], [2, '2'], [3, '3 · Fair'], [4, '4'], [5, '5 · Excellent']]),
    rating('Noise / artifacts', 'artifact_severity', answer, [[1, '1 · None'], [2, '2'], [3, '3 · Moderate'], [4, '4'], [5, '5 · Severe']]),
    rating('Unwanted music or speech?', 'unwanted_music_or_speech', answer, [['no', 'No'], ['yes', 'Yes']]),
    rating('Would you keep it?', 'would_use', answer, [['yes', 'Yes'], ['after_edit', 'After editing'], ['no', 'No']])
  );
  $('prev').disabled = state.index === 0;
  $('next').textContent = state.index === study.scenes.length - 1 ? 'Finish and download ↓' : 'Next scene →';
  refresh();
}
function refresh() {
  const done = state.answers.filter(complete).length;
  $('progress').max = study.scenes.length; $('progress').value = done;
  $('progressLabel').textContent = done + ' / ' + study.scenes.length + ' scenes rated';
  $('state').textContent = complete(answerFor()) ? 'RATED' : 'IN PROGRESS';
  $('deliveryTitle').textContent = done === study.scenes.length ? 'Study complete — thank you' : 'Take a break or finish';
  $('jump').replaceChildren(...state.scene_order.map((sceneId, index) => {
    const button = document.createElement('button');
    button.textContent = String(index + 1); button.className = complete(answerFor(sceneId)) ? 'done' : '';
    button.setAttribute('aria-current', String(index === state.index));
    button.setAttribute('aria-label', 'Scene ' + (index + 1) + ', ' + (complete(answerFor(sceneId)) ? 'completed' : 'incomplete'));
    button.onclick = () => { state.index = index; save(); render(); }; return button;
  }));
}
$('alias').oninput = () => { state.alias = $('alias').value; save(); };
$('device').onchange = () => { state.device = $('device').value; save(); };
$('consent').onchange = () => { state.consent_acknowledged = $('consent').checked; save(); };
$('prev').onclick = () => { if (state.index > 0) { state.index--; save(); render(); } };
$('next').onclick = () => {
  if (state.index < study.scenes.length - 1) { state.index++; save(); render(); }
  else $('download').focus();
};
$('download').onclick = () => {
  state.consent_acknowledged = $('consent').checked;
  if (!state.consent_acknowledged) { $('message').textContent = 'Please tick the consent box before submitting your response.'; return; }
  save();
  const response = { ...state, exported_at: new Date().toISOString() };
  const link = document.createElement('a');
  const url = URL.createObjectURL(new Blob([JSON.stringify(response, null, 2)], { type: 'application/json' }));
  link.href = url; link.download = 'kandinsky_answers_' + study.study_id.slice(0, 10) + '_' + state.participant_id + '.json';
  link.click(); setTimeout(() => URL.revokeObjectURL(url), 1200);
  $('message').textContent = 'Your JSON response was downloaded. Send this file to the study owner; no automatic upload occurred.';
};
$('import').onchange = async event => {
  const file = event.target.files[0]; if (!file) return;
  try {
    if (file.size > 2_000_000) throw Error('Response file is too large.');
    const incoming = validate(JSON.parse(await file.text()));
    if (!confirm('Replace the current browser session with this response file? Download unsaved work first.')) return;
    state = incoming; save(); render(); $('message').textContent = 'Response loaded. You can continue where you left off.';
  } catch (error) { $('message').textContent = error.message; }
  finally { event.target.value = ''; }
};
$('reset').onclick = () => {
  if (!confirm('Start a new participant? Download current responses first.')) return;
  state = fresh(); save(); render(); $('message').textContent = 'A new participant session is ready.';
};
$('studyTag').textContent = 'Study ID: ' + study.study_id.slice(0, 12);
save(); render();
