#!/usr/bin/env python3

"""
JGT Trading System Orchestrator

This module orchestrates the complete JGT trading system using the jgtcore timeframe library
for proper separation between CLI utilities and core logic. It provides both real-time
scheduling and simulation modes for testing.

Usage:
    # Real-time mode
    python trading_orchestrator.py --timeframe H4 --instruments EUR-USD,GBP-USD --demo
    
    # Test mode (simulation)
    python trading_orchestrator.py --timeframe H4 --instruments EUR-USD,GBP-USD --demo --test-mode
"""

import argparse
import sys
import time
import subprocess
from typing import List, Optional
import os

# Import jgtcore for timeframe logic
try:
    import jgtcore
except ImportError:
    # Add jgtcore to path if not installed
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'jgtcore'))
    import jgtcore


class TradingOrchestrator:
    """Main trading system orchestrator using jgtcore timeframe library."""
    
    def __init__(self, timeframe: str, instruments: List[str], 
                 quality_threshold: float = 8.0, demo: bool = True, test_mode: bool = False):
        self.timeframe = timeframe
        self.instruments = instruments
        self.quality_threshold = quality_threshold
        self.demo = demo
        self.test_mode = test_mode
        
        # Initialize timeframe checker using jgtcore
        self.timeframe_checker = jgtcore.TimeframeChecker(timeframe)
        
        print(f"🚀 JGT Trading Orchestrator Initialized")
        print(f"📊 Timeframe: {timeframe} | Instruments: {','.join(instruments)}")
        print(f"🎯 Quality Threshold: {quality_threshold} | Demo: {demo}")
        if test_mode:
            print("⚡ TEST MODE ENABLED - Using simulation")
    
    def run_enhanced_trading_analysis(self) -> bool:
        """Run enhanced trading CLI analysis."""
        try:
            instruments_str = ','.join(self.instruments)
            mode_flag = '--demo' if self.demo else '--real'
            
            cmd = [
                'enhancedtradingcli', 'auto', 
                '-i', instruments_str,
                mode_flag,
                '--quality-threshold', str(self.quality_threshold)
            ]
            
            print(f"🔍 Running Enhanced Trading Analysis: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Enhanced trading analysis completed successfully")
                if result.stdout:
                    print(f"📋 Output: {result.stdout.strip()}")
                return True
            else:
                print(f"❌ Enhanced trading analysis failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error running enhanced trading analysis: {e}")
            return False
    
    def generate_analysis_charts(self) -> bool:
        """Generate analysis charts for all instruments."""
        success_count = 0
        
        for instrument in self.instruments:
            try:
                print(f"📈 Generating chart for {instrument} {self.timeframe}")
                
                cmd = [
                    'jgtads', '-i', instrument, '-t', self.timeframe,
                    '--save_figure', 'charts/',
                    '--save_figure_as_timeframe'
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"✅ Chart generated for {instrument}")
                    success_count += 1
                else:
                    print(f"⚠️  Chart generation failed for {instrument}: {result.stderr}")
                    
            except Exception as e:
                print(f"❌ Error generating chart for {instrument}: {e}")
        
        return success_count > 0
    
    def update_trailing_stops(self) -> bool:
        """Update trailing stops for active trades."""
        try:
            mode_flag = '--demo' if self.demo else '--real'
            
            # Refresh trade data
            cmd_refresh = ['jgtapp', 'fxtr', mode_flag]
            print("🔄 Refreshing trade data...")
            
            result = subprocess.run(cmd_refresh, capture_output=True, text=True)
            if result.returncode != 0:
                print("⚠️  No active trades found or trade data unavailable")
                return False
            
            print("✅ Trade data refreshed")
            
            # Update FDB-based trailing stops with Alligator fallback
            print("🐊 Updating FDB-based trailing stops with Alligator fallback...")
            cmd_stops = ['jgtapp', 'fxmvstopfdb', '-t', self.timeframe, '--lips', mode_flag]
            
            result = subprocess.run(cmd_stops, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ FDB trailing stops updated")
                return True
            else:
                print(f"⚠️  FDB trailing stops update failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error updating trailing stops: {e}")
            return False
    
    def quick_monitoring_update(self) -> bool:
        """Quick chart update for monitoring."""
        try:
            primary_instrument = self.instruments[0] if self.instruments else "EUR-USD"
            
            cmd = [
                'jgtads', '-i', primary_instrument, '-t', 'm5',
                '--save_figure', 'charts/', '-tf'
            ]
            
            print(f"📈 Quick monitoring chart update for {primary_instrument}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Monitoring chart updated")
                return True
            else:
                print(f"⚠️  Monitoring chart update failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error updating monitoring chart: {e}")
            return False
    
    def rapid_trade_status_check(self) -> bool:
        """Ultra-quick trade status check."""
        try:
            mode_flag = '--demo' if self.demo else '--real'
            cmd = ['jgtapp', 'fxtr', mode_flag, '--nosave']
            
            print("⚡ Rapid trade status check...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Trade status checked")
                return True
            else:
                print("⚠️  Trade status check failed")
                return False
                
        except Exception as e:
            print(f"❌ Error checking trade status: {e}")
            return False
    
    def process_timeframe_trigger(self) -> bool:
        """Process actions when timeframe is triggered."""
        print(f"🎯 Processing {self.timeframe} timeframe trigger...")
        
        if self.timeframe in ["H4", "H1", "D1"]:
            print("📈 PRIMARY MARKET ANALYSIS MODE")
            
            # Step 1: Enhanced trading analysis
            if not self.run_enhanced_trading_analysis():
                return False
            
            # Step 2: Generate analysis charts
            if not self.generate_analysis_charts():
                print("⚠️  Chart generation had issues but continuing...")
            
            return True
            
        elif self.timeframe in ["m15", "m5"]:
            print("🎯 TRADE MANAGEMENT MODE")
            
            # Update trailing stops
            self.update_trailing_stops()
            
            # Quick monitoring if m5
            if self.timeframe == "m5":
                self.quick_monitoring_update()
            
            return True
            
        elif self.timeframe == "m1":
            print("⚡ RAPID MONITORING MODE")
            
            # Ultra-quick status check
            return self.rapid_trade_status_check()
        
        else:
            print(f"❌ Unsupported timeframe: {self.timeframe}")
            return False
    
    def run_single_cycle(self) -> bool:
        """Run a single trading cycle (for testing)."""
        if self.test_mode:
            print(f"🔄 SIMULATION: {self.timeframe} timeframe reached")
            time.sleep(1)  # Small delay for realism
            return self.process_timeframe_trigger()
        else:
            # Check if timeframe should trigger now
            if self.timeframe_checker.check_now():
                return self.process_timeframe_trigger()
            else:
                return False
    
    def run_continuous(self, max_cycles: Optional[int] = None) -> None:
        """Run continuous trading orchestration."""
        cycle_count = 0
        
        if self.test_mode:
            # In test mode, just run once or a few cycles
            max_cycles = max_cycles or 1
            print(f"🧪 Test mode: Running {max_cycles} cycle(s)")
            
            for i in range(max_cycles):
                print(f"\n--- Test Cycle {i+1}/{max_cycles} ---")
                self.run_single_cycle()
                if i < max_cycles - 1:
                    time.sleep(2)  # Short delay between test cycles
            
            print("🎯 Test cycles completed")
            return
        
        # Real-time mode
        print(f"🔄 Starting continuous monitoring for {self.timeframe} timeframe...")
        
        # Show next trigger time
        next_seconds = self.timeframe_checker.seconds_until_next_trigger()
        if next_seconds:
            minutes = next_seconds // 60
            seconds = next_seconds % 60
            print(f"⏰ Next {self.timeframe} trigger in: {minutes}m {seconds}s")
        
        try:
            while True:
                if self.run_single_cycle():
                    cycle_count += 1
                    print(f"✅ Cycle {cycle_count} completed")
                    
                    if max_cycles and cycle_count >= max_cycles:
                        print(f"🏁 Reached maximum cycles ({max_cycles})")
                        break
                
                # Sleep appropriate amount for timeframe
                if self.timeframe == "m1":
                    time.sleep(2)
                elif self.timeframe in ["m5", "m15"]:
                    time.sleep(30)
                else:
                    time.sleep(60)
                    
        except KeyboardInterrupt:
            print("\n🛑 Trading orchestrator stopped by user")
        except Exception as e:
            print(f"\n❌ Trading orchestrator error: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="JGT Trading System Orchestrator",
        epilog="Example: python trading_orchestrator.py --timeframe H4 --instruments EUR-USD,GBP-USD --demo --test-mode"
    )
    
    parser.add_argument(
        '--timeframe', '-t', 
        default='H4',
        help='Trading timeframe (m1, m5, m15, H1, H4, D1)'
    )
    
    parser.add_argument(
        '--instruments', '-i',
        default='EUR-USD,GBP-USD,XAU-USD',
        help='Comma-separated list of instruments'
    )
    
    parser.add_argument(
        '--quality-threshold', '-q',
        type=float, default=8.0,
        help='Quality threshold for trading signals'
    )
    
    parser.add_argument(
        '--demo', action='store_true', default=True,
        help='Use demo account (default: True)'
    )
    
    parser.add_argument(
        '--real', action='store_true',
        help='Use real account (overrides --demo)'
    )
    
    parser.add_argument(
        '--test-mode', action='store_true',
        help='Enable test mode (simulation without real timeframe waiting)'
    )
    
    parser.add_argument(
        '--max-cycles', type=int,
        help='Maximum number of cycles to run (useful for testing)'
    )
    
    args = parser.parse_args()
    
    # Parse instruments
    instruments = [inst.strip() for inst in args.instruments.split(',')]
    
    # Determine demo mode
    demo_mode = not args.real  # Default to demo unless --real is specified
    
    # Create and run orchestrator
    orchestrator = TradingOrchestrator(
        timeframe=args.timeframe,
        instruments=instruments,
        quality_threshold=args.quality_threshold,
        demo=demo_mode,
        test_mode=args.test_mode
    )
    
    if args.test_mode or args.max_cycles:
        orchestrator.run_continuous(max_cycles=args.max_cycles)
    else:
        orchestrator.run_continuous()


if __name__ == "__main__":
    main() 
  
