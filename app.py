"""Single-file cTrader UI prototype. Simulation only; no external APIs."""
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="NEXUS | cTrader Agent",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
.stApp {background:#060e15}
.block-container {
    padding:3.5rem .25rem .5rem;
    max-width:1180px;
}
iframe {border:0}
</style>
""", unsafe_allow_html=True)

HTML = r"""
<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root {
  --bg:#060e15; --panel:#101d27; --line:#263641;
  --text:#e7eff5; --muted:#94a8b7; --cyan:#49d9ef;
  --green:#28d6aa; --red:#fb718f; --purple:#b3a1ff;
}
* {box-sizing:border-box}
body {
  margin:0; background:var(--bg); color:var(--text);
  font-family:Tahoma,Arial,sans-serif; font-size:14px;
}
button,input,select {font:inherit}
button {cursor:pointer; touch-action:manipulation}
button:disabled {opacity:.4;cursor:not-allowed}
button:focus-visible,input:focus-visible,select:focus-visible {
  outline:2px solid var(--cyan);outline-offset:3px;
}
.wrap {max-width:1050px;margin:auto;padding:12px}
.header {
  display:flex;justify-content:space-between;align-items:center;
  gap:12px;padding:12px 0 20px;
}
.brand {font-size:22px;font-weight:900}
.brand b {color:var(--cyan)}
.sub,.muted {color:var(--muted);font-size:12px;line-height:1.8}
.clock {direction:ltr;color:var(--cyan);font:17px monospace}
.tag {
  display:inline-block;border:1px solid #655329;background:#302919;
  color:#f4ce79;border-radius:20px;padding:5px 10px;font-size:11px;
}
.notice {
  color:#b7cfdb;background:#11232b;border:1px solid #24404a;
  border-radius:13px;padding:12px;line-height:1.9;margin-bottom:16px;
}
.ticker {
  display:flex;gap:20px;overflow:auto;white-space:nowrap;
  padding:12px;border-block:1px solid var(--line);direction:ltr;
  font:12px monospace;color:var(--cyan);margin-bottom:18px;
}
.card {
  border:1px solid var(--line);border-radius:22px;padding:20px;
  background:linear-gradient(130deg,#151c2c 0%,#0b2023 100%);
  margin-bottom:16px;overflow:hidden;
}
.card.glow {
  border-color:#23665c;
  box-shadow:0 0 30px #13ba8b0b;
}
.heading {
  display:flex;align-items:center;justify-content:space-between;
  gap:10px;margin-bottom:18px;
}
h2 {font-size:18px;margin:0}
h3 {font-size:15px;margin:0 0 8px}
p {line-height:1.9}
.icon {
  width:50px;height:50px;border-radius:16px;display:grid;
  place-items:center;background:#23ceb515;color:var(--cyan);
  border:1px solid #39717b;font-size:27px;
}
.row {display:flex;gap:12px;align-items:center}
.between {justify-content:space-between}
.badge {
  color:var(--green);border:1px solid #257f6c;
  background:#0a9e7c16;padding:6px 10px;border-radius:20px;font-size:12px;
}
.grid2 {display:grid;grid-template-columns:1fr 1fr;gap:12px}
.grid3 {display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.metric {
  background:#ffffff03;border:1px solid var(--line);
  border-radius:16px;padding:16px 12px;min-width:0;
}
.metric small {color:var(--muted);display:block;margin-bottom:13px}
.value {font:700 23px monospace;direction:ltr;display:block}
.green {color:var(--green)}
.red {color:var(--red)}
.cyan {color:var(--cyan)}
.purple {color:var(--purple)}
.btn {
  background:#14252f;border:1px solid #344954;color:var(--text);
  padding:12px;border-radius:12px;min-height:44px;
}
.btn:hover {border-color:var(--cyan)}
.btn.active {
  border-color:var(--green);background:#13a9861c;color:#9fffe2;
}
.btn.primary {
  width:100%;background:linear-gradient(100deg,#029e7f,#16bc90);
  color:white;font-weight:bold;font-size:17px;border:none;
  box-shadow:0 5px 25px #0db28d22;
}
.btn.danger {
  width:100%;border-color:#884052;color:#ffadbf;background:#7a213b30;
}
.tool {
  border:1px solid var(--line);border-radius:14px;padding:13px;
  margin-top:9px;display:flex;justify-content:space-between;
  align-items:center;gap:10px;
}
.tool small {color:var(--muted);display:block;margin-top:6px}
.status {font-size:11px;color:var(--green);white-space:nowrap}
.status.blocked {color:var(--red)}
label {display:block;color:var(--muted);font-size:12px;margin:15px 0 8px}
input,select {
  width:100%;background:#101b28;color:var(--text);
  border:1px solid #35434f;border-radius:10px;padding:11px;
  min-height:43px;
}
input[type=range] {accent-color:var(--green);padding:0;min-height:30px}
.ring {
  width:118px;height:118px;border-radius:50%;
  background:conic-gradient(var(--cyan) 0deg,#20343d 0deg);
  padding:10px;flex-shrink:0;
}
.ring-inner {
  width:100%;height:100%;border-radius:50%;background:#0c1922;
  display:flex;flex-direction:column;align-items:center;justify-content:center;
}
.ring strong {font:700 24px monospace}
.ring small {font-size:10px;color:var(--muted);margin-top:6px}
.track {height:7px;background:#25353e;border-radius:8px;overflow:hidden;margin-top:12px}
.track i {display:block;height:100%;background:var(--green);width:0}
.network {width:100%;height:130px;display:block;opacity:.8}
.speech {
  padding:14px;border:1px solid #36505a;background:#ffffff03;
  border-radius:15px;line-height:1.9;margin-top:12px;color:#bed0dc;
}
.chart {width:100%;display:block;direction:ltr}
.symbols {display:flex;gap:8px;overflow:auto;margin-bottom:18px}
.symbols button {white-space:nowrap;font:12px monospace}
.table-wrap {overflow:auto}
table {width:100%;border-collapse:collapse;font-size:12px;white-space:nowrap}
td,th {padding:13px 8px;text-align:right;border-bottom:1px solid var(--line)}
th {font-weight:normal;color:var(--muted)}
.empty {padding:24px;text-align:center;color:var(--muted)}
.chat {max-height:290px;overflow:auto}
.bubble {
  margin:10px 0;padding:13px;border-radius:14px;
  background:#182632;border:1px solid #2c4250;line-height:1.9;
}
.bubble.user {background:#14382f;border-color:#226552}
.quick {display:flex;overflow:auto;gap:8px;margin:12px 0}
.quick button {white-space:nowrap;font-size:12px}
.log {
  padding:12px;border:1px solid var(--line);border-radius:13px;
  margin-top:9px;color:#c3d0db;font-size:12px;line-height:1.8;
}
.log time {display:block;font:10px monospace;color:var(--muted);margin-top:6px}
.foot {color:var(--muted);text-align:center;font-size:11px;line-height:1.9;padding:15px}
@media(min-width:800px) {
  .desktop {display:grid;grid-template-columns:1fr 1fr;gap:16px;align-items:start}
}
@media(max-width:400px) {
  .wrap {padding:8px}
  .card {padding:16px;border-radius:18px}
  h2 {font-size:16px}
  .value {font-size:20px}
  .ring {width:100px;height:100px}
  .brand {font-size:20px}
}
</style>
</head>
<body>
<div class="wrap">
  <header class="header">
    <div>
      <div class="brand">NEXUS <b>AI</b> ◈</div>
      <div class="sub">cTrader Agent · لوحة قيادة الوكيل</div>
    </div>
    <div style="text-align:left">
      <div class="clock" id="clock"></div>
      <span class="tag">محاكاة محلية</span>
    </div>
  </header>

  <div class="notice">
    نسخة واجهة تفاعلية: الأسعار مولدة، والتحليل قاعدة محلية،
    والمحادثة ليست نموذج ذكاء اصطناعي. لا اتصال بـ cTrader،
    ولا تنفيذ حقيقي أو مراقبة مستمرة في الخلفية.
  </div>

  <div class="ticker" id="ticker"></div>

  <section class="card glow">
    <div class="heading">
      <div class="row">
        <div class="icon">✧</div>
        <div>
          <h2>وكيل <span id="agentName" class="cyan">Claude</span></h2>
          <div class="sub" id="agentStatus">في وضع الاستعداد · محاكاة</div>
        </div>
      </div>
      <span class="badge" id="runBadge">متوقف</span>
    </div>
    <svg class="network" id="network" viewBox="0 0 500 130"></svg>
    <div class="speech" id="thought">
      جاهز لتجربة مسار التحليل والمخاطر. اختر الإعدادات ثم ابدأ المحاكاة.
    </div>
    <div style="margin-top:12px">
      <button class="btn" style="width:100%" onclick="scan()">
        مسح السوق التجريبي الآن ↻
      </button>
    </div>
  </section>

  <section class="card glow">
    <div class="heading">
      <h2>⌘ صلاحيات الوكيل</h2>
      <span class="badge">تداول افتراضي فقط</span>
    </div>
    <div class="grid2">
      <button id="manualMode" class="btn active" onclick="setMode('manual')">
        <h3>موافقة يدوية</h3><span class="sub">راجع الإشارة قبل التنفيذ</span>
      </button>
      <button id="autoMode" class="btn" onclick="setMode('auto')">
        <h3>محاكاة ذاتية</h3><span class="sub">تنفيذ عند الضغط على المسح</span>
      </button>
    </div>
    <div class="tool">
      <div>فتح مراكز مع حماية<small>بعد فحص الثقة والحجم وحد الخسارة</small></div>
      <span class="status">محاكاة</span>
    </div>
    <div class="tool">
      <div>وقف الخسارة وجني الأرباح<small>إلزاميان لكل صفقة افتراضية</small></div>
      <span class="status">إلزامي</span>
    </div>
    <div class="tool">
      <div>السحب وتحويل الأموال<small>غير منفّذين وخارج نطاق الواجهة</small></div>
      <span class="status blocked">محظور</span>
    </div>
    <div style="margin-top:16px">
      <button class="btn danger" onclick="emergency()">
        ⊗ إيقاف طارئ — إغلاق المحاكاة وقفل التنفيذ
      </button>
    </div>
  </section>

  <div class="desktop">
    <section class="card">
      <div class="heading"><h2>✧ نموذج الذكاء الاصطناعي</h2></div>
      <div class="grid3">
        <button class="btn active" id="mClaude" onclick="setModel('Claude')">Claude</button>
        <button class="btn" id="mGPT4o" onclick="setModel('GPT4o')">GPT-4o</button>
        <button class="btn" id="mGemini" onclick="setModel('Gemini')">Gemini</button>
      </div>
      <p class="muted">
        نموذج واحد مختار للعرض. لا تُرسل أي بيانات لمزود خارجي.
      </p>
      <div class="grid3">
        <div class="metric"><small>الدقة</small><b class="cyan">غير مقاسة</b></div>
        <div class="metric"><small>زمن الاستدلال</small><b class="purple">غير مقاس</b></div>
        <div class="metric"><small>حالة API</small><b class="red">غير متصل</b></div>
      </div>
    </section>

    <section class="card">
      <div class="heading"><h2>◉ تحليل السوق التجريبي</h2><b class="cyan">EURUSD</b></div>
      <div class="row between">
        <div>
          <div class="muted">الاتجاه المقترح</div>
          <h2 id="direction" style="margin:12px 0">بانتظار المسح</h2>
          <div class="muted" id="analysisText">لا توجد إشارة بعد.</div>
        </div>
        <div class="ring" id="ring">
          <div class="ring-inner">
            <strong id="confidence">—</strong>
            <small>درجة توضيحية</small>
          </div>
        </div>
      </div>
      <p class="muted">الدرجة محاكاة وليست احتمال نجاح أو دقة تاريخية.</p>
    </section>
  </div>

  <section class="card">
    <div class="heading"><h2>⚙ استراتيجية وإدارة المخاطر</h2></div>
    <label>نمط الاستراتيجية التجريبية</label>
    <select id="strategy" onchange="invalidate()">
      <option value="balanced">متوازن — متوسط 12 / 26</option>
      <option value="trend">تتبّع الاتجاه — متوسط 20 / 50</option>
      <option value="scalp">قصير الأجل — متوسط 5 / 12</option>
    </select>

    <div class="grid2">
      <div>
        <label>المخاطرة لكل صفقة %</label>
        <input id="risk" type="number" min=".1" max="2" step=".1" value=".5" onchange="invalidate()">
      </div>
      <div>
        <label>أقصى حجم Lots</label>
        <input id="lots" type="number" min=".01" max="1" step=".01" value=".10" onchange="invalidate()">
      </div>
      <div>
        <label>وقف الخسارة Pips</label>
        <input id="sl" type="number" min="5" max="200" value="30" onchange="invalidate()">
      </div>
      <div>
        <label>جني الأرباح Pips</label>
        <input id="tp" type="number" min="5" max="500" value="60" onchange="invalidate()">
      </div>
      <div>
        <label>حد خسارة الجلسة %</label>
        <input id="limit" type="number" min=".5" max="10" step=".5" value="2" onchange="limitChanged()">
      </div>
      <div>
        <label>حد درجة الإشارة %</label>
        <input id="threshold" type="number" min="50" max="99" value="70" onchange="invalidate()">
      </div>
    </div>
    <div class="muted" style="margin-top:16px">
      مركز واحد فقط · حساب USD · اللوت 100,000 وحدة ·
      هامش تكلفة حسابي 15%. ليس ضماناً للخسارة القصوى.
    </div>
    <div class="track"><i id="riskBar"></i></div>
    <div class="muted" id="drawdownText"></div>
  </section>

  <button class="btn primary" id="startBtn" onclick="toggleRun()">
    ▶ تشغيل المحاكاة
  </button>
  <div class="muted" style="text-align:center;margin:10px 0 18px">
    التشغيل يفعّل الأزرار فقط؛ لا يوجد تداول خلفي أو أسعار حية.
  </div>

  <div class="grid2" style="margin-bottom:16px">
    <div class="metric"><small>الرصيد USD</small><span id="balance" class="value"></span></div>
    <div class="metric"><small>حقوق الملكية USD</small><span id="equity" class="value"></span></div>
    <div class="metric"><small>الربح العائم USD</small><span id="floating" class="value green"></span></div>
    <div class="metric"><small>صفقات مغلقة / نسبة فوز</small><span id="wins" class="value"></span></div>
  </div>

  <section class="card" style="padding:16px 8px">
    <div class="heading" style="padding:0 8px">
      <div><h2>السوق التجريبي</h2><span class="muted">EURUSD · شموع مولدة</span></div>
      <b id="price" class="value cyan"></b>
    </div>
    <div class="symbols" style="padding:0 8px">
      <button class="btn active">EURUSD</button>
      <span class="muted">النسخة الحالية تدعم رمزاً واحداً فقط</span>
    </div>
    <svg class="chart" id="chart" viewBox="0 0 650 320" role="img"
         aria-label="رسم شموع أسعار افتراضية"></svg>
    <div style="padding:8px">
      <button class="btn" style="width:100%" onclick="tick()">
        ↻ توليد شمعة جديدة وتقييم الحماية
      </button>
    </div>
  </section>

  <section class="card" id="signalCard" hidden>
    <div class="heading"><h2>إشارة تنتظر موافقتك</h2><span class="badge">محاكاة</span></div>
    <p id="signalDetails"></p>
    <button class="btn primary" onclick="execute()">تأكيد الصفقة الافتراضية</button>
  </section>

  <section class="card">
    <div class="heading">
      <h2>↗ المراكز المفتوحة</h2>
      <button class="btn" onclick="closePosition('إغلاق يدوي')">إغلاق الكل</button>
    </div>
    <div id="positions"></div>
  </section>

  <section class="card">
    <div class="heading"><h2>⇄ حالة التكامل</h2><span class="tag">غير متصل</span></div>
    <div class="grid3">
      <div class="metric"><small>cTrader</small><b>غير متصل</b></div>
      <div class="metric"><small>نموذج AI</small><b>غير متصل</b></div>
      <div class="metric"><small>Telegram</small><b>غير متصل</b></div>
    </div>
    <p class="muted">
      الاتصال المشفّر وOAuth وProtobuf يجب تنفيذها في الخدمة الخلفية.
      لا تعني حالة الواجهة وجود تفويض حقيقي.
    </p>
  </section>

  <section class="card">
    <div class="heading"><h2>✧ مساعد المحاكاة</h2><span class="muted">ردود محلية</span></div>
    <div class="chat" id="chat" aria-live="polite"></div>
    <div class="quick">
      <button class="btn" onclick="ask('وضع الحساب')">وضع الحساب</button>
      <button class="btn" onclick="ask('تحليل السوق')">تحليل السوق</button>
      <button class="btn" onclick="ask('إغلاق الكل')">إغلاق الكل</button>
      <button class="btn" onclick="ask('تقليل المخاطرة')">تقليل المخاطرة</button>
    </div>
    <form onsubmit="event.preventDefault();sendChat()" class="row">
      <input id="message" maxlength="300" placeholder="اسأل عن الحساب أو التحليل..." aria-label="رسالتك">
      <button class="btn" type="submit">إرسال</button>
    </form>
    <p class="muted">المحادثة لا تفتح صفقات ولا تفهم أوامر تداول حرة.</p>
  </section>

  <section class="card">
    <div class="heading"><h2>● سجل نشاط الوكيل</h2><button class="btn" onclick="downloadLogs()">تنزيل</button></div>
    <div id="logs"></div>
  </section>

  <section class="card">
    <div class="heading"><h2>⌁ منحنى حقوق الملكية</h2></div>
    <svg id="equityChart" class="chart" viewBox="0 0 650 140"></svg>
    <p class="muted">قراءات الجلسة المحلية فقط، وليست سجلاً تاريخياً للحساب.</p>
  </section>

  <section class="card">
    <div class="heading"><h2>◷ آخر الصفقات المغلقة</h2></div>
    <div id="history"></div>
  </section>

  <details class="card">
    <summary>إعادة ضبط المحاكاة</summary>
    <p class="muted">يمسح جميع بيانات الجلسة المحلية ويعيد الرصيد إلى 10,000 USD.</p>
    <button class="btn danger" onclick="resetDemo()">إعادة ضبط كاملة</button>
  </details>

  <div class="foot">
    NEXUS / cTrader UI Prototype<br>
    لا أموال حقيقية · لا وعود ربحية · لا تخزين دائم<br>
    إعادة تحميل الصفحة قد تعيد ضبط المحاكاة.
  </div>
</div>

<script>
const $=id=>document.getElementById(id);
const S={
  model:"Claude",mode:"manual",running:false,killed:false,
  balance:10000,baseline:10000,position:null,signal:null,
  candles:[],closed:[],logs:[],equities:[10000]
};
let last=1.085;
for(let i=0;i<65;i++) addCandle(.00045);

function addCandle(scale){
  const open=last;
  const close=Math.max(.1,open+(Math.random()-.5)*scale);
  S.candles.push({
    o:open,c:close,
    h:Math.max(open,close)+Math.random()*scale*.35,
    l:Math.min(open,close)-Math.random()*scale*.35
  });
  last=close;
  if(S.candles.length>90) S.candles.shift();
}
function fmt(n){return n.toLocaleString("en-US",{minimumFractionDigits:2,maximumFractionDigits:2})}
function price(){return last}
function floating(){
  const p=S.position;
  return p?(price()-p.entry)*(p.side==="buy"?1:-1)*p.units:0;
}
function equity(){return S.balance+floating()}
function dd(){return Math.max(0,(S.baseline-equity())/S.baseline*100)}
function value(id,min,max){
  const n=Number($(id).value);
  if(!Number.isFinite(n)||n<min||n>max) throw Error("راجع قيمة الحقل: "+id);
  return n;
}
function note(text){
  S.logs.unshift({text,time:new Date().toISOString()});
  S.logs=S.logs.slice(0,70);
}
function element(tag,text,cls){
  const e=document.createElement(tag);
  if(text!==undefined)e.textContent=text;
  if(cls)e.className=cls;
  return e;
}
function bubble(text,user=false){
  const box=element("div",text,"bubble"+(user?" user":""));
  $("chat").appendChild(box);
  while($("chat").children.length>20) $("chat").firstChild.remove();
  $("chat").scrollTop=$("chat").scrollHeight;
}
function invalidate(){
  S.signal=null;$("signalCard").hidden=true;
}
function setMode(mode){
  S.mode=mode;invalidate();
  $("manualMode").classList.toggle("active",mode==="manual");
  $("autoMode").classList.toggle("active",mode==="auto");
  note("وضع التنفيذ: "+(mode==="manual"?"موافقة يدوية":"محاكاة ذاتية بالضغط"));
  render();
}
function setModel(model){
  S.model=model;invalidate();
  for(const m of ["Claude","GPT4o","Gemini"])
    $("m"+m).classList.toggle("active",m===model);
  $("agentName").textContent=model==="GPT4o"?"GPT-4o":model;
  note("اختيار نموذج للعرض فقط: "+model);render();
}
function toggleRun(){
  if(S.killed){bubble("الطوارئ مقفلة؛ أعد ضبط المحاكاة أولاً.");return}
  S.running=!S.running;invalidate();
  note(S.running?"تفعيل المحاكاة التفاعلية":"إيقاف إنشاء وتنفيذ الإشارات");
  render();
}
function emergency(){
  S.killed=true;S.running=false;invalidate();
  closePosition("إيقاف طارئ");
  note("قفل التنفيذ التجريبي؛ لا استئناف دون إعادة الضبط");
  render();
}
function checkLimit(){
  const limit=value("limit",.5,10);
  if(!S.killed && dd()>=limit){
    S.killed=true;S.running=false;invalidate();
    closePosition("بلوغ حد خسارة الجلسة");
    note("تفعيل حد الخسارة المحلي");
  }
}
function limitChanged(){
  invalidate();
  try{checkLimit();render()}catch(e){bubble(e.message)}
}
function closePosition(reason){
  if(S.position){
    const gain=floating();
    S.balance+=gain;
    S.closed.unshift({...S.position,exit:price(),gain});
    S.position=null;
    note(reason+" | P/L: "+fmt(gain)+" USD");
  }
  invalidate();
  S.equities.push(equity());render();
}
function tick(){
  addCandle(.0015);
  const p=S.position;
  if(p){
    // Deliberately evaluate at the generated close, not guaranteed SL/TP fill.
    const hit=p.side==="buy"
 
