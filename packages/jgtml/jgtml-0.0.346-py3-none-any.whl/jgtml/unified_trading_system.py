#!/usr/bin/env python3
"""
🚀 Unified JGT Trading System - Proper Integration
Integrates real FDB scanner, proper cache system, and jgtagentic components
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# Add jgtml to path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import REAL components
try:
    from fdb_scanner_2408 import (
        main as fdb_main, 
        parse_args as fdb_parse_args, 
        _make_cached_filepath, 
        generate_fresh_and_cache,
        get_jgt_cache_root_dir,
        _ini_cache
    )
    FDB_SCANNER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ FDB Scanner import failed: {e}")
    FDB_SCANNER_AVAILABLE = False

try:
    from jgtapp import cds, ids
    JGTAPP_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ JGTApp import failed: {e}")
    JGTAPP_AVAILABLE = False

try:
    from jgtutils import jgtcommon
    JGTUTILS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ JGTUtils import failed: {e}")
    JGTUTILS_AVAILABLE = False

# Import jgtagentic components if available
try:
    sys.path.insert(0, '/src/jgtagentic')
    from jgtagentic.fdbscan_agent import FDBScanAgent
    from jgtagentic.enhanced_fdb_scanner import EnhancedFDBScanner
    JGTAGENTIC_AVAILABLE = True
except ImportError:
    JGTAGENTIC_AVAILABLE = False

class UnifiedTradingSystem:
    """
    Proper unified trading system using real JGT infrastructure
    """
    
    def __init__(self, cache_dir=None, demo=True, quality_threshold=8.0):
        # Initialize cache directory properly
        if cache_dir:
            self.cache_dir = os.path.abspath(cache_dir)
            os.environ["JGT_CACHE"] = self.cache_dir
        else:
            self.cache_dir = get_jgt_cache_root_dir() if FDB_SCANNER_AVAILABLE else os.path.expanduser("~/.cache/jgt")
        
        self.demo = demo
        self.quality_threshold = quality_threshold
        
        # Ensure cache directory exists and is writable
        os.makedirs(self.cache_dir, exist_ok=True)
        os.environ["JGT_CACHE"] = self.cache_dir
        
        # Initialize cache system
        if FDB_SCANNER_AVAILABLE:
            try:
                _ini_cache()
            except Exception as e:
                print(f"⚠️ Cache initialization warning: {e}")
        
        # Initialize jgtagentic components if available
        if JGTAGENTIC_AVAILABLE:
            self.fdb_agent = FDBScanAgent(real=True)
            self.enhanced_scanner = EnhancedFDBScanner()
        else:
            self.fdb_agent = None
            self.enhanced_scanner = None
            
        print(f"🚀 Unified Trading System Initialized")
        print(f"   Cache Directory: {self.cache_dir}")
        print(f"   Demo Mode: {self.demo}")
        print(f"   Quality Threshold: {self.quality_threshold}")
        print(f"   FDB Scanner Available: {FDB_SCANNER_AVAILABLE}")
        print(f"   JGTApp Available: {JGTAPP_AVAILABLE}")
        print(f"   JGTagentic Available: {JGTAGENTIC_AVAILABLE}")
    
    def refresh_instrument_data_with_jgtapp(self, instrument, timeframes=None):
        """
        Refresh CDS data using REAL jgtapp.cds() function
        """
        if not JGTAPP_AVAILABLE:
            print("❌ JGTApp not available - cannot refresh data")
            return False
            
        if timeframes is None:
            timeframes = ["H4", "H1", "m15"]
            
        print(f"🔄 Refreshing {instrument} data using jgtapp.cds()...")
        
        success_count = 0
        for tf in timeframes:
            try:
                # Use REAL jgtapp.cds() function 
                cds(instrument, tf, use_fresh=True, use_full=True)
                print(f"  ✅ {instrument} {tf}: CDS data generated")
                success_count += 1
            except Exception as e:
                print(f"  ❌ {instrument} {tf}: Failed - {e}")
                
        return success_count > 0
    
    def refresh_instrument_data_with_fdb_cache(self, instrument, timeframes=None):
        """
        Generate data using the FDB scanner's cache mechanism
        """
        if not FDB_SCANNER_AVAILABLE:
            print("❌ FDB Scanner not available - cannot generate cache")
            return False
            
        if timeframes is None:
            timeframes = ["H4", "H1", "m15"]
            
        print(f"🔄 Generating {instrument} cache data using FDB mechanism...")
        
        success_count = 0
        for tf in timeframes:
            try:
                # Use the REAL cache generation from FDB scanner
                cache_filepath = _make_cached_filepath(instrument, tf, suffix="_cds_cache")
                df = generate_fresh_and_cache(instrument, tf, 300, cache_filepath)
                
                if df is not None and len(df) > 0:
                    print(f"  ✅ {instrument} {tf}: Cache generated ({len(df)} bars)")
                    success_count += 1
                else:
                    print(f"  ⚠️ {instrument} {tf}: Empty data")
                    
            except Exception as e:
                print(f"  ❌ {instrument} {tf}: Cache generation failed - {e}")
                
        return success_count > 0
    
    def scan_with_real_fdb(self, instruments=None, timeframes=None):
        """
        Use the REAL FDB scanner (fdb_scanner_2408.py)
        """
        if not FDB_SCANNER_AVAILABLE:
            print("❌ FDB Scanner not available")
            return False
            
        if instruments is None:
            instruments = ["EUR/USD", "GBP/USD", "XAU/USD"]
        if timeframes is None:
            timeframes = ["H4", "H1", "m15"]
            
        print(f"🔍 Running REAL FDB Scanner")
        
        # Set environment variables for FDB scanner
        os.environ["INSTRUMENTS"] = ",".join(instruments)
        os.environ["TIMEFRAMES"] = ",".join(timeframes)
        
        # Save current sys.argv
        original_argv = sys.argv.copy()
        
        try:
            # Set up argv for FDB scanner
            sys.argv = ["fdb_scanner_2408.py", "--verbose", "2"]
            if self.demo:
                sys.argv.append("--demo")
                
            # Run the REAL FDB scanner
            fdb_main()
            
            print("✅ FDB Scanner completed")
            return True
            
        except SystemExit as e:
            # FDB scanner may call sys.exit() - this is normal
            if e.code == 0:
                print("✅ FDB Scanner completed successfully")
                return True
            else:
                print(f"❌ FDB Scanner exited with code: {e.code}")
                return False
        except Exception as e:
            print(f"❌ FDB Scanner failed: {e}")
            return False
        finally:
            # Restore original argv
            sys.argv = original_argv
            
    def enhanced_scan_with_jgtagentic(self, observation=None, instruments=None):
        """
        Use jgtagentic enhanced scanning if available
        """
        if not JGTAGENTIC_AVAILABLE:
            print("⚠️ JGTagentic not available - using basic FDB scan")
            return self.scan_with_real_fdb(instruments)
            
        if observation:
            print(f"🔮 Enhanced observation-based scanning: {observation}")
            result = self.fdb_agent.scan_with_observation(observation, instruments)
            return result
        else:
            print(f"🔍 Enhanced intent-aware scanning")
            result = self.fdb_agent.scan_all(with_intent=True)
            return result
    
    def analyze_instrument(self, instrument, timeframes=None):
        """
        Complete analysis pipeline for an instrument
        """
        print(f"\n🎯 ANALYZING {instrument}")
        print("-" * 40)
        
        timeframes = timeframes or ["H4", "H1", "m15"]
        
        # Step 1: Try to refresh data using jgtapp first
        data_refreshed = False
        if JGTAPP_AVAILABLE:
            print("🔄 Attempting data refresh with jgtapp.cds()...")
            data_refreshed = self.refresh_instrument_data_with_jgtapp(instrument, timeframes)
            
        # Step 2: If jgtapp failed, try FDB cache generation
        if not data_refreshed and FDB_SCANNER_AVAILABLE:
            print("🔄 Attempting data refresh with FDB cache mechanism...")
            data_refreshed = self.refresh_instrument_data_with_fdb_cache(instrument, timeframes)
            
        if not data_refreshed:
            print(f"⚠️ Data refresh failed for {instrument} - continuing with existing cache")
            
        # Step 3: Check cache files exist
        cache_status = {}
        
        for tf in timeframes:
            if FDB_SCANNER_AVAILABLE:
                cache_file = _make_cached_filepath(instrument, tf, suffix="_cds_cache")
            else:
                cache_file = f"{self.cache_dir}/fdb_scanners/{instrument.replace('/', '-')}_{tf}_cds_cache.csv"
                
            exists = os.path.exists(cache_file)
            size = os.path.getsize(cache_file) if exists else 0
            cache_status[tf] = {"exists": exists, "size": size, "path": cache_file}
            status_icon = "✅" if exists and size > 0 else "❌"
            print(f"  📁 {tf} cache: {status_icon} {cache_file} ({size} bytes)")
            
        # Step 4: Run FDB analysis if cache exists
        has_cache = any(status["exists"] and status["size"] > 0 for status in cache_status.values())
        
        if has_cache:
            print("📊 Running FDB analysis...")
            fdb_success = self.scan_with_real_fdb([instrument], timeframes)
            
            if fdb_success:
                # Step 5: Enhanced analysis if jgtagentic available
                if JGTAGENTIC_AVAILABLE:
                    observation = f"Analyzing {instrument} for trading opportunities across {', '.join(timeframes)}"
                    result = self.enhanced_scan_with_jgtagentic(observation, [instrument])
                    
                    if result and result.get('success'):
                        recommendations = result.get('scan_results', {}).get('recommendations', {})
                        print(f"🎯 Enhanced Analysis Result: {recommendations.get('action', 'wait')}")
                        print(f"📋 Reason: {recommendations.get('reason', 'N/A')}")
                        return True
                        
            return fdb_success
        else:
            print(f"❌ No valid cache data available for {instrument}")
            return False
    
    def run_trading_session(self, instruments=None, observation=None):
        """
        Run complete trading session
        """
        instruments = instruments or ["EUR/USD", "GBP/USD", "XAU/USD"]
        
        print(f"\n🌸 UNIFIED TRADING SESSION")
        print("=" * 50)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Instruments: {', '.join(instruments)}")
        print(f"Cache Directory: {self.cache_dir}")
        print("=" * 50)
        
        results = {}
        
        for instrument in instruments:
            try:
                success = self.analyze_instrument(instrument)
                results[instrument] = "SUCCESS" if success else "FAILED"
            except Exception as e:
                print(f"❌ {instrument} analysis failed: {e}")
                results[instrument] = f"ERROR: {e}"
                
        print(f"\n📊 SESSION RESULTS")
        print("=" * 30)
        for instrument, status in results.items():
            status_icon = "✅" if status == "SUCCESS" else "❌"
            print(f"{status_icon} {instrument}: {status}")
            
        return results

def main():
    parser = argparse.ArgumentParser(description="Unified JGT Trading System")
    parser.add_argument("--instruments", nargs="+", default=["EUR/USD", "GBP/USD", "XAU/USD"])
    parser.add_argument("--timeframes", nargs="+", default=["H4", "H1", "m15"])
    parser.add_argument("--cache-dir", help="Cache directory (defaults to JGT_CACHE env var)")
    parser.add_argument("--demo", action="store_true", default=True, help="Demo mode")
    parser.add_argument("--quality-threshold", type=float, default=8.0, help="Quality threshold")
    parser.add_argument("--observation", help="Market observation for enhanced scanning")
    
    args = parser.parse_args()
    
    # Initialize system
    system = UnifiedTradingSystem(
        cache_dir=args.cache_dir,
        demo=args.demo,
        quality_threshold=args.quality_threshold
    )
    
    # Run trading session
    results = system.run_trading_session(args.instruments, args.observation)
    
    # Print final status
    success_count = sum(1 for status in results.values() if status == "SUCCESS")
    total_count = len(results)
    
    print(f"\n🎯 FINAL STATUS: {success_count}/{total_count} instruments successful")
    
    return 0 if success_count > 0 else 1

if __name__ == "__main__":
    sys.exit(main()) 