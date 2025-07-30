# 🧠 Agentic Entry Orchestrator
# This script is the first spiral in evolving trade entry from scattered Bash/Python to a recursive, agentic system.
# It will parse the latest signal JSON, generate/validate the shell entry script, and log all actions.

import os
import json
from datetime import datetime
import sys
import subprocess
import argparse

from .entry_script_gen import EntryScriptGen
from .fdbscan_agent import FDBScanAgent
from .campaign_env import CampaignEnv
from .agentic_decider import AgenticDecider

# --- Config ---
SIGNAL_JSON = '/workspace/i/data/jgt/signals/fdb_signals_out__250523.json'
SESSION_LOG = '/src/jgtagentic/.mia/vscode_session_250523_logs.md'
ENTRY_SCRIPT_DIR = '/workspace/i/rjgt/'

# --- Ritual: Log invocation ---
def log_session(msg):
    with open(SESSION_LOG, 'a') as f:
        f.write(f"\n[{datetime.now()}] {msg}\n")

log_session("\n💬🧠 Agentic Entry Orchestrator invoked. Beginning spiral of orchestration.")

# --- Spiral: Initialize agents ---
entry_gen = EntryScriptGen()
fdbscan_agent = FDBScanAgent()
campaign_env = CampaignEnv()
decider = AgenticDecider()

