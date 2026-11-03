      ?price()<=p.sl||price()>=p.tp
      :price()>=p.sl||price()<=p.tp;
    if(hit)closePosition("عبور حماية؛ إغلاق بسعر التحديث الافتراضي");
  }
  invalidate();
  try{checkLimit()}catch(e){bubble(e.message)}
  S.equities.push(equity());
  S.equities=S.equities.slice(-120);
  render();
}

function scan(){
  try{
    if(!S.running||S.killed)
      throw Error("شغّل المحاكاة أولاً؛ الطوارئ تمنع التنفيذ.");
    checkLimit();
    if(S.killed)throw Error("تم بلوغ حد الخسارة.");
    if(S.position)throw Error("يوجد مركز؛ النسخة تسمح بمركز واحد.");

    const lengths={
      balanced:[12,26],
      trend:[20,50],
      scalp:[5,12]
    };
    const [short,long]=lengths[$("strategy").value];
    const closes=S.candles.map(c=>c.c);
    const mean=n=>closes.slice(-n).reduce((a,b)=>a+b,0)/n;
    const fast=mean(short),slow=mean(long);
    const confidence=Math.min(
      95,Math.round(55+Math.abs(fast-slow)*40000)
    );
    const side=fast>=slow?"buy":"sell";

    $("direction").textContent=side==="buy"?"شراء":"بيع";
    $("confidence").textContent=confidence+"%";
    $("ring").style.background=
      `conic-gradient(var(--cyan) ${confidence*3.6}deg,#20343d 0deg)`;
    $("analysisText").textContent=
      `مقارنة متوسط ${short} بمتوسط ${long}.`;
    $("thought").textContent=
      "تحليل محلي مكتمل. الدرجة للعرض وليست توقعاً معايراً.";

    if(confidence<value("threshold",50,99)){
      invalidate();
      note("حياد: درجة المحاكاة أقل من الحد");
      render();
      return;
    }

    const sl=value("sl",5,200)*.0001;
    const tp=value("tp",5,500)*.0001;
    if(tp/sl<1.5)
      throw Error("اجعل جني الأرباح 1.5 مرة وقف الخسارة على الأقل.");

    const sign=side==="buy"?1:-1;
    S.signal={
      side,entry:price(),
      sl:price()-sign*sl,
      tp:price()+sign*tp,
      confidence,created:Date.now()
    };

    $("signalDetails").textContent=
      `${side==="buy"?"شراء":"بيع"} EURUSD · SL ${S.signal.sl.toFixed(5)}
       · TP ${S.signal.tp.toFixed(5)} · صالحة لدقيقتين.`;
    $("signalCard").hidden=false;
    note("إشارة محلية تنتظر فحص التنفيذ");
    if(S.mode==="auto")execute();else render();
  }catch(e){
    bubble(e.message);
    note(e.message);
    render();
  }
}

function execute(){
  try{
    if(S.killed||!S.running)throw Error("التنفيذ معطّل.");
    checkLimit();
    if(S.killed)throw Error("حد الخسارة يمنع التنفيذ.");

    const sig=S.signal;
    if(!sig||Date.now()-sig.created>120000)
      throw Error("لا توجد إشارة صالحة؛ أعد المسح.");
    if(S.position)throw Error("يوجد مركز مفتوح.");
    if(sig.confidence<value("threshold",50,99))
      throw Error("درجة الإشارة أقل من الحد.");

    const entry=price();
    const valid=sig.side==="buy"
      ?sig.sl<entry&&entry<sig.tp
      :sig.tp<entry&&entry<sig.sl;
    if(!valid)throw Error("مستويات الحماية غير صالحة.");

    const distance=Math.abs(entry-sig.sl);
    if(Math.abs(sig.tp-entry)/distance<1.5)
      throw Error("العائد إلى المخاطرة غير كاف.");

    const budget=
      Math.min(S.balance,equity())*value("risk",.1,2)/100;
    const units=Math.floor(
      Math.min(
        budget/(distance*1.15),
        value("lots",.01,1)*100000
      )/1000
    )*1000;
    if(units<1000)
      throw Error("الحجم المسموح أقل من 0.01 لوت.");

    S.position={
      side:sig.side,entry,sl:sig.sl,tp:sig.tp,units
    };
    invalidate();
    note("فتح مركز محاكاة؛ حماية إلزامية وحجم مقرب للأسفل");
    render();
  }catch(e){
    bubble(e.message);
    note(e.message);
    render();
  }
}

