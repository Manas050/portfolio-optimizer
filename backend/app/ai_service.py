"""
Gemini AI research service for portfolio analysis.

Provides a streaming endpoint that gives portfolio-aware market insights
and stock research using Google's Gemini model.
"""

import json
import logging
from typing import AsyncGenerator

import google.generativeai as genai

from app.config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

# ── System prompt template ───────────────────────────────────────────

_BASE_SYSTEM_PROMPT = """You are an expert Indian equity market analyst and portfolio advisor with deep knowledge of:
- NSE/BSE listed companies and their fundamentals
- Nifty 50, Nifty Next 50, and Midcap indices
- Modern Portfolio Theory and efficient frontier analysis
- Macroeconomic factors affecting Indian markets (RBI policy, FII/DII flows, INR, oil prices)
- Sector dynamics: IT, Banking, FMCG, Pharma, Auto, Energy, Infrastructure, Metals

Your communication style:
- Direct, precise, and data-driven
- Use concise bullet points and structured analysis
- Flag risks clearly alongside opportunities
- Refer to Indian-specific factors (SEBI regulations, GST impact, budget cycles)
- All monetary values in INR unless stated otherwise

IMPORTANT CONSTRAINTS:
- Never give advice that guarantees returns
- Always mention that past performance is not indicative of future results
- This is for informational/educational purposes only
"""

def _build_portfolio_context_block(portfolio_context: dict | None) -> str:
    """Convert the optimizer's output into a readable context block for Gemini."""
    if not portfolio_context:
        return ""

    lines = ["\n\n══ USER'S CURRENT PORTFOLIO CONTEXT ══"]

    # Holdings
    holdings = portfolio_context.get("holdings", [])
    if holdings:
        lines.append("\nHoldings:")
        for h in holdings:
            sym = h.get("symbol", "").replace(".NS", "")
            lines.append(
                f"  • {sym}: {h.get('units', 0)} units "
                f"@ ₹{h.get('price', 0):,.0f} = ₹{h.get('value', 0):,.0f} "
                f"({h.get('weight', 0)*100:.1f}%)"
            )

    tv = portfolio_context.get("total_value")
    if tv:
        lines.append(f"\nTotal Portfolio Value: ₹{tv:,.0f}")

    # Current metrics
    cur = portfolio_context.get("current_portfolio", {})
    if cur:
        lines.append(f"\nCurrent Allocation Metrics:")
        lines.append(f"  Return (annualised): {cur.get('expected_return', 0)*100:.2f}%")
        lines.append(f"  Volatility (annualised): {cur.get('volatility', 0)*100:.2f}%")
        lines.append(f"  Sharpe Ratio: {cur.get('sharpe_ratio', 0):.3f}")

    # Optimal allocation
    opt = portfolio_context.get("optimal_sharpe", {})
    if opt:
        lines.append(f"\nOptimizer Recommended Allocation (Max Sharpe):")
        weights = opt.get("weights", {})
        for sym, w in sorted(weights.items(), key=lambda x: -x[1]):
            if w > 0.005:
                lines.append(f"  • {sym.replace('.NS','')}: {w*100:.1f}%")
        lines.append(f"  → Expected Return: {opt.get('expected_return', 0)*100:.2f}%")
        lines.append(f"  → Volatility: {opt.get('volatility', 0)*100:.2f}%")
        lines.append(f"  → Sharpe Ratio: {opt.get('sharpe_ratio', 0):.3f}")

    # Min vol allocation
    minvol = portfolio_context.get("min_volatility", {})
    if minvol:
        lines.append(f"\nMin-Volatility Allocation:")
        weights = minvol.get("weights", {})
        for sym, w in sorted(weights.items(), key=lambda x: -x[1]):
            if w > 0.005:
                lines.append(f"  • {sym.replace('.NS','')}: {w*100:.1f}%")
        lines.append(f"  → Volatility: {minvol.get('volatility', 0)*100:.2f}%")
        lines.append(f"  → Sharpe Ratio: {minvol.get('sharpe_ratio', 0):.3f}")

    rf = portfolio_context.get("risk_free_rate")
    if rf:
        lines.append(f"\nRisk-Free Rate used: {rf*100:.1f}% (India 91-day T-bill)")

    lines.append("══════════════════════════════════════\n")
    return "\n".join(lines)


async def stream_research(
    query: str,
    portfolio_context: dict | None = None,
    history: list[dict] | None = None,
) -> AsyncGenerator[str, None]:
    """
    Stream a Gemini response for the given research query.

    Yields SSE-formatted strings: `data: <text chunk>\\n\\n`
    Final message: `data: [DONE]\\n\\n`

    Args:
        query: The user's research question.
        portfolio_context: The full optimizer response dict (optional).
        history: Previous conversation turns [{role, text}] for multi-turn.
    """
    if not GEMINI_API_KEY:
        yield 'data: ⚠ GEMINI_API_KEY not configured. Add it to backend/.env and restart the server.\n\n'
        yield 'data: [DONE]\n\n'
        return

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            system_instruction=_BASE_SYSTEM_PROMPT + _build_portfolio_context_block(portfolio_context),
        )

        # Build conversation history for multi-turn
        chat_history = []
        if history:
            for turn in history:
                role = "user" if turn.get("role") == "user" else "model"
                chat_history.append({"role": role, "parts": [turn.get("text", "")]})

        chat = model.start_chat(history=chat_history)

        response = chat.send_message(
            query,
            stream=True,
            generation_config=genai.GenerationConfig(
                temperature=0.7,
                max_output_tokens=2048,
            ),
        )

        for chunk in response:
            text = chunk.text
            if text:
                # Escape newlines for SSE; client will unescape
                escaped = text.replace("\n", "\\n")
                yield f"data: {escaped}\n\n"

        yield "data: [DONE]\n\n"

    except Exception as e:
        logger.error("Gemini stream error: %s", e)
        err = str(e).replace("\n", " ")
        yield f"data: ⚠ AI Error: {err}\n\n"
        yield "data: [DONE]\n\n"
