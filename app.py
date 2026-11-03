"""Single-file mobile-friendly DEMO dashboard. No broker/AI/network integration.
Deploy on Streamlit Community Cloud, selecting app.py as the entry point.
Never put real credentials in this file or in GitHub.
"""
import csv
import io
import math
import random
from datetime import datetime, timezone

import streamlit as st

st.set_page_config(page_title="cTrader AI | DEMO", page_icon="📊", layout="wide")
st.markdown("""<style>
.stApp {background:#0b1220;color:#e5edf7}
[data-testid="stSidebar"] {background:#111d30}
h1,h2,h3,p,label {text-align:right}
[data-testid="stMetric"] {background:#142238;padding:16px;border-radius:14px;border:1px solid #263750}
.stButton button {border-radius:10px;min-height:44px}
.notice {direction:rtl;background:#192a40;border-right:4px solid #26c6aa;padding:16px;border-radius:10px;margin-bottom:16px}
</style>""", unsafe_allow_html=True)


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def initialize():
    if "demo_account" not in st.session_state:
        rng = random.Random(42)
        prices = [1.085]
        for _ in range(79):
            prices.append(round(prices[-1] + rng.uniform(-.00012, .00012), 5))
        st.session_state.demo_account = {
            "balance": 10000.0, "baseline": 10000.0,
            "prices": prices, "positions": [], "killed": False,
            "logs": [], "signal": None,
            "analysis": "لم يُنشأ تحليل تجريبي بعد.",
        }


initialize()
a = st.session_state.demo_account


def log(event):
    a["logs"].insert(0, {"time_utc": now(), "event": event})
    a["logs"] = a["logs"][:300]


def pnl(position, price):
    direction = 1 if position["side"] == "buy" else -1
    return (price - position["entry"]) * direction * position["units"]


def equity():
    return a["balance"] + sum(pnl(p, a["prices"][-1]) for p in a["positions"])


def close_all(reason):
    for position in a["positions"]:
        a["balance"] += pnl(position, a["prices"][-1])
    a["positions"] = []
    a["signal"] = None
    log(reason)


def kill(reason):
    a["killed"] = True
    close_all(reason)


with st.sidebar:
    st.title("📊 cTrader AI")
    st.caption("DEMO • محاكاة فقط")
    page = st.radio("القائمة", ["لوحة التحكم", "إدارة المخاطر", "سجل الأحداث", "دليل الهاتف"])
    st.divider()
    provider = st.selectbox("اختيار نموذج واحد — عرض فقط", ["GPT-4o", "Claude", "Gemini"])
    st.caption("لا يتم استدعاء أي نموذج؛ التحليل قواعد تجريبية محلية.")
    risk_percent = st.slider("المخاطرة للصفقة %", .1, 2.0, .5, .1)
    daily_limit = st.slider("حد الخسارة منذ بدء الجلسة %", .5, 5.0, 2.0, .5)
    max_lots = st.slider("أقصى حجم تجريبي Lots", .01, 1.0, .10, .01)
    st.caption("النموذج الحسابي: EUR/USD، حساب USD، اللوت = 100,000 وحدة.")
    if st.button("🛑 إيقاف طارئ وإغلاق الكل", type="primary", use_container_width=True):
        kill("إيقاف طارئ يدوي؛ إغلاق كل المراكز التجريبية")
        st.rerun()
    if st.button("إغلاق المراكز وتعطيل التنفيذ", use_container_width=True):
        kill("إغلاق يدوي وتعطيل التنفيذ التجريبي")
        st.rerun()

# إعادة التقييم أيضاً عند تغيير حد المخاطرة من الشريط الجانبي.
if not a["killed"] and equity() <= a["baseline"] * (1 - daily_limit / 100):
    kill("تفعيل حد خسارة الجلسة التجريبية")

st.title("لوحة تحكم وكيل التداول")
st.markdown('<div class="notice">واجهة تفاعلية تجريبية — الأسعار والأوامر والتحليل محاكاة. لا اتصال بـ cTrader أو Telegram أو مزودي الذكاء الاصطناعي، ولا توجد عمليات سحب أو تحويل.</div>', unsafe_allow_html=True)
if a["killed"]:
    st.error("مفتاح الطوارئ مفعّل. إنشاء وتنفيذ الإشارات متوقفان في هذه الجلسة.")

