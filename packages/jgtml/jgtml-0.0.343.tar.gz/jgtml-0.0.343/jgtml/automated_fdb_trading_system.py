#!/usr/bin/env python3
"""
Automated FDB Trading System - Production Ready
================================================================

CRITICAL DOCUMENTATION:
- Last CSV row = INCOMPLETE bar (current forming period)
- Second-to-last CSV row = COMPLETED bar (FDB signal analysis target)  
- FDB signals MUST be analyzed on COMPLETED bars only

This system:
1. Analyzes higher timeframe bias (Monthly, Weekly, Daily)
2. Scans trading timeframes (m15, H1, H4) for FDB signals on COMPLETED bars
3. Automatically executes market entries when quality scores are high
4. Creates trading campaigns for signal execution
"""

import os
import sys
import json
import subprocess
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import argparse

# Add jgtml to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from .enhanced_fdb_scanner_with_illusion_detection import EnhancedFDBScanner
    from .SOHelper import get_last_two_bars, get_bar_at_index
    from .SignalOrderingHelper import create_fdb_entry_order
    from jgtutils import jgtcommon
    from jgtutils.jgtconstants import FDB, ZONE_SIGNAL, MFI_FADE, MFI_SQUAT
    import tlid
except ImportError as e:
    try:
        # Fallback to absolute imports
        from jgtml.enhanced_fdb_scanner_with_illusion_detection import EnhancedFDBScanner
        from jgtml.SOHelper import get_last_two_bars, get_bar_at_index
        from jgtml.SignalOrderingHelper import create_fdb_entry_order
        from jgtutils import jgtcommon
        from jgtutils.jgtconstants import FDB, ZONE_SIGNAL, MFI_FADE, MFI_SQUAT
        import tlid
    except ImportError as e2:
        print(f"Import error: {e2}")
        print("Some modules may not be available")

class HigherTimeframeBiasAnalyzer:
    """Analyzes higher timeframe bias for trading decisions"""
    
    def __init__(self):
        self.htf_timeframes = ["M1", "W1", "D1"]  # Higher timeframes for bias
        try:
            self.scanner = EnhancedFDBScanner()
        except:
            self.scanner = None
            print("⚠️  Scanner not available - using simplified analysis")
    
    def get_htf_bias(self, instrument: str) -> Dict:
        """Get higher timeframe bias for instrument"""
        print(f"\n📊 ANALYZING HIGHER TIMEFRAME BIAS - {instrument}")
        print("=" * 60)
        
        bias_analysis = {
            "instrument": instrument,
            "timeframes": {},
            "overall_bias": "NEUTRAL",
            "confidence": 0.0,
            "analysis_time": datetime.now().isoformat()
        }
        
        if not self.scanner:
            print("⚠️  Scanner not available - returning neutral bias")
            return bias_analysis
        
        bias_signals = []
        
        for tf in self.htf_timeframes:
            try:
                print(f"  📈 Analyzing {tf}...")
                
                # Get data for timeframe
                data = self.scanner.get_cached_data(instrument, tf)
                if not data:
                    print(f"    ⚠️  No data available for {tf}")
                    continue
                
                # Get completed bar analysis - CRITICAL: Use signal_bar (completed)
                df = pd.DataFrame(data)
                signal_bar, current_bar = get_last_two_bars(df)
                
                # Analyze signals on COMPLETED bar (signal_bar) ONLY
                zone_signal = signal_bar.get(ZONE_SIGNAL, 0)
                fdb_signal = signal_bar.get(FDB, 0)
                mfi_fade = signal_bar.get(MFI_FADE, 0)
                
                bias_direction = "BULLISH" if zone_signal > 0 else "BEARISH" if zone_signal < 0 else "NEUTRAL"
                fdb_direction = "BUY" if fdb_signal > 0 else "SELL" if fdb_signal < 0 else "NONE"
                
                tf_analysis = {
                    "zone_signal": zone_signal,
                    "fdb_signal": fdb_signal,
                    "mfi_fade": mfi_fade,
                    "bias_direction": bias_direction,
                    "fdb_direction": fdb_direction,
                    "signal_timestamp": str(signal_bar.name) if hasattr(signal_bar, 'name') else ""
                }
                
                bias_analysis["timeframes"][tf] = tf_analysis
                
                # Weight bias signals (Monthly > Weekly > Daily)
                weight = 3 if tf == "M1" else 2 if tf == "W1" else 1
                if zone_signal != 0:
                    bias_signals.extend([bias_direction] * weight)
                
                print(f"    ✅ {tf}: {bias_direction} bias, FDB: {fdb_direction}")
                
            except Exception as e:
                print(f"    ❌ Error analyzing {tf}: {e}")
                continue
        
        # Calculate overall bias
        if bias_signals:
            bullish_count = bias_signals.count("BULLISH")
            bearish_count = bias_signals.count("BEARISH")
            total_signals = len(bias_signals)
            
            if bullish_count > bearish_count:
                bias_analysis["overall_bias"] = "BULLISH"
                bias_analysis["confidence"] = bullish_count / total_signals
            elif bearish_count > bullish_count:
                bias_analysis["overall_bias"] = "BEARISH" 
                bias_analysis["confidence"] = bearish_count / total_signals
            else:
                bias_analysis["overall_bias"] = "NEUTRAL"
                bias_analysis["confidence"] = 0.5
        
        print(f"\n🎯 OVERALL BIAS: {bias_analysis['overall_bias']} (Confidence: {bias_analysis['confidence']:.2f})")
        
        return bias_analysis