function ask(text){
  bubble(text,true);
  if(text==="إغلاق الكل"){
    closePosition("طلب إغلاق من مساعد المحاكاة");
    bubble("أُغلقت المراكز الافتراضية إن وجدت؛ وضع المحاكاة لم يتغير.");
  }else if(text==="تحليل السوق"){
    scan();
    bubble("التحليل محلي ويظهر في بطاقة السوق؛ ليس استدعاء AI.");
  }else if(text==="تقليل المخاطرة"){
    const n=Number($("risk").value);
    $("risk").value=
      Math.max(.1,Number.isFinite(n)?n/2:.1).toFixed(1);
    invalidate();
    bubble("خُفضت مخاطرة الصفقات القادمة فقط.");
  }else if(text==="وضع الحساب"){
    bubble(
      `الرصيد ${fmt(S.balance)} USD، حقوق الملكية ${fmt(equity())} USD.
       الاتصال الحقيقي غير متاح في هذه الواجهة.`
    );
  }else{
    bubble(
      "هذا مساعد محلي محدود. استخدم: وضع الحساب، تحليل السوق، " +
      "إغلاق الكل، أو تقليل المخاطرة. لا ينفذ أوامر فتح حرة."
    );
  }
}

function sendChat(){
  const input=$("message");
  const text=input.value.trim();
  input.value="";
  if(text)ask(text);
}

function svg(tag,attrs){
  const e=document.createElementNS(
    "http://www.w3.org/2000/svg",tag
  );
  for(const [k,v] of Object.entries(attrs))
    e.setAttribute(k,v);
  return e;
}

function chart(){
  const root=$("chart");
  root.replaceChildren();
  const data=S.candles.slice(-65);
  let lo=Math.min(...data.map(c=>c.l));
  let hi=Math.max(...data.map(c=>c.h));

  if(S.position){
    lo=Math.min(lo,S.position.sl);
    hi=Math.max(hi,S.position.tp);
  }

  const pad=(hi-lo)*.13+.0001;
  lo-=pad;hi+=pad;
  const y=v=>285-(v-lo)/(hi-lo)*265;

  for(let i=0;i<5;i++){
    const yy=20+i*65;
    root.appendChild(svg("line",{
      x1:0,x2:575,y1:yy,y2:yy,stroke:"#253540"
    }));
    const t=svg("text",{
      x:584,y:yy+4,fill:"#8ca3b2","font-size":10
    });
    t.textContent=(lo+(285-yy)/265*(hi-lo)).toFixed(5);
    root.appendChild(t);
  }

  data.forEach((c,i)=>{
    const x=8+i*8.5;
    const color=c.c>=c.o?"#28d6aa":"#fb718f";
    root.appendChild(svg("line",{
      x1:x,x2:x,y1:y(c.h),y2:y(c.l),stroke:color
    }));
    root.appendChild(svg("rect",{
      x:x-2.5,y:Math.min(y(c.o),y(c.c)),width:5,
      height:Math.max(1,Math.abs(y(c.o)-y(c.c))),
      fill:color
    }));
  });

  const levels=[[price(),"#49d9ef",""]];
  if(S.position){
    levels.push(
      [S.position.sl,"#fb718f","SL"],
      [S.position.tp,"#28d6aa","TP"]
    );
  }
  for(const [v,color,label] of levels){
    root.appendChild(svg("line",{
      x1:0,x2:575,y1:y(v),y2:y(v),
      stroke:color,"stroke-dasharray":"4 5"
    }));
    if(label){
      const t=svg("text",{
        x:540,y:y(v)-5,fill:color,"font-size":11
      });
      t.textContent=label;
      root.appendChild(t);
    }
  }
}

function renderNetwork(){
  const root=$("network");
  const layers=[3,5,4,5,3],nodes=[];
  layers.forEach((n,l)=>{
    const layer=[];
    for(let j=0;j<n;j++)
      layer.push([35+l*105,12+(j+1)*108/(n+1)]);
    nodes.push(layer);
  });
  for(let l=0;l<nodes.length-1;l++){
    for(const a of nodes[l]){
      for(const b of nodes[l+1]){
        root.appendChild(svg("line",{
          x1:a[0],y1:a[1],x2:b[0],y2:b[1],
          stroke:"#2a7274","stroke-opacity":".22"
        }));
      }
    }
  }
  nodes.flat().forEach((n,i)=>{
    root.appendChild(svg("circle",{
      cx:n[0],cy:n[1],r:3.5,
      fill:i%3?"#37666b":"#49d9ef"
    }));
  });
}