if page == "لوحة التحكم":
    columns = st.columns(4)
    columns[0].metric("الرصيد USD", f'{a["balance"]:,.2f}')
    columns[1].metric("حقوق الملكية USD", f'{equity():,.2f}')
    columns[2].metric("أداء الجلسة USD", f'{equity() - a["baseline"]:+,.2f}')
    drawdown = max(0, (a["baseline"] - equity()) / a["baseline"] * 100)
    columns[3].metric("خسارة الجلسة", f"{drawdown:.2f}%", delta=None)
    st.subheader("EUR/USD — أسعار مولدة محلياً")
    st.line_chart(a["prices"], height=270)
    st.caption(f'آخر سعر تجريبي: {a["prices"][-1]:.5f} | يتغير فقط عند الضغط على زر تحديث السعر.')
    left, right = st.columns(2)
    with left:
        if st.button("تحديث السعر التجريبي", use_container_width=True):
            price = max(.1, round(a["prices"][-1] + random.uniform(-.0008, .0008), 5))
            a["prices"].append(price)
            a["prices"] = a["prices"][-240:]
            remaining = []
            for position in a["positions"]:
                hit = ((price <= position["sl"] or price >= position["tp"])
                       if position["side"] == "buy" else
                       (price >= position["sl"] or price <= position["tp"]))
                if hit:
                    a["balance"] += pnl(position, price)
                    log("إغلاق تجريبي عند عبور SL/TP؛ بسعر التحديث لا السعر المضمون")
                else:
                    remaining.append(position)
            a["positions"] = remaining
            if equity() <= a["baseline"] * (1 - daily_limit / 100):
                kill("تفعيل حد خسارة الجلسة التجريبية")
            st.rerun()
    with right:
        if st.button("إنشاء إشارة محاكاة", disabled=a["killed"], use_container_width=True):
            prices = a["prices"]
            side = "buy" if prices[-1] >= sum(prices[-10:]) / 10 else "sell"
            entry = prices[-1]
            direction = 1 if side == "buy" else -1
            a["signal"] = {"direction": side, "confidence": .82,
                "entry": entry, "stop_loss": round(entry - direction * .002, 5),
                "take_profit": round(entry + direction * .004, 5),
                "analysis": "قاعدة اتجاه تجريبية مقارنة بمتوسط آخر عشرة أسعار.",
                "reason": "اختبار الواجهة فقط؛ الثقة ثابتة وغير محسوبة إحصائياً."}
            log(f"إنشاء إشارة محاكاة؛ اختيار المزود للعرض فقط: {provider}")
            st.rerun()

    if a["signal"]:
        signal = a["signal"]
        st.subheader("إشارة موحدة JSON — ليست توصية تداول")
        st.json(signal)
        if st.button("تأكيد فتح صفقة تجريبية", type="primary",
                     disabled=a["killed"] or bool(a["positions"])):
            entry = a["prices"][-1]
            sl, tp = signal["stop_loss"], signal["take_profit"]
            valid = sl < entry < tp if signal["direction"] == "buy" else tp < entry < sl
            if not valid:
                st.error("الإشارة لم تعد صالحة بالسعر الحالي. أنشئ إشارة جديدة.")
            else:
                distance = abs(entry - sl)
                budget = min(a["balance"], equity()) * risk_percent / 100
                units = math.floor(min(budget / (distance * 1.15), max_lots * 100000) / 1000) * 1000
                if units < 1000:
                    st.error("حجم المخاطرة أقل من الحد الأدنى التجريبي: 0.01 لوت.")
                elif abs(tp - entry) / distance < 1.5:
                    st.error("العائد إلى المخاطرة أقل من 1.5.")
                else:
                    a["positions"].append({"side": signal["direction"], "entry": entry,
                        "sl": sl, "tp": tp, "units": units, "lots": units / 100000})
                    a["signal"] = None
                    log("فتح مركز محاكاة مع SL وTP إلزاميين")
                    st.rerun()
    st.subheader("المراكز التجريبية")
    if a["positions"]:
        st.dataframe([{**p, "pnl_usd": round(pnl(p, a["prices"][-1]), 2)}
                      for p in a["positions"]], use_container_width=True, hide_index=True)
    else:
        st.info("لا توجد مراكز مفتوحة.")

elif page == "إدارة المخاطر":
    st.subheader("حدود المحاكاة")
    st.write(f"المخاطرة: {risk_percent}% — حد خسارة الجلسة: {daily_limit}% — أقصى حجم: {max_lots:.2f} Lots")
    st.progress(min(1.0, max(0.0, (a["baseline"] - equity()) / a["baseline"] * 100 / daily_limit)))
    st.warning("هذا حد خسارة جلسة وليس حداً يومياً حقيقياً. الحالة ليست محفوظة على خادم دائم، وتتلاشى عند فقد جلسة المتصفح أو إعادة تشغيل التطبيق. لا توجد مراقبة مستمرة أو تداول خلفي.")
    st.write("الحماية التجريبية: صفقة واحدة، SL/TP إلزاميان، تقريب الحجم للأسفل، هامش تكلفة 15%، ومنع التنفيذ بعد الطوارئ.")
    confirm = st.checkbox("أفهم أن هذا يعيد الحساب التجريبي فقط إلى 10,000 دولار")
    if st.button("إعادة ضبط المحاكاة", disabled=not confirm):
        del st.session_state.demo_account
        st.rerun()

elif page == "سجل الأحداث":
    st.subheader("سجل الجلسة — UTC")
    if a["logs"]:
        st.dataframe(a["logs"], use_container_width=True, hide_index=True)
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["time_utc", "event"])
        writer.writeheader()
        writer.writerows(a["logs"])
        st.download_button("تنزيل سجل CSV", data="\ufeff" + output.getvalue(),
                           file_name="demo-events.csv", mime="text/csv")
    else:
        st.info("لم تُسجّل أحداث بعد.")

else:
    st.subheader("تشغيل من الهاتف فقط")
    st.markdown("""1. ارفع هذا الملف باسم **app.py** إلى مستودع GitHub تملكه.
2. افتح **share.streamlit.io** وسجّل الدخول واربط المستودع.
3. أنشئ تطبيقاً، واختر المستودع والفرع وملف **app.py** ثم Deploy.
4. افتح رابط التطبيق الناتج من الهاتف. لا تضف مفاتيح حقيقية لهذه النسخة.

لا يلزم requirements.txt لهذه النسخة على Community Cloud لأنها تعتمد على Streamlit المتاح افتراضياً ومكتبة Python القياسية فقط. لا توجد أصول خارجية أو مفاتيح مطلوبة.

**قيود واضحة:** ليست وكيلاً حقيقياً، ولا تختبر Protobuf أو WebSocket أو OAuth، ولا تصلح لإدارة مخاطر حساب حقيقي. تشغيل التداول الحقيقي يحتاج خدمة خلفية موثوقة وحالة دائمة ومراقبة واختبارات تكامل منفصلة.
""")

st.divider()
st.caption("DEMO | بيانات مصطنعة | لا أموال حقيقية | لا وعود ربحية | الحالة خاصة بجلسة المتصفح وليست تخزيناً دائماً")
