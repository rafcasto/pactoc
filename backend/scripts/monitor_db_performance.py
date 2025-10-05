#!/usr/bin/env python3
"""
Database performance monitoring script.
Run this to monitor your PostgreSQL connection performance.
"""
import os
import sys
import time
import statistics
from datetime import datetime

# Add the parent directory to the path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_connection_performance(num_tests=10):
    """Test database connection performance multiple times."""
    print(f"🔍 Running {num_tests} database connection tests...")
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    connection_times = []
    successful_connections = 0
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        from app import create_app
        app = create_app()
        
        with app.app_context():
            from app.services.database_service import test_connection
            
            for i in range(num_tests):
                start_time = time.time()
                success = test_connection(retry_count=1)
                test_time = time.time() - start_time
                
                if success:
                    successful_connections += 1
                    connection_times.append(test_time)
                    print(f"Test {i+1:2d}: ✅ {test_time:.3f}s")
                else:
                    print(f"Test {i+1:2d}: ❌ Failed")
                
                # Small delay between tests
                time.sleep(0.1)
    
    except Exception as e:
        print(f"❌ Monitoring failed: {e}")
        return
    
    # Calculate statistics
    if connection_times:
        print("-" * 60)
        print("📊 Performance Statistics:")
        print(f"   Success Rate: {successful_connections}/{num_tests} ({successful_connections/num_tests*100:.1f}%)")
        print(f"   Average Time: {statistics.mean(connection_times):.3f}s")
        print(f"   Median Time:  {statistics.median(connection_times):.3f}s")
        print(f"   Min Time:     {min(connection_times):.3f}s")
        print(f"   Max Time:     {max(connection_times):.3f}s")
        
        if len(connection_times) > 1:
            print(f"   Std Deviation: {statistics.stdev(connection_times):.3f}s")
        
        # Performance assessment
        avg_time = statistics.mean(connection_times)
        if avg_time < 0.5:
            print("🚀 Performance: Excellent")
        elif avg_time < 1.0:
            print("✅ Performance: Good")
        elif avg_time < 2.0:
            print("⚠️  Performance: Acceptable (consider optimizations)")
        else:
            print("🐌 Performance: Slow (needs optimization)")
    
    print(f"🕐 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    # Allow custom number of tests
    num_tests = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    test_connection_performance(num_tests)
