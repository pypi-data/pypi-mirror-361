"""
📖🧠 IntentSpecParser — The Intent Mirror (Enhanced)

Purpose: Parse and validate .jgtml-spec YAML files to extract trading intent.
Enhanced to consolidate all prototypes and provide comprehensive intent processing.
"""

from typing import Any, Dict, List, Optional
import yaml
import json
from datetime import datetime


class IntentSpecParser:
    """Enhanced parser for trading intent specifications."""

    def __init__(self):
        self.spec_history = []
        self.templates = IntentTemplateLibrary()

    def load(self, path: str) -> Dict[str, Any]:
        """Load and validate a YAML intent specification from path."""
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        validated_spec = self.validate_spec(data or {})
        self.spec_history.append({
            "path": path,
            "timestamp": datetime.now().isoformat(),
            "spec": validated_spec
        })
        
        return validated_spec

    def load_from_json(self, json_str: str) -> Dict[str, Any]:
        """Load intent specification from JSON string."""
        data = json.loads(json_str)
        return self.validate_spec(data)

    def validate_spec(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance intent specification."""
        
        # Ensure required fields exist
        validated = {
            "strategy_intent": spec.get("strategy_intent", "General Trading Strategy"),
            "instruments": spec.get("instruments", ["EUR/USD"]),
            "timeframes": spec.get("timeframes", ["H4", "H1"]),
            "signals": spec.get("signals", []),
            "risk_management": spec.get("risk_management", {}),
            "validation_timestamp": datetime.now().isoformat()
        }
        
        # Validate risk management
        validated["risk_management"] = self._validate_risk_management(
            validated["risk_management"]
        )
        
        # Validate signals
        validated["signals"] = self._validate_signals(validated["signals"])
        
        return validated

    def _validate_risk_management(self, risk_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and set defaults for risk management."""
        
        return {
            "position_size": risk_config.get("position_size", 1),
            "max_risk_percent": risk_config.get("max_risk_percent", 2.0),
            "target_rr": risk_config.get("target_rr", 2.0),
            "stop_loss_type": risk_config.get("stop_loss_type", "adaptive"),
            "take_profit_type": risk_config.get("take_profit_type", "multiple")
        }

    def _validate_signals(self, signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate signal configurations."""
        
        validated_signals = []
        
        for signal in signals:
            validated_signal = {
                "name": signal.get("name", "unnamed_signal"),
                "description": signal.get("description", ""),
                "jgtml_components": signal.get("jgtml_components", {}),
                "validation": signal.get("validation", {}),
                "priority": signal.get("priority", 1.0)
            }
            validated_signals.append(validated_signal)
        
        return validated_signals

    def signals(self, spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Return validated signal definitions from a loaded spec."""
        return spec.get("signals", [])

    def create_from_observation(self, observation: str, 
                              instruments: List[str] = None,
                              timeframes: List[str] = None) -> Dict[str, Any]:
        """Create intent specification from natural language observation."""
        
        return self.templates.observation_to_spec(observation, instruments, timeframes)

    def translate_to_scan_params(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Translate intent specification to FDB scanner parameters."""
        
        return {
            "instruments": spec.get("instruments", ["EUR/USD"]),
            "timeframes": spec.get("timeframes", ["H4", "H1"]),
            "strategy_context": spec.get("strategy_intent", ""),
            "signal_requirements": spec.get("signals", []),
            "risk_parameters": spec.get("risk_management", {}),
            "demo": True  # Default to demo mode
        }


class IntentTemplateLibrary:
    """Library of intent specification templates and conversion utilities."""
    
    def observation_to_spec(self, observation: str, 
                           instruments: List[str] = None,
                           timeframes: List[str] = None) -> Dict[str, Any]:
        """Convert natural language observation to intent specification."""
        
        observation_lower = observation.lower()
        
        # Base specification
        spec = {
            "strategy_intent": f"Analysis based on observation: {observation[:100]}...",
            "instruments": instruments or ["EUR/USD"],
            "timeframes": timeframes or ["H4", "H1", "m15"],
            "signals": [],
            "risk_management": {
                "position_size": 1,
                "max_risk_percent": 2.0,
                "target_rr": 2.0
            },
            "source_observation": observation
        }
        
        # Detect signal types from observation
        signals = []
        
        if any(word in observation_lower for word in ["breakout", "break"]):
            signals.append({
                "name": "breakout_signal",
                "description": "Breakout detection based on observation",
                "jgtml_components": {
                    "fractal_analysis": "jgtpy.fractal_detection",
                    "momentum": "jgtpy.ao_acceleration"
                }
            })
        
        if any(word in observation_lower for word in ["alligator", "gator", "mouth"]):
            signals.append({
                "name": "alligator_signal", 
                "description": "Alligator-based signal from observation",
                "jgtml_components": {
                    "alligator_state": "TideAlligatorAnalysis.mouth_opening"
                }
            })
        
        if any(word in observation_lower for word in ["confluence", "align"]):
            signals.append({
                "name": "confluence_signal",
                "description": "Multi-indicator confluence",
                "jgtml_components": {
                    "fractal_analysis": "jgtpy.fractal_detection",
                    "alligator_state": "TideAlligatorAnalysis.mouth_opening",
                    "momentum": "jgtpy.ao_acceleration"
                }
            })
        
        # Default signal if none detected
        if not signals:
            signals.append({
                "name": "general_signal",
                "description": "General signal detection",
                "jgtml_components": {
                    "fractal_analysis": "jgtpy.fractal_detection"
                }
            })
        
        spec["signals"] = signals
        
        # Detect bias
        if any(word in observation_lower for word in ["bearish", "sell", "down", "short"]):
            spec["bias"] = "bearish"
        elif any(word in observation_lower for word in ["bullish", "buy", "up", "long"]):
            spec["bias"] = "bullish"
        
        # Detect timeframe preferences
        if "daily" in observation_lower or "d1" in observation_lower:
            if "D1" not in spec["timeframes"]:
                spec["timeframes"].insert(0, "D1")
        
        return spec
    
    def get_template(self, template_name: str) -> Dict[str, Any]:
        """Get predefined intent specification template."""
        
        templates = {
            "confluence_strategy": {
                "strategy_intent": "Multi-timeframe Alligator-Fractal confluence",
                "instruments": ["EUR/USD", "GBP/USD"],
                "timeframes": ["H4", "H1", "m15"],
                "signals": [{
                    "name": "five_dimensions_confluence",
                    "description": "Full five dimensions Bill Williams confluence",
                    "jgtml_components": {
                        "fractal_analysis": "jgtpy.fractal_detection",
                        "alligator_state": "TideAlligatorAnalysis.mouth_opening",
                        "momentum": "jgtpy.ao_acceleration",
                        "volume_analysis": "jgtpy.mfi_analysis"
                    }
                }],
                "risk_management": {
                    "position_size": 1,
                    "max_risk_percent": 2.0,
                    "target_rr": 2.0
                }
            },
            
            "trend_following": {
                "strategy_intent": "Trend following with Alligator confirmation",
                "instruments": ["EUR/USD"],
                "timeframes": ["H4", "H1"],
                "signals": [{
                    "name": "trend_confirmation",
                    "description": "Trend following with multiple confirmations",
                    "jgtml_components": {
                        "alligator_state": "TideAlligatorAnalysis.mouth_opening",
                        "momentum": "jgtpy.ao_acceleration"
                    }
                }],
                "risk_management": {
                    "position_size": 1,
                    "max_risk_percent": 1.5,
                    "target_rr": 3.0
                }
            }
        }
        
        return templates.get(template_name, {})


# CLI interface for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Intent Specification Parser")
    parser.add_argument("--spec_file", help="Path to .jgtml-spec file")
    parser.add_argument("--observation", help="Natural language observation")
    parser.add_argument("--template", help="Use predefined template")
    parser.add_argument("--validate", action="store_true", help="Validate specification")
    
    args = parser.parse_args()
    
    parser_instance = IntentSpecParser()
    
    if args.spec_file:
        spec = parser_instance.load(args.spec_file)
        print(f"✅ Loaded specification: {spec['strategy_intent']}")
        print(json.dumps(spec, indent=2))
    
    elif args.observation:
        spec = parser_instance.create_from_observation(args.observation)
        print(f"🔮 Generated specification from observation")
        print(json.dumps(spec, indent=2))
    
    elif args.template:
        spec = parser_instance.templates.get_template(args.template)
        if spec:
            print(f"📋 Template: {args.template}")
            print(json.dumps(spec, indent=2))
        else:
            print(f"❌ Template '{args.template}' not found")
    
    else:
        print("🌸 Intent Specification Parser")
        print("Available templates:")
        templates = ["confluence_strategy", "trend_following"]
        for template in templates:
            print(f"  - {template}")