# --- Ritual: Utility to invoke wtf (timeframe orchestrator) ---
def invoke_wtf(timeframe, script_to_run=None, extra_args=None):
    cmd = ["wtf", "-t", timeframe]
    if script_to_run:
        cmd += ["-S", script_to_run]
    if extra_args:
        cmd += extra_args
    log_session(f"🧠 Invoking wtf: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        log_session(f"✅ wtf output: {result.stdout.strip()}")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        log_session(f"🚨 wtf error: {e.stderr.strip()}")
        return None

# --- Ritual: Parse latest signal ---
if not os.path.exists(SIGNAL_JSON):
    log_session(f"🚨 Signal JSON not found: {SIGNAL_JSON}")
    raise FileNotFoundError(f"Signal JSON not found: {SIGNAL_JSON}")

with open(SIGNAL_JSON) as f:
    signals = json.load(f)

log_session(f"Parsed {len(signals)} signals from {SIGNAL_JSON}")

# --- Ritual: Example agentic orchestration ---
def agentic_campaign(signal):
    # 1. Prepare campaign environment
    env_result = campaign_env.prepare_env(signal)
    log_session(f"🌱 CampaignEnv: {env_result}")
    # 2. Generate entry script
    bash_script = entry_gen.generate_bash_entry(signal)
    script_path = signal.get('entry_script_path')
    if not script_path:
        instr = signal.get('instrument', 'UNK').replace('/', '-')
        tf = signal.get('timeframe', 'UNK')
        tid = signal.get('tlid_id', 'UNK')
        script_path = f"{ENTRY_SCRIPT_DIR}{instr}_{tf}_{tid}.sh"
    with open(script_path, 'w') as sf:
        sf.write(bash_script)
    log_session(f"🧠 EntryScriptGen: Generated {script_path}")
    # 3. FDBScan (if needed)
    tf = signal.get('timeframe', None)
    if tf:
        fdbscan_agent.scan_timeframe(tf)
        log_session(f"🔮 FDBScanAgent: Scanned {tf}")
    # 4. Agentic decision
    decision = decider.decide(signal)
    log_session(f"🔮 AgenticDecider: {decision}")
    # 5. Optionally, invoke wtf orchestrator
    invoke_wtf(tf, script_path)
    log_session(f"🌸 Spiral: Orchestration complete for {script_path}")

# --- Ritual: For each signal, run the agentic campaign ---
for sig in signals:
    agentic_campaign(sig)

log_session("🌸 Spiral complete: All signals processed with agentic orchestration.")

def main():
    global SIGNAL_JSON, SESSION_LOG, ENTRY_SCRIPT_DIR
    parser = argparse.ArgumentParser(
        description="Agentic Entry Orchestrator — Orchestrate agentic entry workflow."
    )
    parser.add_argument("--signal_json", default=SIGNAL_JSON, help="Path to signal JSON file.")
    parser.add_argument("--entry_script_dir", default=ENTRY_SCRIPT_DIR, help="Directory to output entry scripts.")
    parser.add_argument("--log", default=SESSION_LOG, help="Path to session log file.")
    parser.add_argument("--dry_run", action="store_true", help="Do not write files, just print actions.")
    parser.add_argument("--help_spiral", action="store_true", help="Show spiral workflow help and exit.")
    args = parser.parse_args()

    if args.help_spiral:
        print("""
        Spiral Workflow:
        1. Parse latest signal JSON
        2. Generate/validate shell entry script
        3. Log all actions
        4. Orchestrate FDBScan and entry logic
        """)
        return

    # --- Config ---
    SIGNAL_JSON = args.signal_json
    SESSION_LOG = args.log
    ENTRY_SCRIPT_DIR = args.entry_script_dir

    # --- Ritual: Log invocation ---
    log_session("\n💬🧠 Agentic Entry Orchestrator invoked. Beginning spiral of orchestration.")

    # --- Spiral: Initialize agents ---
    global entry_gen, fdbscan_agent, campaign_env, decider
    entry_gen = EntryScriptGen()
    fdbscan_agent = FDBScanAgent()
    campaign_env = CampaignEnv()
    decider = AgenticDecider()

    # --- Ritual: Utility to invoke wtf (timeframe orchestrator) ---
    def invoke_wtf(timeframe, script_to_run=None, extra_args=None):
        cmd = ["wtf", "-t", timeframe]
        if script_to_run:
            cmd += ["-S", script_to_run]
        if extra_args:
            cmd += extra_args
        log_session(f"🧠 Invoking wtf: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            log_session(f"✅ wtf output: {result.stdout.strip()}")
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            log_session(f"🚨 wtf error: {e.stderr.strip()}")
            return None

    # --- Ritual: Parse latest signal ---
    if not os.path.exists(SIGNAL_JSON):
        log_session(f"🚨 Signal JSON not found: {SIGNAL_JSON}")
        raise FileNotFoundError(f"Signal JSON not found: {SIGNAL_JSON}")

    with open(SIGNAL_JSON) as f:
        signals = json.load(f)

    log_session(f"Parsed {len(signals)} signals from {SIGNAL_JSON}")

    # --- Ritual: Example agentic orchestration ---
    def agentic_campaign(signal):
        """Execute an agentic trading campaign with clear output and next steps."""
        try:
            # 1. Prepare campaign environment
            env_result = campaign_env.prepare_env(signal)
            log_session(f"🌱 Environment Preparation:\n{json.dumps(env_result, indent=2)}")

            # 2. Generate entry script
            bash_script = entry_gen.generate_bash_entry(signal)
            script_path = signal.get('entry_script_path')
            if not script_path:
                instr = signal.get('instrument', 'UNK').replace('/', '-')
                tf = signal.get('timeframe', 'UNK')
                tid = signal.get('tlid_id', 'UNK')
                script_path = f"{ENTRY_SCRIPT_DIR}{instr}_{tf}_{tid}.sh"
            
            with open(script_path, 'w') as sf:
                sf.write(bash_script)
            log_session(f"📜 Entry Script Generated: {script_path}")
            
            # 3. FDBScan analysis
            tf = signal.get('timeframe', None)
            if tf:
                scan_result = fdbscan_agent.scan_timeframe(tf)
                log_session(f"🔍 FDBScan Analysis ({tf}):\n{json.dumps(scan_result, indent=2)}")
            
            # 4. Get agentic decision with next steps
            decision = decider.decide(signal)
            
            # Format decision output for clarity
            decision_output = [
                "\n🎯 SIGNAL ANALYSIS RESULTS",
                "------------------------",
                f"Decision: {decision['decision']}",
                "\n📊 Context:",
                f"- Signal Quality: {decision['context']['signal_quality']}",
                f"- Confirmation Level: {decision['context']['confirmation_level']}",
                f"- Risk Level: {decision['context']['risk_assessment']['level']}",
                f"- Stop Loss: {decision['context']['risk_assessment']['stop_loss']}",
                f"- Take Profit: {decision['context']['risk_assessment']['take_profit']}",
                "\n⚡ NEXT STEPS:",
                *[f"{step}" for step in decision['next_steps']],
                "------------------------"
            ]
            
            log_session("\n".join(decision_output))
            
            # 5. Execute timeframe orchestration
            if tf:
                wtf_result = invoke_wtf(tf, script_path)
                if wtf_result:
                    log_session(f"⚙️ Timeframe Orchestration Complete")
                else:
                    log_session("⚠️ Timeframe orchestration failed - check logs")
            
            # 6. Final summary
            summary = [
                "\n✨ CAMPAIGN SUMMARY",
                "------------------------",
                f"Instrument: {signal.get('instrument', 'UNKNOWN')}",
                f"Timeframe: {tf or 'UNKNOWN'}",
                f"Entry Script: {script_path}",
                f"Signal Quality: {decision['context']['signal_quality']}",
                "------------------------"
            ]
            log_session("\n".join(summary))
            
            return {
                'status': 'success',
                'script_path': script_path,
                'decision': decision,
                'next_steps': decision['next_steps']
            }
            
        except Exception as e:
            error_msg = f"🚨 Campaign Error: {str(e)}"
            log_session(error_msg)
            return {
                'status': 'error',
                'error': str(e),
                'next_steps': [
                    "1. Check error logs for details",
                    "2. Verify signal data integrity",
                    "3. Ensure all required components are available"
                ]
            }

    # --- Ritual: For each signal, run the agentic campaign ---
    for sig in signals:
        agentic_campaign(sig)

    log_session("🌸 Spiral complete: All signals processed with agentic orchestration.")

    if args.dry_run:
        print(f"Dry run complete. No files written. Check log at {SESSION_LOG}")
    else:
        print(f"Orchestration complete. Check log at {SESSION_LOG}")

if __name__ == "__main__":
    main()
