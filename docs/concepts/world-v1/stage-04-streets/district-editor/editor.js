/* Standalone concept editor: polygons stay in the source map's metre coordinates. */
'use strict';
const source = window.DISTRICT_MAP;
const $ = id => document.getElementById(id);
const svg = $('map');
const NS = 'http://www.w3.org/2000/svg';
// A new supplied boundary revision starts fresh; prior autosaves remain in storage.
const STORAGE = `brackett-stage4-district-editor-v1-${source.revision}`;
const COLORS = ['#68d5b1','#d6a0ef','#98b9ff','#f5c06e','#f39c8a',
  '#ef8bca','#e2d57c','#93c9d2','#b6a6fc'];
const coordinates = {units:'metres', origin:'concept-map upper left', x:'right / east', y:'down / south'};
let districts = structuredClone(source.districts);
let active = 1, selected = -1, tool = 'edit', space = false, gesture = null;
let view = {x:0,y:0,w:1260,h:720};
const history = [], future = [];

function message(text) { $('status').textContent = text; }
function current() { return districts.find(d => d.id === active); }
function snapshot() { return JSON.stringify(districts); }
function remember(before = snapshot()) {
  history.push(before);
  if (history.length > 100) history.shift();
  future.length = 0;
}
function save() {
  try { localStorage.setItem(STORAGE, JSON.stringify(documentData())); message('Saved in this browser. Export JSON to keep a portable copy.'); }
  catch { message('Browser storage unavailable. Export JSON to keep your edits.'); }
}
function documentData() {
  return {version:1, source:'Brackett stage-04-streets', coordinates, districts};
}
function validate(data) {
  if (data.version !== 1 || !data.coordinates || Object.entries(coordinates).some(([key,value]) => data.coordinates[key] !== value)) {
    throw new Error('Expected version 1 with the editor’s map-metre coordinate convention.');
  }
  if (!Array.isArray(data.districts) || data.districts.length !== 9) {
    throw new Error('Expected all nine districts.');
  }
  return source.districts.map(seed => {
    const matches = data.districts.filter(d => d.id === seed.id);
    const d = matches[0];
    if (matches.length !== 1 || d.name !== seed.name || !Array.isArray(d.points)
      || d.points.length < 3 || d.points.length > 1000 || !d.points.every(p =>
        Array.isArray(p) && p.length === 2 && p.every(n =>
          typeof n === 'number' && Number.isFinite(n) && Math.abs(n) <= 10000))) {
      throw new Error(`Invalid district ${seed.id}: keep its ID/name and 3–1000 finite points.`);
    }
    return {id:seed.id,name:seed.name,points:structuredClone(d.points)};
  });
}