class AutomatedFDBTradingSystem:
    """Complete automated FDB trading system with higher timeframe bias"""
    
    def __init__(self, demo_mode=True):
        self.demo_mode = demo_mode
        try:
            self.scanner = EnhancedFDBScanner()
        except:
            self.scanner = None
            print("⚠️  Enhanced scanner not available")
            
        self.htf_analyzer = HigherTimeframeBiasAnalyzer()
        self.trading_timeframes = ["H4", "H1", "m15"]  # Entry timeframes
        self.quality_threshold = 8.0  # Minimum quality score for automated entry
        self.campaigns_dir = "campaigns"
        os.makedirs(self.campaigns_dir, exist_ok=True)
    
    def analyze_instrument_for_trading(self, instrument: str) -> Dict:
        """Complete analysis of instrument for trading opportunities"""
        print(f"\n🚀 AUTOMATED FDB TRADING ANALYSIS - {instrument}")
        print("=" * 80)
        
        analysis_result = {
            "instrument": instrument,
            "htf_bias": None,
            "trading_signals": [],
            "recommended_action": "NONE",
            "quality_score": 0.0,
            "automated_entry": False,
            "campaign_created": False,
            "analysis_time": datetime.now().isoformat()
        }
        
        try:
            # Step 1: Get higher timeframe bias
            htf_bias = self.htf_analyzer.get_htf_bias(instrument)
            analysis_result["htf_bias"] = htf_bias
            
            # Step 2: Scan trading timeframes for FDB signals
            trading_signals = []
            for tf in self.trading_timeframes:
                signal_analysis = self.analyze_trading_timeframe(instrument, tf, htf_bias)
                if signal_analysis:
                    trading_signals.append(signal_analysis)
            
            analysis_result["trading_signals"] = trading_signals
            
            # Step 3: Determine best trading opportunity
            best_signal = self.select_best_trading_signal(trading_signals, htf_bias)
            
            if best_signal:
                analysis_result["quality_score"] = best_signal.get("quality_score", 0.0)
                analysis_result["recommended_action"] = best_signal.get("direction", "NONE")
                
                # Step 4: Execute automated entry if quality is high enough
                if best_signal.get("quality_score", 0.0) >= self.quality_threshold:
                    campaign_result = self.create_trading_campaign(instrument, best_signal, htf_bias)
                    analysis_result["automated_entry"] = True
                    analysis_result["campaign_created"] = campaign_result.get("success", False)
                    analysis_result["campaign_id"] = campaign_result.get("campaign_id", "")
            
            return analysis_result
            
        except Exception as e:
            print(f"❌ Error in automated analysis for {instrument}: {e}")
            analysis_result["error"] = str(e)
            return analysis_result
    
    def analyze_trading_timeframe(self, instrument: str, timeframe: str, htf_bias: Dict) -> Optional[Dict]:
        """Analyze specific timeframe for FDB signals on COMPLETED bars"""
        try:
            print(f"  🔍 Scanning {timeframe} for FDB signals...")
            
            if not self.scanner:
                print(f"    ⚠️  Scanner not available for {timeframe}")
                return None
            
            # Get data
            data = self.scanner.get_cached_data(instrument, timeframe)
            if not data or len(data) < 2:
                print(f"    ⚠️  Insufficient data for {timeframe}")
                return None
            
            # CRITICAL: Analyze COMPLETED bar (signal_bar), not current forming bar
            df = pd.DataFrame(data)
            signal_bar, current_bar = get_last_two_bars(df)
            
            # Check for FDB signal on COMPLETED bar
            fdb_signal = signal_bar.get(FDB, 0)
            if fdb_signal == 0:
                print(f"    ℹ️  No FDB signal on completed bar in {timeframe}")
                return None
            
            # Validate signal using SignalOrderingHelper
            try:
                order_result, msg = create_fdb_entry_order(
                    instrument, signal_bar, current_bar,
                    lots=1, t=timeframe,
                    quiet=True, demo_flag=self.demo_mode
                )
                
                if not order_result:
                    print(f"    ❌ FDB signal validation failed in {timeframe}")
                    return None
                
            except Exception as e:
                print(f"    ❌ Signal validation error in {timeframe}: {e}")
                return None
            
            # Calculate quality score
            quality_score = self.calculate_signal_quality(signal_bar, htf_bias, timeframe)
            
            direction = "BUY" if fdb_signal > 0 else "SELL"
            signal_timestamp = str(signal_bar.name) if hasattr(signal_bar, 'name') else ""
            
            signal_analysis = {
                "timeframe": timeframe,
                "direction": direction,
                "fdb_signal": fdb_signal,
                "quality_score": quality_score,
                "signal_timestamp": signal_timestamp,
                "entry_rate": order_result.get("entry_rate", 0),
                "stop_rate": order_result.get("stop_rate", 0),
                "order_details": order_result
            }
            
            print(f"    ✅ {direction} signal found, Quality: {quality_score:.1f}/10")
            
            return signal_analysis
            
        except Exception as e:
            print(f"    ❌ Error analyzing {timeframe}: {e}")
            return None
    
    def calculate_signal_quality(self, signal_bar: pd.Series, htf_bias: Dict, timeframe: str) -> float:
        """Calculate signal quality score (0-10)"""
        base_score = 5.0  # Base score
        
        try:
            # HTF bias alignment (+3 points)
            fdb_signal = signal_bar.get(FDB, 0)
            signal_direction = "BULLISH" if fdb_signal > 0 else "BEARISH" if fdb_signal < 0 else "NEUTRAL"
            
            if htf_bias.get("overall_bias") == signal_direction:
                htf_alignment_bonus = 3.0 * htf_bias.get("confidence", 0)
                base_score += htf_alignment_bonus
            
            # Zone signal confirmation (+1.5 points)
            zone_signal = signal_bar.get(ZONE_SIGNAL, 0)
            if (fdb_signal > 0 and zone_signal > 0) or (fdb_signal < 0 and zone_signal < 0):
                base_score += 1.5
            
            # MFI fade confirmation (+0.5 points)
            mfi_fade = signal_bar.get(MFI_FADE, 0)
            if mfi_fade > 0:
                base_score += 0.5
            
            # Timeframe bonus (H4 > H1 > m15)
            tf_bonus = 1.0 if timeframe == "H4" else 0.5 if timeframe == "H1" else 0.0
            base_score += tf_bonus
            
        except Exception as e:
            print(f"Warning: Error calculating quality score: {e}")
        
        return min(10.0, max(0.0, base_score))
    
    def select_best_trading_signal(self, trading_signals: List[Dict], htf_bias: Dict) -> Optional[Dict]:
        """Select best trading signal based on quality and HTF bias"""
        if not trading_signals:
            return None
        
        # Filter signals that align with HTF bias
        aligned_signals = []
        for signal in trading_signals:
            signal_direction = "BULLISH" if signal["direction"] == "BUY" else "BEARISH"
            if htf_bias.get("overall_bias") in [signal_direction, "NEUTRAL"]:
                aligned_signals.append(signal)
        
        # Use all signals if none align (fallback)
        candidate_signals = aligned_signals if aligned_signals else trading_signals
        
        # Sort by quality score and select best
        best_signal = max(candidate_signals, key=lambda x: x.get("quality_score", 0))
        
        return best_signal
    
    def create_trading_campaign(self, instrument: str, signal: Dict, htf_bias: Dict) -> Dict:
        """Create and execute trading campaign"""
        try:
            # Use current timestamp for campaign ID
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            campaign_id = f"{instrument.replace('/', '-')}_{signal['timeframe']}_{timestamp}"
            
            print(f"\n🎯 CREATING TRADING CAMPAIGN: {campaign_id}")
            print("=" * 60)
            
            # Create campaign directory
            campaign_dir = os.path.join(self.campaigns_dir, campaign_id)
            os.makedirs(campaign_dir, exist_ok=True)
            
            # Generate trading order command
            order_details = signal["order_details"]
            direction_flag = "B" if signal["direction"] == "BUY" else "S"
            demo_flag = "--demo" if self.demo_mode else "--real"
            
            # Create fxaddorder command (from jgtfxcon)
            entry_cmd = f"fxaddorder -r {signal['entry_rate']} -x {signal['stop_rate']} -d {direction_flag} -n 1 -i {instrument} {demo_flag}"
            
            # Save campaign files
            campaign_data = {
                "campaign_id": campaign_id,
                "instrument": instrument,
                "signal": signal,
                "htf_bias": htf_bias,
                "entry_command": entry_cmd,
                "created_time": datetime.now().isoformat(),
                "status": "CREATED"
            }
            
            # Save campaign.json
            with open(os.path.join(campaign_dir, "campaign.json"), "w") as f:
                json.dump(campaign_data, f, indent=2)
            
            # Save entry.sh
            with open(os.path.join(campaign_dir, "entry.sh"), "w") as f:
                f.write("#!/bin/bash\n")
                f.write(f"# Automated FDB Trading Entry\n")
                f.write(f"# Campaign: {campaign_id}\n")
                f.write(f"# Created: {campaign_data['created_time']}\n\n")
                f.write(entry_cmd + "\n")
            
            # Make entry.sh executable
            os.chmod(os.path.join(campaign_dir, "entry.sh"), 0o755)
            
            # Create monitoring scripts
            self.create_campaign_scripts(campaign_dir, campaign_data)
            
            print(f"✅ Campaign created successfully: {campaign_id}")
            print(f"📁 Campaign directory: {campaign_dir}")
            print(f"🚀 Entry command: {entry_cmd}")
            
            return {"success": True, "campaign_id": campaign_id, "campaign_dir": campaign_dir}
            
        except Exception as e:
            print(f"❌ Error creating campaign: {e}")
            return {"success": False, "error": str(e)}
    
    def create_campaign_scripts(self, campaign_dir: str, campaign_data: Dict):
        """Create monitoring and management scripts for campaign"""
        
        try:
            # Extract order details for monitoring
            entry_rate = campaign_data["signal"]["entry_rate"]
            stop_rate = campaign_data["signal"]["stop_rate"]
            direction = campaign_data["signal"]["direction"]
            instrument = campaign_data["instrument"]
            demo_flag = "--demo" if self.demo_mode else "--real"
            
            # README.md with instructions
            readme_content = f"""# Trading Campaign: {campaign_data['campaign_id']}

## Campaign Details
- **Instrument**: {instrument}
- **Direction**: {direction}
- **Entry Rate**: {entry_rate}
- **Stop Rate**: {stop_rate}
- **Quality Score**: {campaign_data['signal'].get('quality_score', 'N/A')}
- **Created**: {campaign_data['created_time']}

## How to Execute
1. Run `./entry.sh` to place the order
2. Update ORDER_ID in scripts after execution
3. Use `./status.sh` to check order status
4. Use `./watch.sh` to monitor order
5. Use `./cancel.sh` to cancel if needed

## Higher Timeframe Bias
- **Overall Bias**: {campaign_data['htf_bias'].get('overall_bias', 'N/A')}
- **Confidence**: {campaign_data['htf_bias'].get('confidence', 'N/A')}
"""
            
            with open(os.path.join(campaign_dir, "README.md"), "w") as f:
                f.write(readme_content)
            
            # status.sh - Check order status (will need order ID after execution)
            status_script = f"""#!/bin/bash
# Status check script - Update ORDER_ID after order execution
ORDER_ID=""
if [ -n "$ORDER_ID" ]; then
    echo "Checking status for order $ORDER_ID"
    fxstatusorder -id $ORDER_ID -x {stop_rate} -d {direction[0]} {demo_flag}
else
    echo "❌ Order ID not set. Update ORDER_ID in this script after order execution."
    echo "Example: ORDER_ID=123456789"
fi
"""
            
            with open(os.path.join(campaign_dir, "status.sh"), "w") as f:
                f.write(status_script)
            
            # watch.sh - Monitor order
            watch_script = f"""#!/bin/bash  
# Watch order script - Update ORDER_ID after order execution
ORDER_ID=""
if [ -n "$ORDER_ID" ]; then
    echo "Watching order $ORDER_ID"
    fxwatchorder -id $ORDER_ID -x {stop_rate} -d {direction[0]} {demo_flag}
else
    echo "❌ Order ID not set. Update ORDER_ID in this script after order execution."
    echo "Example: ORDER_ID=123456789"
fi
"""
            
            with open(os.path.join(campaign_dir, "watch.sh"), "w") as f:
                f.write(watch_script)
            
            # cancel.sh - Cancel order
            cancel_script = f"""#!/bin/bash
# Cancel order script - Update ORDER_ID after order execution
ORDER_ID=""
if [ -n "$ORDER_ID" ]; then
    echo "Cancelling order $ORDER_ID"
    fxrmorder -id $ORDER_ID {demo_flag}
else
    echo "❌ Order ID not set. Update ORDER_ID in this script after order execution."
    echo "Example: ORDER_ID=123456789"
fi
"""
            
            with open(os.path.join(campaign_dir, "cancel.sh"), "w") as f:
                f.write(cancel_script)
            
            # Make scripts executable
            for script in ["status.sh", "watch.sh", "cancel.sh"]:
                os.chmod(os.path.join(campaign_dir, script), 0o755)
                
        except Exception as e:
            print(f"Warning: Error creating campaign scripts: {e}")

