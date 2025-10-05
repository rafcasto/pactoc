#!/bin/bash

# Database Performance Testing Script
# Run this script to test your PostgreSQL connection performance

echo "🔍 PostgreSQL Connection Performance Test"
echo "=========================================="

cd /Users/rafaelcastillo/pactoc/backend
source venv/bin/activate

echo "🚀 Testing optimized configuration..."
python3 -c "
import time
import statistics
from dotenv import load_dotenv
load_dotenv()

from app import create_app
app = create_app()

connection_times = []
print('Running 10 connection tests...')

with app.app_context():
    from app.services.database_service import test_connection
    
    for i in range(10):
        start_time = time.time()
        success = test_connection(retry_count=1)
        test_time = time.time() - start_time
        
        if success:
            connection_times.append(test_time)
            print(f'Test {i+1:2d}: {test_time:.3f}s')
        else:
            print(f'Test {i+1:2d}: FAILED')

if connection_times:
    avg_time = statistics.mean(connection_times)
    print(f'\\n📊 Average connection time: {avg_time:.3f}s')
    print(f'📊 Fastest connection: {min(connection_times):.3f}s')
    print(f'📊 Slowest connection: {max(connection_times):.3f}s')
    
    if avg_time < 0.5:
        print('🚀 Performance: Excellent!')
    elif avg_time < 1.0:
        print('✅ Performance: Good')
    else:
        print('⚠️  Performance: Could be improved')
"

echo ""
echo "✅ Performance test completed!"
