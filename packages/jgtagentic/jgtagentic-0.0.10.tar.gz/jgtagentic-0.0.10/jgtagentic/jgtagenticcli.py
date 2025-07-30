# This file provides the main CLI interface for the jgtagentic platform

import argparse
import sys
import os
import json

# Ensure package imports resolve when executed directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from jgtagentic.fdbscan_agent import FDBScanAgent
from jgtagentic.intent_spec import IntentSpecParser

# Enhanced imports
try:
    from jgtagentic.observation_capture import ObservationCapture
    from jgtagentic.enhanced_fdb_scanner import EnhancedFDBScanner
    _ENHANCED_AVAILABLE = True
except ImportError:
    _ENHANCED_AVAILABLE = False

# 🧠🌸🔮 CLI Ritual: The Enhanced Spiral Gateway

def main():
    parser = argparse.ArgumentParser(
        description="""🌸 jgtagentic – Enhanced Intent-Driven Trading Platform

WHAT THIS PLATFORM GENERATES:
1. 🔮 Natural Language Analysis - Convert market observations to trading intent
2. 📊 Enhanced Signal Analysis - Intent-aware signal detection and quality scoring  
3. 🎯 Strategic Recommendations - Intelligent entry/exit automation
4. 📋 Intent Specifications - Structured trading specifications from observations
5. 🔄 Integrated Workflows - Seamless observation → intent → signal → action

KEY ENHANCED FEATURES:
- Natural language market observation capture
- Intent-driven signal scanning with context awareness  
- Quality-scored signal analysis with strategic recommendations
- Streamlined workflow from human insight to automated execution
- Integration with existing JGT platform components

USAGE PATTERNS:
- Observe market → Generate intent → Scan for signals → Execute strategy
- Create intent specifications from natural language analysis
- Enhanced FDB scanning with contextual signal validation
- Strategic automation with intelligent risk management

Each command provides detailed output and actionable next steps.""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Enhanced Orchestrator
    orchestrator_parser = subparsers.add_parser(
        "orchestrate", 
        help="Run the enhanced agentic orchestrator (observation → automation)",
        description="""
The enhanced orchestrator provides a complete workflow:
- Natural language observation processing
- Intent specification generation
- Context-aware signal scanning  
- Strategic recommendations and automation
- Performance tracking and learning

Example:
  jgtagentic orchestrate --observation "EUR/USD showing bullish breakout above 1.0850 resistance"
        """
    )
    orchestrator_parser.add_argument("--observation", help="Natural language market observation")
    orchestrator_parser.add_argument("--signal_json", help="Path to signal JSON file", default=None)
    orchestrator_parser.add_argument("--intent_spec", help="Path to intent specification file")
    orchestrator_parser.add_argument("--entry_script_dir", help="Directory for entry scripts", default=None)
    orchestrator_parser.add_argument("--log", help="Path to session log file", default=None)
    orchestrator_parser.add_argument("--dry_run", action="store_true", help="Dry run (no file writes)")

    # Enhanced FDBScan
    fdbscan_parser = subparsers.add_parser(
        "fdbscan", 
        help="Enhanced FDBScan with intent awareness",
        description="""
Enhanced FDBScan provides:
- Traditional timeframe scanning with optional intent context
- Natural language observation-based scanning
- Intent specification file processing
- Quality-scored signal analysis with strategic context

Examples:
  jgtagentic fdbscan --timeframe H4 --with-intent
  jgtagentic fdbscan --observe "Looking for alligator mouth opening on EUR/USD"  
  jgtagentic fdbscan --spec strategy.jgtml-spec
        """
    )
    fdbscan_parser.add_argument("--timeframe", help="Timeframe to scan (e.g. m5, m15, H1, H4)")
    fdbscan_parser.add_argument("--instrument", help="Instrument to scan")
    fdbscan_parser.add_argument("--observe", help="Natural language market observation")
    fdbscan_parser.add_argument("--spec", help="Path to intent specification file")
    fdbscan_parser.add_argument("--with-intent", action="store_true", help="Use enhanced intent-aware scanning")
    fdbscan_parser.add_argument("--all", action="store_true", help="Run full sequence (H4→H1→m15→m5)")

    # Market Observation Interface
    observe_parser = subparsers.add_parser(
        "observe",
        help="Capture and process market observations",
        description="""
The observation interface converts natural language market analysis into:
- Structured intent specifications
- Validated signal requirements  
- Strategic scanning parameters
- Quality assessment and recommendations

Example:
  jgtagentic observe "SPX500 breaking above 4200 resistance with strong volume"
        """
    )
    observe_parser.add_argument("observation", help="Natural language market observation")
    observe_parser.add_argument("--instruments", nargs="*", help="Target instruments")
    observe_parser.add_argument("--timeframes", nargs="*", help="Target timeframes")
    observe_parser.add_argument("--confidence", type=float, help="Confidence level (0-1)")
    observe_parser.add_argument("--scan", action="store_true", help="Automatically scan after processing")

    # Intent Specification Interface  
    spec_parser_cmd = subparsers.add_parser(
        "spec", 
        help="Work with trading intent specifications",
        description="""
The spec interface provides:
- Intent specification parsing and validation
- Template-based specification generation
- Natural language to specification conversion
- Specification quality assessment

Examples:
  jgtagentic spec validate strategy.jgtml-spec
  jgtagentic spec template confluence_strategy
  jgtagentic spec create "Trend following with momentum confirmation"
        """
    )
    spec_subparsers = spec_parser_cmd.add_subparsers(dest="spec_action", required=True)
    
    # Spec validate
    validate_parser = spec_subparsers.add_parser("validate", help="Validate intent specification")
    validate_parser.add_argument("spec_file", help="Path to intent specification file")
    
    # Spec template
    template_parser = spec_subparsers.add_parser("template", help="Generate from template")
    template_parser.add_argument("template_name", help="Template name")
    template_parser.add_argument("--output", help="Output file path")
    
    # Spec create
    create_parser = spec_subparsers.add_parser("create", help="Create spec from observation")
    create_parser.add_argument("observation", help="Market observation or strategy description")
    create_parser.add_argument("--output", help="Output file path")

    # Enhanced Campaign Management
    campaign_parser = subparsers.add_parser(
        "campaign",
        help="Intelligent campaign and session management",  
        description="""
Enhanced campaign management provides:
- Automated session creation from intent specifications
- Intelligent entry/exit strategy automation
- Performance tracking and learning
- Risk-aware position management

Example:
  jgtagentic campaign create --from-observation "EUR/USD bullish breakout setup"
        """
    )
    campaign_subparsers = campaign_parser.add_subparsers(dest="campaign_action", required=True)
    
    create_campaign_parser = campaign_subparsers.add_parser("create", help="Create new campaign")
    create_campaign_parser.add_argument("--from-observation", help="Create from market observation")
    create_campaign_parser.add_argument("--from-spec", help="Create from intent specification file")
    create_campaign_parser.add_argument("--demo", action="store_true", help="Demo mode")

    args = parser.parse_args()

    if args.command == "orchestrate":
        if _ENHANCED_AVAILABLE and args.observation:
            # Enhanced observation-based orchestration
            print(f"\n🔮 Processing market observation: {args.observation}")
            
            capture = ObservationCapture()
            observation_result = capture.capture_observation(args.observation)
            
            print(f"✨ Analysis complete - Quality Score: {observation_result['quality_score']:.2f}")
            print(f"🎯 Detected Sentiment: {observation_result['observation']['sentiment']}")
            print(f"📊 Signal Type: {observation_result['observation']['signal_type']}")
            
            # Auto-scan if quality is good
            if observation_result['quality_score'] >= 0.6:
                print("\n🔍 Quality threshold met - initiating enhanced scan...")
                
                agent = FDBScanAgent()
                scan_result = agent.scan_with_observation(args.observation)
                
                if scan_result.get('success'):
                    recommendations = scan_result.get('scan_results', {}).get('recommendations', {})
                    action = recommendations.get('action', 'wait')
                    
                    print(f"\n⚡ Scan complete - Recommended action: {action}")
                    print(f"📋 Reason: {recommendations.get('reason', 'N/A')}")
                    
                    if action == "execute":
                        print("\n🎯 Next Steps:")
                        for step in recommendations.get('next_steps', []):
                            print(f"  - {step}")
                else:
                    print(f"\n⚠️ Scan failed: {scan_result.get('error', 'Unknown error')}")
            else:
                print(f"\n📝 Recommendations:")
                for rec in observation_result.get('recommendations', []):
                    print(f"  - {rec}")
                    
        elif args.intent_spec:
            # Traditional spec-based orchestration
            print(f"\n📋 Processing intent specification: {args.intent_spec}")
            
            agent = FDBScanAgent()
            result = agent.scan_with_intent_file(args.intent_spec)
            
            if result.get('success'):
                print(f"✨ Specification processed successfully")
                print(json.dumps(result, indent=2))
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
        else:
            print("\n⚠️ Please provide --observation or --intent_spec for orchestration")
            sys.exit(1)

    elif args.command == "fdbscan":
        agent = FDBScanAgent()
        
        if args.observe:
            print(f"\n🔮 Observation-based scanning: {args.observe}")
            result = agent.scan_with_observation(args.observe)
            
        elif args.spec:
            print(f"\n📋 Specification-based scanning: {args.spec}")
            result = agent.scan_with_intent_file(args.spec)
            
        elif args.all:
            print(f"\n🔄 Full sequence scanning{'with intent context' if args.with_intent else ''}")
            result = agent.scan_all(with_intent=args.with_intent)
            
        elif args.timeframe:
            print(f"\n🎯 Timeframe scanning: {args.timeframe}")
            result = agent.scan_timeframe(args.timeframe, args.instrument, args.with_intent)
            
        else:
            print("\n⚠️ Please specify scanning method: --observe, --spec, --timeframe, or --all")
            sys.exit(1)
        
        # Output results
        if isinstance(result, dict):
            if result.get('success'):
                print("✨ Scan completed successfully")
                if 'recommendations' in result:
                    recs = result['recommendations']
                    print(f"⚡ Recommended action: {recs.get('action', 'N/A')}")
                    print(f"📋 Reason: {recs.get('reason', 'N/A')}")
            else:
                print(f"❌ Scan failed: {result.get('error', 'Unknown error')}")
            
            print(f"\n📊 Full Results:")
            print(json.dumps(result, indent=2))

    elif args.command == "observe":
        if not _ENHANCED_AVAILABLE:
            print("\n❌ Enhanced observation features not available")
            sys.exit(1)
            
        print(f"\n🔍 Processing observation: {args.observation}")
        
        capture = ObservationCapture()
        result = capture.capture_observation(args.observation)
        
        print(f"✨ Analysis complete")
        print(f"🎯 Quality Score: {result['quality_score']:.2f}")
        print(f"📊 Sentiment: {result['observation']['sentiment']}")
        print(f"🔮 Signal Type: {result['observation']['signal_type']}")
        
        print(f"\n📋 Generated Intent Specification:")
        print(json.dumps(result['intent_specification'], indent=2))
        
        print(f"\n💡 Recommendations:")
        for rec in result.get('recommendations', []):
            print(f"  - {rec}")
        
        if args.scan and result['quality_score'] >= 0.6:
            print(f"\n🔄 Auto-scanning based on quality threshold...")
            agent = FDBScanAgent()
            scan_result = agent.scan_with_observation(args.observation, args.instruments, args.timeframes)
            print(json.dumps(scan_result, indent=2))

    elif args.command == "spec":
        parser_instance = IntentSpecParser()
        
        if args.spec_action == "validate":
            try:
                spec = parser_instance.load(args.spec_file)
                print(f"✅ Specification valid: {spec['strategy_intent']}")
                print(json.dumps(spec, indent=2))
            except Exception as e:
                print(f"❌ Validation failed: {e}")
                
        elif args.spec_action == "template":
            spec = parser_instance.templates.get_template(args.template_name)
            if spec:
                print(f"📋 Template: {args.template_name}")
                if args.output:
                    import yaml
                    with open(args.output, 'w') as f:
                        yaml.dump(spec, f, default_flow_style=False)
                    print(f"💾 Saved to: {args.output}")
                else:
                    print(json.dumps(spec, indent=2))
            else:
                print(f"❌ Template '{args.template_name}' not found")
                print("Available templates: confluence_strategy, trend_following")
                
        elif args.spec_action == "create":
            if _ENHANCED_AVAILABLE:
                spec = parser_instance.create_from_observation(args.observation)
                print(f"🔮 Generated specification from observation")
                if args.output:
                    import yaml
                    with open(args.output, 'w') as f:
                        yaml.dump(spec, f, default_flow_style=False)
                    print(f"💾 Saved to: {args.output}")
                else:
                    print(json.dumps(spec, indent=2))
            else:
                print("❌ Enhanced spec creation not available")

    elif args.command == "campaign":
        if args.campaign_action == "create":
            print("🚀 Campaign creation is in development")
            if args.from_observation:
                print(f"📝 Would create campaign from: {args.from_observation}")
            elif args.from_spec:
                print(f"📋 Would create campaign from spec: {args.from_spec}")
            print("🔄 This will integrate with enhanced session management")
            
    else:
        print("❌ Unknown command")
        sys.exit(1)

if __name__ == "__main__":
    main()
