"""Streamlit UI — AI DevOps Incident Responder."""

import asyncio
import concurrent.futures
import sys
from pathlib import Path

import litellm
import streamlit as st

litellm.suppress_warnings = True
litellm.set_verbose = False

sys.path.insert(0, str(Path(__file__).parent))

from src.agents.log_analyzer import KubernetesAgent, LogAnalyzerAgent, SummarizerAgent
from src.config import Config


def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(asyncio.run, coro).result()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


st.set_page_config(
    page_title="AI Incident Responder",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODE_META = {
    "Summarizer Dashboard": {
        "icon": "📊",
        "desc": "Executive-level infrastructure health summary using all available tools.",
    },
    "Kubernetes Operations": {
        "icon": "☸️",
        "desc": "Deep kubectl inspection — pods, logs, events, and patches.",
    },
    "Full Analysis": {
        "icon": "🔍",
        "desc": "Triage agent routes your query to the right specialist automatically.",
    },
}


def apply_styles() -> None:
    st.markdown(
        """
        <style>
        /* ── Base ───────────────────────────────────────────── */
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #0a0f1e !important;
            color: #e2e8f0 !important;
        }
        .block-container {
            max-width: 1100px;
            padding-top: 1.75rem;
            padding-bottom: 5rem;
            background: #0a0f1e;
        }

        /* ── Sidebar ─────────────────────────────────────────── */
        [data-testid="stSidebar"] {
            background: #060b18 !important;
            border-right: 1px solid #1e293b !important;
        }
        [data-testid="stSidebar"] * {
            color: #cbd5e1 !important;
        }
        [data-testid="stSidebar"] .stSelectbox label,
        [data-testid="stSidebar"] .stCaption {
            color: #64748b !important;
        }
        [data-testid="stSidebar"] hr {
            border-color: #1e293b !important;
        }

        /* ── Page header ─────────────────────────────────────── */
        .ir-header {
            display: flex;
            align-items: flex-start;
            gap: 1rem;
            border-bottom: 1px solid #1e293b;
            margin-bottom: 1.5rem;
            padding-bottom: 1.25rem;
        }
        .ir-header-icon { font-size: 2.4rem; line-height: 1; flex-shrink: 0; }
        .ir-header h1 {
            font-size: 1.65rem;
            font-weight: 700;
            margin: 0 0 .2rem;
            color: #f1f5f9;
        }
        .ir-header p { font-size: .9rem; color: #64748b; margin: 0; }

        /* ── Mode badge ──────────────────────────────────────── */
        .ir-badge {
            display: inline-flex;
            align-items: center;
            gap: .35rem;
            background: #0f2044;
            border: 1px solid #1e40af;
            border-radius: 20px;
            color: #93c5fd;
            font-size: .78rem;
            font-weight: 600;
            letter-spacing: .02em;
            padding: .25rem .75rem;
            margin-bottom: 1.25rem;
        }

        /* ── Stat cards ──────────────────────────────────────── */
        .ir-stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: .75rem;
            margin-bottom: 1.5rem;
        }
        .ir-card {
            background: #0d1526;
            border: 1px solid #1e293b;
            border-radius: 10px;
            padding: .9rem 1rem;
        }
        .ir-card-label {
            font-size: .7rem;
            font-weight: 600;
            letter-spacing: .07em;
            text-transform: uppercase;
            color: #475569;
            margin-bottom: .3rem;
        }
        .ir-card-value {
            font-size: .95rem;
            font-weight: 600;
            color: #f1f5f9;
        }
        .ir-card-sub { font-size: .75rem; color: #475569; margin-top: .15rem; }

        /* ── Empty state ─────────────────────────────────────── */
        .ir-empty {
            border: 1.5px dashed #1e293b;
            border-radius: 10px;
            color: #475569;
            font-size: .93rem;
            margin-top: .5rem;
            padding: 2rem 1.5rem;
            text-align: center;
        }
        .ir-empty strong {
            color: #94a3b8;
            display: block;
            font-size: 1rem;
            margin-bottom: .4rem;
        }

        /* ── Chat messages ───────────────────────────────────── */
        div[data-testid="stChatMessage"] {
            background: #0d1526 !important;
            border: 1px solid #1e293b !important;
            border-radius: 10px;
            padding: .4rem .65rem;
            margin-bottom: .4rem;
        }

        /* ── Tool row (sidebar) ──────────────────────────────── */
        .ir-tool-row {
            display: flex;
            align-items: center;
            gap: .5rem;
            font-size: .83rem;
            padding: .3rem 0;
            color: #cbd5e1;
        }
        .ir-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
        .ir-dot-green  { background: #22c55e; }
        .ir-dot-yellow { background: #f59e0b; }
        .ir-tool-note  { font-size: .72rem; color: #475569; }

        /* ── Sidebar title ───────────────────────────────────── */
        .ir-sidebar-title {
            font-size: 1.05rem;
            font-weight: 700;
            color: #f1f5f9;
            margin-bottom: .1rem;
        }

        @media (max-width: 768px) {
            .ir-stats { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def initialize_session_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agents" not in st.session_state:
        try:
            Config.validate()
            st.session_state.agents = {
                "Summarizer Dashboard": SummarizerAgent(),
                "Kubernetes Operations": KubernetesAgent(),
                "Full Analysis": LogAnalyzerAgent(),
            }
        except ValueError as exc:
            st.error(f"Configuration error: {exc}")
            st.stop()


def display_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            '<div class="ir-sidebar-title">🚨 Incident Responder</div>', unsafe_allow_html=True
        )
        st.caption(f"Model · `{Config.GEMINI_MODEL}`")
        st.divider()

        st.selectbox("Agent Mode", list(MODE_META.keys()), key="agent_mode")
        mode = st.session_state.get("agent_mode", "Summarizer Dashboard")
        st.caption(MODE_META[mode]["desc"])

        st.divider()
        st.caption("TOOLS")

        tools = [
            ("📋", "Log Tools", True),
            ("🐳", "Docker", Config.DOCKER_ENABLED),
            ("☸️", "Kubernetes", Config.K8S_ENABLED),
            ("🐙", "GitHub CLI", bool(Config.GITHUB_TOKEN)),
        ]
        for icon, name, enabled in tools:
            dot = "ir-dot-green" if enabled else "ir-dot-yellow"
            note = "live" if enabled else "simulation"
            st.markdown(
                f'<div class="ir-tool-row">'
                f'<span class="ir-dot {dot}"></span>'
                f"{icon} {name}"
                f'<span class="ir-tool-note">({note})</span>'
                f"</div>",
                unsafe_allow_html=True,
            )

        st.divider()
        if st.button("🗑 Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()


def render_header(mode: str) -> None:
    meta = MODE_META[mode]
    st.markdown(
        f"""
        <div class="ir-header">
            <div class="ir-header-icon">🚨</div>
            <div>
                <h1>AI DevOps Incident Responder</h1>
                <p>{meta["desc"]}</p>
            </div>
        </div>
        <div class="ir-badge">{meta["icon"]} {mode}</div>
        """,
        unsafe_allow_html=True,
    )


def render_stats() -> None:
    k8s = "Live ✓" if Config.K8S_ENABLED else "Simulation"
    dock = "Live ✓" if Config.DOCKER_ENABLED else "Simulation"
    gh = "Connected ✓" if Config.GITHUB_TOKEN else "No token"

    st.markdown(
        f"""
        <div class="ir-stats">
            <div class="ir-card">
                <div class="ir-card-label">Kubernetes</div>
                <div class="ir-card-value">{k8s}</div>
                <div class="ir-card-sub">kubectl</div>
            </div>
            <div class="ir-card">
                <div class="ir-card-label">Docker</div>
                <div class="ir-card-value">{dock}</div>
                <div class="ir-card-sub">docker CLI</div>
            </div>
            <div class="ir-card">
                <div class="ir-card-label">GitHub</div>
                <div class="ir-card-value">{gh}</div>
                <div class="ir-card-sub">gh CLI</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


async def get_response(user_input: str, mode: str) -> str:
    return await st.session_state.agents[mode].process_query(user_input)


def handle_input(user_input: str) -> None:
    mode = st.session_state.get("agent_mode", "Summarizer Dashboard")
    icon = MODE_META[mode]["icon"]

    st.session_state.messages.append({"role": "user", "content": user_input, "agent": mode})
    with st.chat_message("user"):
        st.markdown(f"**[{mode}]** {user_input}")

    with st.chat_message("assistant"):
        with st.status(f"{icon} {mode} analysing…", expanded=True) as status:
            st.write("🤖 Agent started…")
            st.write("🔧 Calling tools…")
            response = run_async(get_response(user_input, mode))
            status.update(label=f"✅ {mode} complete", state="complete", expanded=False)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response, "agent": mode})


def main() -> None:
    apply_styles()
    initialize_session_state()
    display_sidebar()

    mode = st.session_state.get("agent_mode", "Summarizer Dashboard")
    render_header(mode)
    render_stats()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            prefix = f"**[{msg.get('agent', '')}]** " if msg.get("agent") else ""
            st.markdown(f"{prefix}{msg['content']}")

    if not st.session_state.messages:
        st.markdown(
            '<div class="ir-empty">'
            "<strong>No active incidents</strong>"
            "Ask about your cluster, containers, GitHub Actions pipelines, or paste log output."
            "</div>",
            unsafe_allow_html=True,
        )

    if prompt := st.chat_input(
        "Describe the incident or ask about cluster / logs / Docker / GitHub…"
    ):
        handle_input(prompt)


if __name__ == "__main__":
    main()
