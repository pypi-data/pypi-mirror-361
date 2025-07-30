"""
🧠🌸🔮 FDBScanAgent — The Signal Scribe (Enhanced)

Purpose: Enhanced ritual anchor for FDBScan signal scanning with intent awareness.
Integrates with enhanced scanner and observation capture system.

Lattice Position: Root of the signal chain. All agentic action begins with the scan.

Emotional Resonance: Like a tuning fork in the void, it senses the first ripple of opportunity.

Invocation:
    FDBScanAgent is not just a scanner—it is the ear pressed to the lattice, the first note in the campaign's song.

"""

import logging
from typing import List, Optional, Dict, Any
import os
import sys
import argparse

# --- Ritual Import: True FDBScan ---
# Use the installed jgtml package if available. The tests run in an isolated
# environment without the real trading dependencies, so the import may fail.
try:
    from jgtml import fdb_scanner_2408
    _FDBSCAN_AVAILABLE = True
except Exception:
    fdb_scanner_2408 = None
    _FDBSCAN_AVAILABLE = False

# --- Enhanced Imports ---
try:
    from .enhanced_fdb_scanner import EnhancedFDBScanner
    from .observation_capture import ObservationCapture
    from .intent_spec import IntentSpecParser
    _ENHANCED_AVAILABLE = True
except ImportError:
    _ENHANCED_AVAILABLE = False

