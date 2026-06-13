from app.ai.agent1_triage import run_triage_agent
from app.ai.agent2_analyst import run_analyst_agent
from app.ai.agent3_synthesizer import run_synthesizer_agent
from app.ai.agent4_reporter import run_reporter_agent


def run_full_ai_pipeline(analysis_json: dict) -> dict:
    triage_result = run_triage_agent(analysis_json)
    print("Agent 1 Triage complete")

    analyst_result = run_analyst_agent(analysis_json, triage_result)
    print("Agent 2 Analysis complete")

    synthesizer_result = run_synthesizer_agent(analysis_json, triage_result, analyst_result)
    print("Agent 3 Synthesis complete")

    report_result = run_reporter_agent(analysis_json, triage_result, analyst_result, synthesizer_result)
    print("Agent 4 Report complete")

    return {
        "triage": triage_result,
        "analysis": analyst_result,
        "risk_assessment": synthesizer_result,
        "report": report_result,
        "final_risk_score": synthesizer_result.get("final_risk_score"),
        "risk_level": synthesizer_result.get("risk_level"),
    }