def parse_args():
    parser = argparse.ArgumentParser(
        description="Automated FDB Trading System - Production Ready",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan single instrument
  python automated_fdb_trading_system.py -i EUR-USD --demo

  # Scan multiple instruments  
  python automated_fdb_trading_system.py -i EUR-USD,GBP-USD,XAU-USD --demo

  # Production mode (real trading)
  python automated_fdb_trading_system.py -i EUR-USD --real
        """
    )
    
    parser.add_argument(
        "-i", "--instruments",
        type=str,
        required=True,
        help="Comma-separated list of instruments (e.g., EUR-USD,GBP-USD)"
    )
    
    parser.add_argument(
        "--demo",
        action="store_true",
        default=True,
        help="Use demo mode (default)"
    )
    
    parser.add_argument(
        "--real", 
        action="store_true",
        help="Use real trading mode (overrides --demo)"
    )
    
    parser.add_argument(
        "--quality-threshold",
        type=float,
        default=8.0,
        help="Minimum quality score for automated entry (default: 8.0)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Determine trading mode
    demo_mode = not args.real  # Real mode overrides demo
    mode_str = "DEMO" if demo_mode else "REAL"
    
    print("🤖 AUTOMATED FDB TRADING SYSTEM - PRODUCTION READY")
    print("=" * 80)
    print("📋 CRITICAL: FDB signals analyzed on COMPLETED bars only")
    print("📊 System includes higher timeframe bias analysis")
    print("🎯 Automated campaign creation for high-quality signals")
    print("=" * 80)
    print(f"Mode: {mode_str}")
    print(f"Quality Threshold: {args.quality_threshold}")
    print("=" * 80)
    
    # Create trading system
    trading_system = AutomatedFDBTradingSystem(demo_mode=demo_mode)
    trading_system.quality_threshold = args.quality_threshold
    
    # Parse instruments
    instruments = [i.strip() for i in args.instruments.split(",")]
    
    # Process each instrument
    all_results = {}
    campaigns_created = []
    
    for instrument in instruments:
        try:
            result = trading_system.analyze_instrument_for_trading(instrument)
            all_results[instrument] = result
            
            if result.get("campaign_created"):
                campaigns_created.append({
                    "instrument": instrument,
                    "campaign_id": result.get("campaign_id"),
                    "action": result.get("recommended_action"),
                    "quality": result.get("quality_score")
                })
                
        except Exception as e:
            print(f"❌ Error processing {instrument}: {e}")
            all_results[instrument] = {"error": str(e)}
    
    # Summary
    print("\n📊 AUTOMATED TRADING SUMMARY")
    print("=" * 60)
    
    for instrument, result in all_results.items():
        if "error" in result:
            print(f"❌ {instrument}: Error - {result['error']}")
        else:
            action = result.get("recommended_action", "NONE")
            quality = result.get("quality_score", 0)
            automated = "✅ CAMPAIGN CREATED" if result.get("campaign_created") else "📋 MANUAL"
            
            print(f"📈 {instrument}: {action} (Q: {quality:.1f}) - {automated}")
    
    if campaigns_created:
        print(f"\n🎯 CAMPAIGNS CREATED: {len(campaigns_created)}")
        for campaign in campaigns_created:
            print(f"  ✅ {campaign['instrument']}: {campaign['action']} (Q: {campaign['quality']:.1f}) - ID: {campaign['campaign_id']}")
        
        print(f"\n📁 Campaign files saved in: {trading_system.campaigns_dir}/")
        print("📋 Execute campaigns manually using entry.sh scripts")
        
    else:
        print("\n📋 No high-quality signals found for campaign creation")
    
    print("\n✅ Automated FDB trading analysis complete")

if __name__ == "__main__":
    main()