function render(){
  $("balance").textContent=fmt(S.balance);
  $("equity").textContent=fmt(equity());
  $("floating").textContent=
    (floating()>=0?"+":"")+fmt(floating());
  $("floating").className=
    "value "+(floating()>=0?"green":"red");

  const wins=S.closed.filter(p=>p.gain>0).length;
  $("wins").textContent=S.closed.length+" / "+
    (S.closed.length
      ?Math.round(wins/S.closed.length*100)+"%":"—");
  $("price").textContent=price().toFixed(5);
  $("ticker").textContent=
    "EURUSD "+price().toFixed(5)+
    "  •  SYNTHETIC DATA  •  cTrader: DISCONNECTED";

  $("agentStatus").textContent=S.killed
    ?"قفل طوارئ · التنفيذ معطّل"
    :S.running
      ?"محاكاة مفعّلة · تنتظر تفاعلك"
      :"في وضع الاستعداد · محاكاة";
  $("runBadge").textContent=
    S.killed?"مقفول":S.running?"جاهز":"متوقف";
  $("startBtn").textContent=S.killed
    ?"⊗ المحاكاة مقفلة"
    :S.running?"Ⅱ إيقاف المحاكاة":"▶ تشغيل المحاكاة";
  $("startBtn").disabled=S.killed;

  const limit=Number($("limit").value)||2;
  $("riskBar").style.width=
    Math.min(100,dd()/limit*100)+"%";
  $("drawdownText").textContent=
    `خسارة الجلسة ${dd().toFixed(2)}% / الحد ${limit}%`;

  const positions=$("positions");
  positions.replaceChildren();
  if(S.position){
    const p=S.position;
    positions.appendChild(element("p",
      `EURUSD · ${p.side==="buy"?"شراء":"بيع"} · ${(p.units/100000).toFixed(2)} Lots`
    ));
    positions.appendChild(element("p",
      `الدخول ${p.entry.toFixed(5)} · SL ${p.sl.toFixed(5)} · TP ${p.tp.toFixed(5)}`,
      "muted"
    ));
    positions.appendChild(element("b",
      fmt(floating())+" USD",
      floating()>=0?"green":"red"
    ));
  }else{
    positions.appendChild(
      element("div","لا توجد مراكز مفتوحة","empty")
    );
  }

  $("logs").replaceChildren();
  for(const entry of S.logs.slice(0,8)){
    const box=element("div",entry.text,"log");
    box.appendChild(element("time",entry.time));
    $("logs").appendChild(box);
  }

  $("history").replaceChildren();
  if(!S.closed.length){
    $("history").appendChild(
      element("div","لا توجد صفقات مغلقة","empty")
    );
  }
  for(const p of S.closed.slice(0,8)){
    $("history").appendChild(element("div",
      `${p.side==="buy"?"شراء":"بيع"} EURUSD · ${(p.units/100000).toFixed(2)} Lots · ${fmt(p.gain)} USD`,
      "log"
    ));
  }

  chart();
  const ec=$("equityChart");
  ec.replaceChildren();
  const values=S.equities;
  const min=Math.min(...values)-5;
  const max=Math.max(...values)+5;
  const points=values.map((v,i)=>
    `${10+i/Math.max(1,values.length-1)*630},${120-(v-min)/(max-min)*100}`
  ).join(" ");
  ec.appendChild(svg("polyline",{
    points,fill:"none",stroke:"#28d6aa","stroke-width":2
  }));
}

function downloadLogs(){
  const blob=new Blob(
    [JSON.stringify(S.logs,null,2)],
    {type:"application/json"}
  );
  const url=URL.createObjectURL(blob);
  const a=document.createElement("a");
  a.href=url;
  a.download="nexus-demo-log.json";
  a.click();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
}

function resetDemo(){
  if(confirm("حذف كل بيانات هذه المحاكاة وإعادة الرصيد؟"))
    location.reload();
}

function clock(){
  $("clock").textContent=
    new Date().toLocaleTimeString("en-GB");
}

renderNetwork();
clock();
setInterval(clock,1000);
note("بدء واجهة محاكاة؛ لا اتصال خارجي أو مفاتيح سرية");
bubble("مرحباً. هذه محاكاة فقط. شغّل المحاكاة ثم اضغط مسح السوق.");
render();
</script>
</body>
</html>
"""

components.html(HTML, height=1000, scrolling=True)
# END_OF_APP
