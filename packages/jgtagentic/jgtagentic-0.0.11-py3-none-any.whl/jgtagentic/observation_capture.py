"""
🌸🧠 Observation Capture — Market Analysis to Intent Bridge

Purpose: Capture natural language market observations and translate them into 
executable trading intent specifications. This is the bridge between human 
market insight and systematic automation.

Architecture:
Market Observation → Linguistic Analysis → Intent Specification → Scanner Parameters
"""

import logging
import json
import re
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass

from .intent_spec import IntentSpecParser


@dataclass
class MarketObservation:
    """Structured market observation data."""
    text: str
    timestamp: str
    instruments: List[str]
    timeframes: List[str]
    confidence: float
    sentiment: str  # bullish, bearish, neutral
    signal_type: str  # breakout, confluence, trend, reversal
    
    
class ObservationCapture:
    """
    Convert natural language market observations into actionable intent specifications.
    
    This interface:
    1. Analyzes natural language market observations
    2. Extracts trading intent and context
    3. Generates structured intent specifications
    4. Validates and enhances specifications
    5. Provides feedback on observation quality
    """
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger("ObservationCapture")
        self.intent_parser = IntentSpecParser()
        self.observation_history = []
        
    def capture_observation(self, observation_text: str) -> Dict[str, Any]:
        """Capture and process a market observation."""
        
        # Analyze the observation
        analysis = self._analyze_observation(observation_text)
        
        result = {
            "observation": {
                "text": observation_text,
                "timestamp": datetime.now().isoformat(),
                "instruments": analysis["instruments"],
                "timeframes": analysis["timeframes"],
                "confidence": analysis["confidence"],
                "sentiment": analysis["sentiment"],
                "signal_type": analysis["signal_type"]
            },
            "intent_specification": {
                "strategy_intent": f"Analysis: {observation_text[:50]}...",
                "instruments": analysis["instruments"],
                "timeframes": analysis["timeframes"],
                "signals": analysis["signals"],
                "bias": analysis["sentiment"]
            },
            "quality_score": analysis["confidence"],
            "recommendations": analysis["recommendations"],
            "success": True
        }
        
        return result
    
    def capture_session(self, observations: List[str],
                       session_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Capture multiple observations as a trading session.
        
        Args:
            observations: List of observation texts
            session_context: Additional session context
            
        Returns:
            Session analysis with consolidated intent
        """
        
        self.logger.info(f"🎯 Processing trading session with {len(observations)} observations")
        
        session_results = []
        consolidated_instruments = set()
        consolidated_timeframes = set()
        
        # Process each observation
        for i, obs_text in enumerate(observations):
            result = self.capture_observation(obs_text)
            session_results.append(result)
            
            # Consolidate instruments and timeframes
            consolidated_instruments.update(result["observation"]["instruments"])
            consolidated_timeframes.update(result["observation"]["timeframes"])
        
        # Generate consolidated intent
        consolidated_intent = self._consolidate_session_intent(
            session_results, 
            list(consolidated_instruments),
            list(consolidated_timeframes),
            session_context
        )
        
        return {
            "session_timestamp": datetime.now().isoformat(),
            "observations": session_results,
            "consolidated_instruments": list(consolidated_instruments),
            "consolidated_timeframes": list(consolidated_timeframes),
            "consolidated_intent": consolidated_intent,
            "session_quality": self._assess_session_quality(session_results),
            "trading_recommendations": self._generate_session_recommendations(consolidated_intent)
        }
    
    def _analyze_observation(self, text: str) -> Dict[str, Any]:
        """Analyze observation text and extract trading context."""
        
        text_lower = text.lower()
        
        # Extract instruments
        instruments = self._extract_instruments(text)
        
        # Extract timeframes  
        timeframes = self._extract_timeframes(text)
        
        # Analyze sentiment
        sentiment = self._analyze_sentiment(text_lower)
        
        # Detect signal type
        signal_type = self._detect_signal_type(text_lower)
        
        # Assess confidence
        confidence = self._assess_confidence(text_lower)
        
        # Generate signals
        signals = self._generate_signals(signal_type, sentiment)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(confidence, sentiment, signal_type)
        
        return {
            "instruments": instruments,
            "timeframes": timeframes,
            "sentiment": sentiment,
            "signal_type": signal_type,
            "confidence": confidence,
            "signals": signals,
            "recommendations": recommendations
        }
    
    def _extract_instruments(self, text: str) -> List[str]:
        """Extract instrument symbols from observation text."""
        
        text_upper = text.upper()
        instruments = []
        
        if 'EUR' in text_upper and 'USD' in text_upper:
            instruments.append('EUR/USD')
        elif 'GBP' in text_upper and 'USD' in text_upper:
            instruments.append('GBP/USD')
        elif 'SPX' in text_upper or 'SP500' in text_upper:
            instruments.append('SPX500')
        elif 'XAU' in text_upper or 'GOLD' in text_upper:
            instruments.append('XAU/USD')
        
        return instruments if instruments else ["EUR/USD"]
    
    def _extract_timeframes(self, text: str) -> List[str]:
        """Extract timeframes from observation text."""
        
        text_lower = text.lower()
        timeframes = []
        
        if any(word in text_lower for word in ['hour', 'h1', 'h4']):
            timeframes.extend(['H4', 'H1'])
        if any(word in text_lower for word in ['daily', 'day', 'd1']):
            timeframes.append('D1')
        if any(word in text_lower for word in ['15', 'fifteen', 'm15']):
            timeframes.append('m15')
        
        return timeframes if timeframes else ["H4", "H1"]
    
    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment from observation text."""
        
        bullish_words = ['bullish', 'buy', 'long', 'up', 'rising', 'breakout', 'above', 'strong']
        bearish_words = ['bearish', 'sell', 'short', 'down', 'falling', 'breakdown', 'below', 'weak']
        
        bullish_count = sum(1 for word in bullish_words if word in text)
        bearish_count = sum(1 for word in bearish_words if word in text)
        
        if bullish_count > bearish_count:
            return "bullish"
        elif bearish_count > bullish_count:
            return "bearish"
        else:
            return "neutral"
    
    def _detect_signal_type(self, text: str) -> str:
        """Detect the type of trading signal from observation."""
        
        if any(word in text for word in ["breakout", "break", "above", "below"]):
            return "breakout"
        elif any(word in text for word in ["alligator", "gator", "mouth"]):
            return "alligator"
        elif any(word in text for word in ["momentum", "strong", "acceleration"]):
            return "momentum"
        elif any(word in text for word in ["confluence", "align", "multiple"]):
            return "confluence"
        else:
            return "general"
    
    def _assess_confidence(self, text: str) -> float:
        """Assess confidence based on linguistic cues."""
        
        high_confidence_words = ['clear', 'strong', 'definite', 'obvious']
        low_confidence_words = ['maybe', 'might', 'could', 'possibly']
        
        high_count = sum(1 for word in high_confidence_words if word in text)
        low_count = sum(1 for word in low_confidence_words if word in text)
        
        base_confidence = 0.7
        confidence = base_confidence + (high_count * 0.1) - (low_count * 0.1)
        
        return max(0.1, min(1.0, confidence))
    
    def _generate_signals(self, signal_type: str, sentiment: str) -> List[Dict[str, Any]]:
        """Generate signals based on detected type and sentiment."""
        
        signals = []
        
        if signal_type == "breakout":
            signals.append({
                "name": "breakout_signal",
                "description": f"{sentiment.title()} breakout detection",
                "jgtml_components": {
                    "fractal_analysis": "jgtpy.fractal_detection",
                    "momentum": "jgtpy.ao_acceleration"
                }
            })
        elif signal_type == "momentum":
            signals.append({
                "name": "momentum_signal", 
                "description": f"{sentiment.title()} momentum signal",
                "jgtml_components": {
                    "momentum": "jgtpy.ao_acceleration",
                    "alligator_state": "TideAlligatorAnalysis.mouth_opening"
                }
            })
        else:
            signals.append({
                "name": "general_signal",
                "description": f"{sentiment.title()} signal detection",
                "jgtml_components": {
                    "fractal_analysis": "jgtpy.fractal_detection"
                }
            })
        
        return signals
    
    def _generate_recommendations(self, confidence: float, sentiment: str, signal_type: str) -> List[str]:
        """Generate recommendations based on analysis."""
        
        recommendations = []
        
        if confidence >= 0.8:
            recommendations.append("High confidence - proceed with scanning")
        elif confidence >= 0.6:
            recommendations.append("Moderate confidence - consider additional validation")
        else:
            recommendations.append("Low confidence - gather more information")
        
        if sentiment != "neutral":
            recommendations.append(f"Clear {sentiment} bias detected")
        
        if signal_type != "general":
            recommendations.append(f"Specific {signal_type} pattern identified")
        
        return recommendations
    
    def _consolidate_session_intent(self, session_results: List[Dict[str, Any]],
                                  instruments: List[str],
                                  timeframes: List[str],
                                  session_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Consolidate multiple observations into unified intent."""
        
        # Extract all signals
        all_signals = []
        sentiment_counts = {"bullish": 0, "bearish": 0, "neutral": 0}
        
        for result in session_results:
            spec = result["intent_specification"]
            all_signals.extend(spec.get("signals", []))
            sentiment = result["observation"]["sentiment"]
            sentiment_counts[sentiment] += 1
        
        # Determine consolidated sentiment
        dominant_sentiment = max(sentiment_counts, key=sentiment_counts.get)
        
        # Create consolidated intent
        consolidated = {
            "strategy_intent": "Multi-observation trading session analysis",
            "instruments": instruments,
            "timeframes": timeframes,
            "signals": all_signals,
            "bias": dominant_sentiment,
            "observation_count": len(session_results),
            "session_context": session_context or {},
            "risk_management": {
                "position_size": 1,
                "max_risk_percent": 2.0,
                "target_rr": 2.0
            }
        }
        
        return consolidated
    
    def _assess_session_quality(self, session_results: List[Dict[str, Any]]) -> float:
        """Assess overall quality of trading session observations."""
        
        if not session_results:
            return 0.0
        
        total_quality = sum(result["quality_score"] for result in session_results)
        average_quality = total_quality / len(session_results)
        
        # Bonus for consistency
        sentiments = [result["observation"]["sentiment"] for result in session_results]
        consistency_bonus = 0.1 if len(set(sentiments)) <= 2 else 0.0
        
        return min(1.0, average_quality + consistency_bonus)
    
    def _generate_session_recommendations(self, consolidated_intent: Dict[str, Any]) -> List[str]:
        """Generate recommendations for the trading session."""
        
        recommendations = [
            "Review consolidated signals for confluence",
            "Validate sentiment consistency across observations",
            "Consider risk management for multiple signals"
        ]
        
        signal_count = len(consolidated_intent.get("signals", []))
        if signal_count > 3:
            recommendations.append("High signal count - prioritize by quality")
        
        return recommendations


# CLI interface for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Market Observation Capture")
    parser.add_argument("--observation", help="Market observation text", required=True)
    parser.add_argument("--instruments", nargs="*", help="Target instruments")
    parser.add_argument("--timeframes", nargs="*", help="Target timeframes")
    parser.add_argument("--confidence", type=float, help="Confidence level (0-1)")
    
    args = parser.parse_args()
    
    capture = ObservationCapture()
    result = capture.capture_observation(
        args.observation,
        args.instruments,
        args.timeframes,
        args.confidence
    )
    
    print(f"🔮 Observation Analysis Complete")
    print(f"Quality Score: {result['quality_score']:.2f}")
    print(f"Sentiment: {result['observation']['sentiment']}")
    print(f"Signal Type: {result['observation']['signal_type']}")
    print("\n📋 Intent Specification:")
    print(json.dumps(result['intent_specification'], indent=2)) 