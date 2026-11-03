"""Mobile-friendly Streamlit DEMO. No real trading or external API calls."""
import csv
import io
import math
import random
import time
from datetime import datetime, timezone

import streamlit as st


st.set_page_config(
    page_title="cTrader AI | DEMO",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
:root { color-scheme: dark; }
.stApp {
    background: #0b1220;
    color: #f1f5f9;
}
[data-testid="stAppViewContainer"] {
    background: #0b1220;
}
[data-testid="stHeader"] {
    background: rgba(11,18,32,.95);
}
.block-container {
    max-width: 1150px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}
h1,h2,h3,h4 {
    color: #f8fafc !important;
    direction: rtl;
    text-align: right;
}
h1 {
    font-size: clamp(1.7rem, 5vw, 2.7rem) !important;
    line-height: 1.5 !important;
}
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
    color: #e2e8f0;
    direction: rtl;
    text-align: right;
    line-height: 1.85;
}
[data-testid="stCaptionContainer"] p {
    color: #b8c9de !important;
}
[data-testid="stMetric"] {
    background: #142238;
    border: 1px solid #30445f;
    border-radius: 16px;
    padding: 18px;
    min-height: 130px;
}
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] * {
    color: #c3d3e6 !important;
    opacity: 1 !important;
}
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] * {
    color: #ffffff !important;
    opacity: 1 !important;
    -webkit-text-fill-color: #ffffff !important;
    font-weight: 750 !important;
    font-size: clamp(1.65rem, 5vw, 2.25rem) !important;
}
[data-testid="stWidgetLabel"] p {
    color: #f1f5f9 !important;
}
.stButton > button,
.stDownloadButton > button {
    min-height: 48px;
    border-radius: 12px;
    background: #182b43;
    border: 1px solid #45607e;
    color: #ffffff !important;
}
.stButton > button p,
.stDownloadButton > button p {
    color: #ffffff !important;
    text-align: center;
}
.stButton > button[kind="primary"] {
    background: #b42336 !important;
    border-color: #ef6677 !important;
}
.stButton > button:disabled {
    opacity: .5;
}
[data-testid="stExpander"] {
    border: 1px solid #30445f;
    border-radius: 12px;
    background: #111e30;
}
.notice {
    direction: rtl;
    text-align: right;
    background: #182b43;
    border-right: 4px solid #27d3b2;
    padding: 16px;
    border-radius: 12px;
    color: #edf5ff;
    line-height: 1.9;
    margin: 12px 0 20px;
}
.badge {
    display: inline-block;
    background: #403318;
    color: #ffe09b;
    border: 1px solid #89703a;
    border-radius: 20px;
    padding: 5px 14px;
    font-weight: bold;
}
@media (max-width: 640px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        padding-top: 1.4rem;
    }
    [data-testid="stMetric"] {
        min-height: 110px;
        padding: 14px;
    }
}
</style>
""", unsafe_allow_html=True)


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_account():
    rng = random.Random(42)
    prices = [1.08500]
    for _ in range(79):
        prices.append(round(prices[-1] + rng.uniform(-.00012, .00012), 5))
    return {
        "balance": 10000.0,
        "baseline": 10000.0,
        "prices": prices,
        "positions": [],
        "signal": None,
        "killed": False,
        "logs": [],
    }


if "demo_account" not in st.session_state:
    st.session_state.demo_account = new_account()

a = st.session_state.demo_account


def log(text):
    a["logs"].insert(0, {"time_utc": now(), "event": text})
    a["logs"] = a["logs"][:300]


def pnl(position, price):
    sign = 1 if position["side"] == "buy" else -1
    return (price - position["entry"]) * sign * position["units"]


def equity():
    return a["balance"] + sum(
        pnl(p, a["prices"][-1]) for p in a["positions"]
    )


def close_all(reason):
    for position in a["positions"]:
        a["balance"] += pnl(position, a["prices"][-1])
    a["positions"] = []
    a["signal"] = None
    log(reason)


def kill(reason):
    a["killed"] = True
    close_all(reason)


def drawdown():
    return max(
        0.0,
        (a["baseline"] - equity()) / a["baseline"] * 100,
    )


def check_limit(limit):
    if not a["killed"] and drawdown() >= limit:
        kill("تفعيل حد خسارة الجلسة؛ إغلاق المحاكاة وتعطيل التنفيذ")


st.markdown(
    '<span class="badge">DEMO — محاكاة فقط</span>',
    unsafe_allow_html=True,
)
st.title("لوحة تحكم وكيل التداول")
st.markdown("""
<div class="notice">
أسعار وصفقات افتراضية لاختبار الواجهة.
لا اتصال بحساب cTrader أو Telegram أو مزودي الذكاء الاصطناعي.
لا توجد أموال حقيقية أو عمليات سحب أو تحويل.
</div>
""", unsafe_allow_html=True)

# Visible on mobile, without opening the sidebar.
if st.button(
    "🛑 إيقاف طارئ — إغلاق المحاكاة وتعطيل التنفيذ",
    type="primary",
    use_container_width=True,
):
    kill("إيقاف طارئ يدوي")
    st.rerun()

with st.expander("⚙️ إعدادات المحاكاة والمخاطر", expanded=False):
    provider = st.selectbox(
        "النموذج المختار للعرض فقط",
        ["GPT-4o", "Claude", "Gemini"],
        key="display_provider",
    )
    st.caption("لا يُستدعى أي نموذج؛ الإشارة ناتجة عن قاعدة محلية بسيطة.")
    risk_percent = st.slider(
        "المخاطرة للصفقة %",
        min_value=.1, max_value=2.0, value=.5, step=.1,
        key="risk_percent",
    )
    daily_limit = st.slider(
        "حد خسارة الجلسة %",
        min_value=.5, max_value=5.0, value=2.0, step=.5,
        key="session_limit",
    )
    max_lots = st.slider(
        "أقصى حجم تجريبي Lots",
        min_value=.01, max_value=1.0, value=.10, step=.01,
        key="max_lots",
    )
    st.caption("حساب USD، ورمز EUR/USD، واللوت = 100,000 وحدة.")

check_limit(daily_limit)

if a["killed"]:
    st.error(
        "الإيقاف مفعّل. لن تُنشأ أو تُنفّذ إشارات جديدة. "
        "إعادة التفعيل متاحة فقط من قسم إعادة ضبط المحاكاة."
    )

page = st.selectbox(
    "اختر القسم",
    ["لوحة التحكم", "إدارة المخاطر", "سجل الأحداث", "مساعدة"],
)

if page == "لوحة التحكم":
    first, second = st.columns(2)
    first.metric("الرصيد USD", f'{a["balance"]:,.2f}')
    second.metric("حقوق الملكية USD", f"{equity():,.2f}")

    third, fourth = st.columns(2)
    third.metric(
        "أداء الجلسة USD",
        f'{equity() - a["baseline"]:+,.2f}',
    )
    fourth.metric("خسارة الجلسة", f"{drawdown():.2f}%")

    st.subheader("EUR/USD")
    st.caption(
        f'آخر سعر افتراضي: {a["prices"][-1]:.5f} — '
        "يتحرك فقط عند الضغط على تحديث السعر."
    )
    st.line_chart(a["prices"], height=250)

    if st.button("🔄 تحديث السعر التجريبي", use_container_width=True):
        price = max(
            .1,
            round(
                a["prices"][-1] + random.uniform(-.0008, .0008),
                5,
            ),
        )
        a["prices"].append(price)
        a["prices"] = a["prices"][-240:]
        remaining = []

        for position in a["positions"]:
            if position["side"] == "buy":
                hit = price <= position["sl"] or price >= position["tp"]
            else:
                hit = price >= position["sl"] or price <= position["tp"]

            if hit:
                a["balance"] += pnl(position, price)
                log("إغلاق عند عبور SL/TP بسعر التحديث الافتراضي")
            else:
                remaining.append(position)

        a["positions"] = remaining
        check_limit(daily_limit)
        st.rerun()

    if st.button(
        "🧠 إنشاء إشارة محاكاة",
        disabled=a["killed"] or bool(a["positions"]),
        use_container_width=True,
    ):
        prices = a["prices"]
        entry = prices[-1]
        average = sum(prices[-10:]) / 10
        side = "buy" if entry >= average else "sell"
        sign = 1 if side == "buy" else -1

        a["signal"] = {
            "direction": side,
            "confidence": .82,
            "entry": entry,
            "stop_loss": round(entry - sign * .002, 5),
            "take_profit": round(entry + sign * .004, 5),
            "analysis": "مقارنة السعر بمتوسط آخر عشرة أسعار افتراضية.",
            "reason": "اختبار واجهة فقط؛ الثقة ثابتة وليست احتمال نجاح.",
            "created_at": time.time(),
        }
        log(f"إنشاء إشارة محاكاة؛ النموذج للعرض فقط: {provider}")
        st.rerun()

    if a["signal"]:
        signal = a["signal"]
        expired = time.time() - signal["created_at"] > 120

        st.subheader("الإشارة التجريبية")
        direction = "شراء" if signal["direction"] == "buy" else "بيع"
        st.info(
            f'{direction} — درجة عرض ثابتة: 82% — '
            f'SL: {signal["stop_loss"]:.5f} — '
            f'TP: {signal["take_profit"]:.5f}'
        )
        st.caption("صلاحية الإشارة التجريبية دقيقتان من إنشائها.")
        with st.expander("عرض JSON"):
            st.json(signal)

        if expired:
            st.warning("انتهت صلاحية الإشارة. أنشئ إشارة جديدة.")

        if st.button(
            "✅ تأكيد فتح صفقة افتراضية",
            disabled=a["killed"] or bool(a["positions"]) or expired,
            use_container_width=True,
        ):
            # Validate again at click time.
            check_limit(daily_limit)
            entry = a["prices"][-1]
            sl = signal["stop_loss"]
            tp = signal["take_profit"]
            valid = (
                sl < entry < tp
                if signal["direction"] == "buy"
                else tp < entry < sl
            )

            if a["killed"]:
                st.error("التنفيذ متوقف.")
            elif time.time() - signal["created_at"] > 120:
                st.error("انتهت صلاحية الإشارة.")
            elif not valid:
                st.error("مستويات الحماية غير مناسبة للسعر الحالي.")
            else:
                distance = abs(entry - sl)
                reward = abs(tp - entry)
                budget = min(a["balance"], equity()) * risk_percent / 100
                units = math.floor(
                    min(
                        budget / (distance * 1.15),
                        max_lots * 100000,
                    ) / 1000
                ) * 1000

                if units < 1000:
                    st.error("الحجم أقل من الحد الأدنى التجريبي 0.01 لوت.")
                elif reward / distance < 1.5:
                    st.error("نسبة العائد إلى المخاطرة أقل من 1.5.")
                else:
                    a["positions"].append({
                        "side": signal["direction"],
                        "entry": entry,
                        "sl": sl,
                        "tp": tp,
                        "units": units,
                        "lots": units / 100000,
                    })
                    a["signal"] = None
                    log("فتح صفقة افتراضية مع SL وTP")
                    st.rerun()

    st.subheader("المراكز الافتراضية")
    if not a["positions"]:
        st.info("لا توجد مراكز مفتوحة.")
    else:
        for position in a["positions"]:
            st.write({
                "الاتجاه": (
                    "شراء" if position["side"] == "buy" else "بيع"
                ),
                "الحجم Lots": position["lots"],
                "سعر الدخول": position["entry"],
                "وقف الخسارة": position["sl"],
                "جني الأرباح": position["tp"],
                "الربح أو الخسارة USD": round(
                    pnl(position, a["prices"][-1]), 2
                ),
            })

        if st.button(
            "إغلاق الكل وإيقاف التنفيذ",
            use_container_width=True,
        ):
            kill("إغلاق يدوي وتعطيل التنفيذ")
            st.rerun()

elif page == "إدارة المخاطر":
    st.subheader("حدود الجلسة")
    st.write(f"المخاطرة لكل صفقة: {risk_percent:.1f}%")
    st.write(f"حد خسارة الجلسة: {daily_limit:.1f}%")
    st.write(f"أقصى حجم: {max_lots:.2f} Lots")
    st.write(f"الخسارة الحالية: {drawdown():.2f}%")
    st.progress(min(1.0, drawdown() / daily_limit))

    st.warning(
        "هذا حد جلسة وليس حداً يومياً دائماً. "
        "لا توجد مراقبة خلفية مستمرة، وتتغير الأسعار بالضغط فقط. "
        "قد تُفقد الحالة عند انتهاء الجلسة أو إعادة تشغيل الخادم."
    )
    st.write(
        "صفقة واحدة فقط، وقف خسارة وجني أرباح إلزاميان، "
        "تقريب الحجم للأسفل، وهامش تكلفة تقديري 15%."
    )

    st.subheader("إعادة ضبط المحاكاة")
    confirmed = st.checkbox(
        "أوافق على حذف صفقات وسجل هذه المحاكاة وإعادة الرصيد إلى 10,000 USD"
    )
    if st.button(
        "إعادة ضبط الحساب الافتراضي",
        disabled=not confirmed,
        use_container_width=True,
    ):
        st.session_state.demo_account = new_account()
        st.rerun()

elif page == "سجل الأحداث":
    st.subheader("سجل الجلسة — UTC")
    if not a["logs"]:
        st.info("لا توجد أحداث بعد.")
    else:
        st.dataframe(
            a["logs"],
            use_container_width=True,
            hide_index=True,
        )
        output = io.StringIO()
        writer = csv.DictWriter(
            output, fieldnames=["time_utc", "event"]
        )
        writer.writeheader()
        writer.writerows(a["logs"])
        st.download_button(
            "تنزيل سجل CSV",
            data="\ufeff" + output.getvalue(),
            file_name="demo-events.csv",
            mime="text/csv",
            use_container_width=True,
        )

else:
    st.subheader("كيفية الاستخدام")
    st.markdown("""
1. افتح **لوحة التحكم** واضغط تحديث السعر.
2. اضغط **إنشاء إشارة محاكاة**.
3. راجع الاتجاه ومستويات الحماية، ثم أكّد الصفقة الافتراضية.
4. حدّث السعر لمشاهدة تغيّر الربح والخسارة.
5. استخدم زر الطوارئ لإغلاق المحاكاة ومنع التنفيذ.
6. لإعادة البداية، افتح **إدارة المخاطر** ثم إعادة الضبط.

**لا تدخل أي مفاتيح سرية.** اختيار GPT-4o أو Claude أو Gemini
هنا للعرض فقط، ولا ينشئ اتصالاً بمزود الخدمة.

هذه النسخة ليست وكيلاً حقيقياً، ولا تختبر اتصال WebSocket
أو Protobuf أو OAuth. تشغيل التداول الفعلي يحتاج خدمة خلفية
مستقلة وحالة دائمة واختبارات تكامل ومراقبة.
""")

st.divider()
st.caption(
    "DEMO • بيانات مصطنعة • لا اتصال بحساب حقيقي • "
    "الحالة خاصة بجلسة المتصفح • لا وعود ربحية"
    )