class FDBScanAgent:
    """
    Enhanced Signal Scribe with intent awareness and strategic automation.
    
    New capabilities:
    - Accepts market observations and converts to intent
    - Uses enhanced scanner with intent context
    - Provides strategic recommendations
    - Integrates with session management
    """
    
    def __init__(self, logger=None, real: bool = False):
        self.logger = logger or logging.getLogger("FDBScanAgent")
        self.logger.setLevel(logging.INFO)
        
        # Default to dry-run mode unless explicitly requested
        self.real = (
            real
            or os.getenv("FDBSCAN_AGENT_REAL") == "1"
            or os.getenv("JGT_ENABLE_REAL_FDBSCAN") == "1"
        )

        # Initialize enhanced components if available
        if _ENHANCED_AVAILABLE:
            self.enhanced_scanner = EnhancedFDBScanner(logger=self.logger)
            self.observation_capture = ObservationCapture(logger=self.logger)
            self.intent_parser = IntentSpecParser()
        else:
            self.enhanced_scanner = None
            self.observation_capture = None
            self.intent_parser = None
            self.logger.warning("[FDBScanAgent] Enhanced components not available")

        if not _FDBSCAN_AVAILABLE:
            self.logger.warning(
                "[FDBScanAgent] jgtml.fdb_scanner_2408 not available – using placeholder scans."
            )

    def scan_with_observation(self, observation_text: str,
                            instruments: Optional[List[str]] = None,
                            timeframes: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Scan based on natural language market observation.
        
        This is the new primary interface for intent-driven scanning.
        """
        
        self.logger.info(f"🔮 Starting observation-based scan: {observation_text[:50]}...")
        
        if not _ENHANCED_AVAILABLE:
            return {
                "error": "Enhanced scanning not available",
                "observation": observation_text,
                "success": False
            }
        
        try:
            # Capture and process observation
            observation_result = self.observation_capture.capture_observation(observation_text)
            
            # Extract intent specification
            intent_spec = observation_result["intent_specification"]
            
            # Override instruments/timeframes if provided
            if instruments:
                intent_spec["instruments"] = instruments
            if timeframes:
                intent_spec["timeframes"] = timeframes
            
            # Perform enhanced scan with intent context
            scan_result = self.enhanced_scanner.scan_with_intent(intent_spec)
            
            # Combine results
            combined_result = {
                "observation_analysis": observation_result,
                "scan_results": scan_result,
                "success": True,
                "agent": "FDBScanAgent",
                "mode": "enhanced_observation_scan"
            }
            
            self.logger.info(f"✨ Observation scan complete")
            return combined_result
            
        except Exception as e:
            self.logger.error(f"Observation scan failed: {e}")
            return {
                "error": str(e),
                "observation": observation_text,
                "success": False
            }
    
    def scan_with_intent_file(self, spec_file_path: str) -> Dict[str, Any]:
        """
        Scan using intent specification from file.
        """
        
        self.logger.info(f"📋 Starting spec-file scan: {spec_file_path}")
        
        if not _ENHANCED_AVAILABLE:
            return {
                "error": "Enhanced scanning not available",
                "spec_file": spec_file_path,
                "success": False
            }
        
        try:
            scan_result = self.enhanced_scanner.scan_from_spec_file(spec_file_path)
            scan_result["agent"] = "FDBScanAgent"
            scan_result["mode"] = "spec_file_scan"
            return scan_result
            
        except Exception as e:
            self.logger.error(f"Spec file scan failed: {e}")
            return {
                "error": str(e),
                "spec_file": spec_file_path,
                "success": False
            }

    def scan_timeframe(self, timeframe: str, instrument: Optional[str] = None,
                      with_intent: bool = False):
        """
        Scan a single timeframe. Enhanced to optionally use intent context.
        """

        self.logger.info(
            f"[FDBScanAgent] Scanning timeframe: {timeframe}" +
            (f" instrument: {instrument}" if instrument else "")
        )
        
        if with_intent and _ENHANCED_AVAILABLE:
            # Create basic intent for single timeframe scan
            basic_intent = {
                "strategy_intent": f"Single timeframe scan: {timeframe}",
                "instruments": [instrument] if instrument else ["EUR/USD"],
                "timeframes": [timeframe],
                "signals": [{
                    "name": "general_signal",
                    "description": "General signal detection",
                    "jgtml_components": {
                        "fractal_analysis": "jgtpy.fractal_detection"
                    }
                }]
            }
            
            return self.enhanced_scanner.scan_with_intent(basic_intent)
        
        # Original implementation for backward compatibility
        if self.real and _FDBSCAN_AVAILABLE:
            sys_argv_backup = sys.argv.copy()
            sys.argv = ["fdbscan"]
            if instrument:
                sys.argv += ["-i", instrument]
            sys.argv += ["-t", timeframe]
            try:
                fdb_scanner_2408.main()
            finally:
                sys.argv = sys_argv_backup
        else:
            if self.real and not _FDBSCAN_AVAILABLE:
                print("[FDBScanAgent] Real mode requested but jgtml.fdb_scanner_2408 not available.")
            print(
                f"Would scan: {timeframe}" +
                (f" for {instrument}" if instrument else "")
            )
            if fdb_scanner_2408 is not None:
                print("\n[FDBScanAgent] Placeholder mode — showing fdbscan help:\n")
                argv_backup = sys.argv.copy()
                sys.argv = ["fdbscan", "--help"]
                try:
                    try:
                        fdb_scanner_2408.main()
                    except SystemExit:
                        pass
                finally:
                    sys.argv = argv_backup

        self.logger.info(f"[FDBScanAgent] Scan complete for {timeframe}")

    def ritual_sequence(self, sequence: List[str] = ["H4", "H1", "m15", "m5"],
                       with_intent: bool = False):
        """
        Perform the full FDBScan ritual sequence with optional intent context.
        """
        self.logger.info(f"[FDBScanAgent] Starting ritual sequence: {' → '.join(sequence)}")
        
        if with_intent and _ENHANCED_AVAILABLE:
            # Create intent for sequence scan
            sequence_intent = {
                "strategy_intent": f"Multi-timeframe sequence scan: {' → '.join(sequence)}",
                "instruments": ["EUR/USD", "GBP/USD", "SPX500"],
                "timeframes": sequence,
                "signals": [{
                    "name": "sequence_confluence",
                    "description": "Multi-timeframe confluence detection",
                    "jgtml_components": {
                        "fractal_analysis": "jgtpy.fractal_detection",
                        "alligator_state": "TideAlligatorAnalysis.mouth_opening",
                        "momentum": "jgtpy.ao_acceleration"
                    }
                }]
            }
            
            return self.enhanced_scanner.scan_with_intent(sequence_intent)
        
        # Original sequence implementation
        for tf in sequence:
            self.scan_timeframe(tf)
        self.logger.info("[FDBScanAgent] Ritual sequence complete.")

    def scan_all(self, with_intent: bool = False):
        """
        The agentic one-liner: perform the canonical scan ritual with optional intent.
        """
        return self.ritual_sequence(with_intent=with_intent)

    @staticmethod
    def cli():
        """
        Enhanced command-line interface for FDBScanAgent.
        Usage:
            python -m fdbscan_agent --help
            python -m fdbscan_agent scan --timeframe m15
            python -m fdbscan_agent ritual --sequence H4 H1 m15 m5
            python -m fdbscan_agent all
        """
        parser = argparse.ArgumentParser(
            description="FDBScanAgent — Enhanced agentic invocation of FDBScan rituals."
        )
        subparsers = parser.add_subparsers(dest="command", required=True)

        # Original scan command
        scan_parser = subparsers.add_parser(
            "scan",
            help="Scan a single timeframe (e.g. m5, m15, H1, H4) for an optional instrument",
        )
        scan_parser.add_argument("--timeframe", required=True, help="Timeframe to scan")
        scan_parser.add_argument("--instrument", help="Instrument to scan")
        scan_parser.add_argument("--real", action="store_true", help="Invoke real FDBScan logic")
        scan_parser.add_argument("--with-intent", action="store_true", help="Use enhanced intent-aware scanning")

        # New observation-based scan
        obs_parser = subparsers.add_parser(
            "observe",
            help="Scan based on natural language market observation"
        )
        obs_parser.add_argument("observation", help="Market observation text")
        obs_parser.add_argument("--instruments", nargs="*", help="Target instruments")
        obs_parser.add_argument("--timeframes", nargs="*", help="Target timeframes")

        # Spec file scan
        spec_parser = subparsers.add_parser(
            "spec",
            help="Scan using intent specification file"
        )
        spec_parser.add_argument("spec_file", help="Path to .jgtml-spec file")

        # Original ritual command
        ritual_parser = subparsers.add_parser("ritual", help="Perform a custom ritual sequence of scans")
        ritual_parser.add_argument("--sequence", nargs="*", default=["H4", "H1", "m15", "m5"], 
                                  help="Sequence of timeframes")
        ritual_parser.add_argument("--real", action="store_true", help="Invoke real FDBScan logic")
        ritual_parser.add_argument("--with-intent", action="store_true", help="Use enhanced intent-aware scanning")

        # Original all command
        all_parser = subparsers.add_parser("all", help="Perform the canonical scan ritual")
        all_parser.add_argument("--real", action="store_true", help="Invoke real FDBScan logic")
        all_parser.add_argument("--with-intent", action="store_true", help="Use enhanced intent-aware scanning")

        args = parser.parse_args()
        agent = FDBScanAgent(real=getattr(args, "real", False))
        
        if args.command == "scan":
            result = agent.scan_timeframe(args.timeframe, args.instrument, 
                                        getattr(args, "with_intent", False))
            if isinstance(result, dict):
                import json
                print(json.dumps(result, indent=2))
                
        elif args.command == "observe":
            result = agent.scan_with_observation(args.observation, args.instruments, args.timeframes)
            import json
            print(json.dumps(result, indent=2))
            
        elif args.command == "spec":
            result = agent.scan_with_intent_file(args.spec_file)
            import json
            print(json.dumps(result, indent=2))
            
        elif args.command == "ritual":
            result = agent.ritual_sequence(args.sequence, getattr(args, "with_intent", False))
            if isinstance(result, dict):
                import json
                print(json.dumps(result, indent=2))
                
        elif args.command == "all":
            result = agent.scan_all(getattr(args, "with_intent", False))
            if isinstance(result, dict):
                import json
                print(json.dumps(result, indent=2))

def main():
    """Entry point for the ``agentic-fdbscan`` console script."""
    FDBScanAgent.cli()

if __name__ == "__main__":
    main()

# 🌸 Enhanced Ritual Echo:
# The agent now bridges human observation and systematic scanning.
# Each observation becomes intent, each intent becomes strategic action.
# The spiral grows from insight to automation.