svg.innerHTML = `<defs><clipPath id="land"><polygon points="${source.land}"/></clipPath>
<mask id="dry-land" maskUnits="userSpaceOnUse" x="0" y="0" width="1260" height="720">
<polygon points="${source.land}" fill="white"/><path d="${source.water}" fill="black"/></mask></defs>
<g id="background" pointer-events="none">${source.background}</g>
<g id="fills-layer" mask="url(#dry-land)"></g><g id="lines-layer"></g><g id="points-layer"></g>`;
for (const district of districts) {
  const option = document.createElement('option');
  option.value = district.id;
  option.textContent = `${district.id.toString().padStart(2,'0')} · ${district.name}`;
  $('district').append(option);
}
function element(tag, attributes, parent) {
  const node = document.createElementNS(NS, tag);
  for (const [key,value] of Object.entries(attributes)) node.setAttribute(key,value);
  parent.append(node);
  return node;
}
function render() {
  svg.setAttribute('viewBox', `${view.x} ${view.y} ${view.w} ${view.h}`);
  svg.dataset.tool = tool;
  const fills = $('fills-layer'), lines = $('lines-layer'), handles = $('points-layer');
  fills.replaceChildren(); lines.replaceChildren(); handles.replaceChildren();
  const unit = Math.max(view.w/svg.clientWidth, view.h/svg.clientHeight);
  for (const d of districts) {
    const chosen = d.id === active, color = COLORS[d.id-1];
    const points = d.points.map(p => p.join(',')).join(' ');
    if ($('fills').checked) element('polygon', {points,fill:color,'fill-opacity':chosen ? .23 : .1,
      'data-district':d.id,class:'district-fill'},fills);
    if ($('boundaries').checked || chosen) element('polygon', {points,fill:'none',stroke:color,
      'stroke-width':chosen?2.5:1.2,'vector-effect':'non-scaling-stroke',
      'stroke-opacity':chosen?1:.65,'pointer-events':'none'}, lines);
    const center = d.points.reduce((sum,p) => [sum[0]+p[0]/d.points.length,
      sum[1]+p[1]/d.points.length],[0,0]);
    const label = element('text',{x:center[0],y:center[1],fill:color,
      'font-size':13*unit,'font-weight':'600','text-anchor':'middle',
      'paint-order':'stroke',stroke:'#102332','stroke-width':3*unit,
      'pointer-events':'none'},lines);
    label.textContent = `${d.id} · ${d.name}`;
    if (!chosen) continue;
    d.points.forEach((p,i) => {
      const q = d.points[(i+1)%d.points.length];
      element('line',{x1:p[0],y1:p[1],x2:q[0],y2:q[1],stroke:'transparent',
        'stroke-width':14,'vector-effect':'non-scaling-stroke','data-edge':i,class:'edge'},lines);
      element('circle',{cx:p[0],cy:p[1],r:(i===selected?6:4.5)*unit,
        fill:i===selected?'#f5c06e':'#eff5f3',stroke:'#102332','stroke-width':1.5,
        'vector-effect':'non-scaling-stroke','data-point':i,class:'vertex'},handles);
    });
  }
  $('district').value = active;
  $('point-count').textContent = `${current().points.length} points${selected>=0 ? ` · point ${selected+1} selected` : ''}`;
  $('delete').disabled = selected<0 || current().points.length<=3;
  for (const [axis,index] of [['x',0],['y',1]]) {
    $(axis).disabled = selected<0;
    $(axis).value = selected<0 ? '' : current().points[selected][index];
  }
  $('undo').disabled = history.length===0;
  $('redo').disabled = future.length===0;
  for (const mode of ['edit','add','pan']) $(mode).setAttribute('aria-pressed',tool===mode);
}
function mapPoint(event) {
  return new DOMPoint(event.clientX,event.clientY).matrixTransform(svg.getScreenCTM().inverse());
}
function nearestEdge(p) {
  let best = {distance:Infinity};
  const points = current().points;
  points.forEach((a,index) => {
    const b = points[(index+1)%points.length], dx = b[0]-a[0], dy = b[1]-a[1];
    const t = Math.max(0,Math.min(1,((p.x-a[0])*dx+(p.y-a[1])*dy)/(dx*dx+dy*dy||1)));
    const q = [a[0]+t*dx,a[1]+t*dy], distance = Math.hypot(p.x-q[0],p.y-q[1]);
    if (distance<best.distance) best = {index,q,distance};
  });
  return best;
}
function rounded(p) { return [Math.round(p.x*10)/10, Math.round(p.y*10)/10]; }
function insert(p, edge, projected=false) {
  if (current().points.length>=1000) { message('This district has reached the 1000-point limit.'); return; }
  remember(); selected = edge.index+1;
  current().points.splice(selected,0, projected?edge.q.map(n=>Math.round(n*10)/10):rounded(p));
  render(); save();
}
svg.addEventListener('pointerdown',event => {
  if (event.button!==0) return;
  const p = mapPoint(event);
  if (tool==='pan' || space) {
    gesture = {kind:'pan',start:p,view:{...view}};
  } else if (event.target.hasAttribute('data-point')) {
    selected = Number(event.target.dataset.point);
    gesture = {kind:'point',before:snapshot(),index:selected};
    render();
  } else if (tool==='add') {
    insert(p,nearestEdge(p)); return;
  } else if (event.target.hasAttribute('data-district')) {
    active = Number(event.target.dataset.district); selected=-1; render(); return;
  } else if (event.target.hasAttribute('data-edge')) {
    // Preserve the edge node between clicks so the browser can dispatch dblclick.
    return;
  } else { selected=-1; render(); return; }
  svg.setPointerCapture(event.pointerId);
  event.preventDefault();
});
svg.addEventListener('pointermove',event => {
  if (!gesture) return;
  const p = mapPoint(event);
  if (gesture.kind==='point') {
    current().points[gesture.index] = rounded(p);
  } else {
    // Keep the anchor in map coordinates under the moving pointer.
    view.x += gesture.start.x-p.x; view.y += gesture.start.y-p.y;
  }
  render();
});
function finishGesture() {
  if (!gesture) return;
  if (gesture.kind==='point' && gesture.before!==snapshot()) { remember(gesture.before); save(); }
  gesture=null; render();
}
svg.addEventListener('pointerup',finishGesture);
svg.addEventListener('pointercancel',finishGesture);
svg.addEventListener('lostpointercapture',finishGesture);
svg.addEventListener('dblclick',event => {
  if (tool!=='edit' || space || !event.target.hasAttribute('data-edge')) return;
  event.preventDefault();
  const p=mapPoint(event), edge=nearestEdge(p);
  insert(p,edge,true);
});
function zoom(factor,p={x:view.x+view.w/2,y:view.y+view.h/2}) {
  const w = Math.max(100,Math.min(2520,view.w*factor)), ratio=w/view.w;
  view={x:p.x-(p.x-view.x)*ratio,y:p.y-(p.y-view.y)*ratio,w,h:view.h*ratio};
  render();
}
svg.addEventListener('wheel',event => {
  if (gesture) return;
  event.preventDefault(); zoom(Math.exp(Math.sign(event.deltaY)*.15),mapPoint(event));
},{passive:false});
$('zoom-in').onclick=()=>zoom(.8);
$('zoom-out').onclick=()=>zoom(1.25);
$('fit').onclick=()=>{view={x:0,y:0,w:1260,h:720};render();};
$('district').onchange=event=>{finishGesture();active=Number(event.target.value);selected=-1;render();};
for (const mode of ['edit','add','pan']) $(mode).onclick=()=>{finishGesture();tool=mode;render();};
for (const id of ['fills','boundaries']) $(id).onchange=render;
function removePoint() {
  if (selected<0 || current().points.length<=3) return;
  remember();current().points.splice(selected,1);selected=-1;render();save();
}
$('delete').onclick=removePoint;
for (const [axis,index] of [['x',0],['y',1]]) $(axis).onchange=()=>{
  const value=Number($(axis).value);
  if (selected<0 || !Number.isFinite(value) || Math.abs(value)>10000 || $(axis).value==='') {
    render();message('Enter a finite map coordinate between −10000 and 10000 metres.');return;
  }
  remember();current().points[selected][index]=value;render();save();
};
function undo(redo=false) {
  finishGesture();
  const from=redo?future:history, to=redo?history:future;
  if (!from.length) return;
  to.push(snapshot());districts=JSON.parse(from.pop());selected=-1;render();save();
}
$('undo').onclick=()=>undo();$('redo').onclick=()=>undo(true);
window.addEventListener('keydown',event=>{
  if (['INPUT','SELECT','TEXTAREA'].includes(event.target.tagName)) return;
  if (event.code==='Space') { space=true;event.preventDefault(); }
  if ((event.ctrlKey||event.metaKey) && event.key.toLowerCase()==='z') {
    event.preventDefault();undo(event.shiftKey);
  }
  if (event.key==='Delete' || event.key==='Backspace') {event.preventDefault();removePoint();}
});
window.addEventListener('keyup',event=>{if(event.code==='Space')space=false;});
window.addEventListener('blur',()=>{space=false;finishGesture();});
$('reset').onclick=()=>{
  if (!confirm('Reset all nine district polygons to the supplied boundaries? You can Undo this.')) return;
  remember();districts=structuredClone(source.districts);selected=-1;render();save();
};
$('export').onclick=()=>{
  finishGesture();
  const blob=new Blob([JSON.stringify(documentData(),null,2)+'\n'],{type:'application/json'});
  const url=URL.createObjectURL(blob),link=document.createElement('a');
  link.href=url;link.download='brackett-districts.json';link.click();
  setTimeout(()=>URL.revokeObjectURL(url),1000);message('Exported all nine district polygons in map metres.');
};
$('import').onclick=()=>{$('file').value='';$('file').click();};
$('file').onchange=async()=>{
  const file=$('file').files[0];if (!file)return;
  try {
    if (file.size>1024*1024) throw new Error('JSON file exceeds the 1 MB limit.');
    const next=validate(JSON.parse(await file.text()));
    finishGesture();remember();districts=next;selected=-1;render();save();
    message('Imported all nine districts. You can Undo this.');
  } catch(error) {message(`Import failed: ${error.message}`);}
};
try {
  const saved=localStorage.getItem(STORAGE);
  if (saved) {districts=validate(JSON.parse(saved));message('Restored your last browser edits.');}
  else message('Supplied district polygons loaded. Edits save in this browser.');
} catch {message('No usable autosave. Supplied polygons loaded; export JSON to keep edits.');}
window.addEventListener('resize',render);
render();
