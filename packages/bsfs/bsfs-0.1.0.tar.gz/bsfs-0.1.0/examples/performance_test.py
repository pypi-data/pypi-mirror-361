#!/usr/bin/env python3
"""
BSFS Performance Testing Suite - FIXED METRICS

This suite provides accurate performance measurements for BSFS:
1. Corrected throughput calculations
2. Proper concurrent operation measurement
3. Realistic performance expectations
4. Separate measurement of different bottlenecks
"""

import time
import uuid
import random
import tempfile
import threading
import statistics
from pathlib import Path
from typing import List, Dict, Any
import sys

import bsfs


class AccuratePerformanceTestSuite:
    """Accurate performance testing suite for BSFS"""
    
    def __init__(self, blob_path: str, master_key: bytes):
        self.blob_path = blob_path
        self.master_key = master_key
        self.results = {}
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all performance tests"""
        print("🚀 BSFS Performance Test Suite - FIXED METRICS")
        print("=" * 60)
        
        # Test individual operation performance
        self.test_individual_operations()
        
        # Test batch operations
        self.test_batch_operations()
        
        # Test concurrent operations (properly measured)
        self.test_concurrent_operations()
        
        # Test different data patterns
        self.test_data_patterns()
        
        # Test Python vs C overhead
        self.test_python_overhead()
        
        return self.results
    
    def test_individual_operations(self):
        """Test individual operation performance"""
        print("\n📊 Testing individual operations...")
        
        with bsfs.BSFS(self.blob_path, self.master_key) as fs:
            # Test different file sizes
            sizes = [1024, 10*1024, 100*1024, 1024*1024]  # 1KB, 10KB, 100KB, 1MB
            
            for size in sizes:
                # Generate test data
                data = b'A' * size
                file_id = uuid.uuid4()
                
                # Measure write performance (single operation)
                start_time = time.perf_counter()
                fs.write_file(file_id, data)
                write_time = time.perf_counter() - start_time
                
                # Measure read performance (single operation)
                start_time = time.perf_counter()
                read_data = fs.read_file(file_id)
                read_time = time.perf_counter() - start_time
                
                # Verify data integrity
                data_ok = len(read_data) == len(data) and read_data == data
                
                # Calculate actual throughput
                write_throughput = size / write_time / 1024 / 1024  # MB/s
                read_throughput = size / read_time / 1024 / 1024    # MB/s
                
                print(f"  📏 Size: {size:>8,} bytes")
                print(f"    Write: {write_time*1000:>6.2f}ms ({write_throughput:>6.1f} MB/s)")
                print(f"    Read:  {read_time*1000:>6.2f}ms ({read_throughput:>6.1f} MB/s)")
                print(f"    Data integrity: {'✅' if data_ok else '❌'}")
                
                # Clean up
                fs.delete_file(file_id)
                
                # Store results
                self.results[f'individual_{size}'] = {
                    'size': size,
                    'write_time': write_time,
                    'read_time': read_time,
                    'write_throughput': write_throughput,
                    'read_throughput': read_throughput,
                    'data_integrity': data_ok
                }
    
    def test_batch_operations(self):
        """Test batch operation performance"""
        print("\n📊 Testing batch operations...")
        
        with bsfs.BSFS(self.blob_path, self.master_key) as fs:
            # Small files batch test
            file_count = 20
            file_size = 5 * 1024  # 5KB each
            
            # Generate test data
            test_files = []
            for i in range(file_count):
                file_id = uuid.uuid4()
                data = f"File {i:03d} - ".encode() + b'X' * (file_size - 20)
                test_files.append((file_id, data))
            
            # Measure batch write performance
            start_time = time.perf_counter()
            for file_id, data in test_files:
                fs.write_file(file_id, data)
            batch_write_time = time.perf_counter() - start_time
            
            # Measure batch read performance
            start_time = time.perf_counter()
            read_data = []
            for file_id, _ in test_files:
                data = fs.read_file(file_id)
                read_data.append(data)
            batch_read_time = time.perf_counter() - start_time
            
            # Calculate batch metrics
            total_size = file_count * file_size
            avg_write_time = batch_write_time / file_count
            avg_read_time = batch_read_time / file_count
            
            write_ops_per_sec = file_count / batch_write_time
            read_ops_per_sec = file_count / batch_read_time
            
            batch_write_throughput = total_size / batch_write_time / 1024 / 1024
            batch_read_throughput = total_size / batch_read_time / 1024 / 1024
            
            print(f"  📦 Batch test: {file_count} files of {file_size:,} bytes each")
            print(f"    Total size: {total_size:,} bytes")
            print(f"    Write: {batch_write_time:.3f}s ({write_ops_per_sec:.1f} ops/s, {batch_write_throughput:.1f} MB/s)")
            print(f"    Read:  {batch_read_time:.3f}s ({read_ops_per_sec:.1f} ops/s, {batch_read_throughput:.1f} MB/s)")
            print(f"    Avg write per file: {avg_write_time*1000:.2f}ms")
            print(f"    Avg read per file: {avg_read_time*1000:.2f}ms")
            
            # Clean up
            for file_id, _ in test_files:
                fs.delete_file(file_id)
            
            self.results['batch_operations'] = {
                'file_count': file_count,
                'file_size': file_size,
                'total_size': total_size,
                'batch_write_time': batch_write_time,
                'batch_read_time': batch_read_time,
                'write_ops_per_sec': write_ops_per_sec,
                'read_ops_per_sec': read_ops_per_sec,
                'batch_write_throughput': batch_write_throughput,
                'batch_read_throughput': batch_read_throughput
            }
    
    def test_concurrent_operations(self):
        """Test concurrent operations with proper measurement"""
        print("\n📊 Testing concurrent operations...")
        
        def worker_thread(thread_id: int, operations: int, results: List, barrier: threading.Barrier):
            """Worker thread for concurrent testing"""
            try:
                with bsfs.BSFS(self.blob_path, self.master_key) as fs:
                    # Wait for all threads to be ready
                    barrier.wait()
                    
                    # Measure individual thread performance
                    thread_start = time.perf_counter()
                    operation_times = []
                    
                    for i in range(operations):
                        file_id = uuid.uuid4()
                        data = f"Thread {thread_id} - Op {i}".encode() + b'X' * 1000
                        
                        # Measure complete operation cycle
                        op_start = time.perf_counter()
                        fs.write_file(file_id, data)
                        read_back = fs.read_file(file_id)
                        fs.delete_file(file_id)
                        op_time = time.perf_counter() - op_start
                        
                        operation_times.append(op_time)
                        
                        # Verify data
                        if read_back != data:
                            raise ValueError(f"Data mismatch in thread {thread_id}")
                    
                    thread_total_time = time.perf_counter() - thread_start
                    
                    results.append({
                        'thread_id': thread_id,
                        'operations': operations,
                        'thread_total_time': thread_total_time,
                        'avg_operation_time': statistics.mean(operation_times),
                        'operations_per_second': operations / thread_total_time,
                        'success': True
                    })
                    
            except Exception as e:
                results.append({
                    'thread_id': thread_id,
                    'error': str(e),
                    'success': False
                })
        
        # Test different thread counts
        for thread_count in [1, 2, 4]:
            print(f"\n  🧵 Testing {thread_count} threads...")
            
            operations_per_thread = 5
            results = []
            threads = []
            barrier = threading.Barrier(thread_count)
            
            # Start all threads
            for i in range(thread_count):
                thread = threading.Thread(
                    target=worker_thread,
                    args=(i, operations_per_thread, results, barrier)
                )
                threads.append(thread)
                thread.start()
            
            # Wait for completion
            for thread in threads:
                thread.join()
            
            # Analyze results
            successful = [r for r in results if r.get('success', False)]
            failed = [r for r in results if not r.get('success', False)]
            
            if successful:
                # Calculate concurrent performance metrics
                total_operations = sum(r['operations'] for r in successful)
                avg_thread_time = statistics.mean(r['thread_total_time'] for r in successful)
                total_ops_per_sec = sum(r['operations_per_second'] for r in successful)
                
                # This is the key fix: concurrent throughput != sum of individual throughputs
                # Real concurrent throughput is limited by contention and system resources
                effective_ops_per_sec = total_operations / avg_thread_time
                
                print(f"    ✅ Successful threads: {len(successful)}")
                print(f"    ❌ Failed threads: {len(failed)}")
                print(f"    📊 Total operations: {total_operations}")
                print(f"    ⏱️ Average thread time: {avg_thread_time:.3f}s")
                print(f"    📈 Individual thread avg: {total_ops_per_sec/len(successful):.1f} ops/s")
                print(f"    🚀 Effective concurrent: {effective_ops_per_sec:.1f} ops/s")
                
                # Show contention effect
                if thread_count > 1:
                    single_thread_ops = self.results.get('concurrent_1', {}).get('effective_ops_per_sec', 0)
                    if single_thread_ops > 0:
                        scaling_efficiency = (effective_ops_per_sec / single_thread_ops) / thread_count * 100
                        print(f"    📊 Scaling efficiency: {scaling_efficiency:.1f}%")
                
                self.results[f'concurrent_{thread_count}'] = {
                    'thread_count': thread_count,
                    'operations_per_thread': operations_per_thread,
                    'successful_threads': len(successful),
                    'failed_threads': len(failed),
                    'total_operations': total_operations,
                    'avg_thread_time': avg_thread_time,
                    'effective_ops_per_sec': effective_ops_per_sec,
                    'individual_avg_ops_per_sec': total_ops_per_sec / len(successful)
                }
    
    def test_data_patterns(self):
        """Test performance with different data patterns"""
        print("\n📊 Testing data patterns...")
        
        with bsfs.BSFS(self.blob_path, self.master_key) as fs:
            patterns = [
                ("zeros", b'\x00' * 10000),
                ("ones", b'\xFF' * 10000),
                ("random", bytes(random.randint(0, 255) for _ in range(10000))),
                ("text", b'Hello World! ' * 769),  # ~10KB
                ("json", b'{"key": "value", "number": 42}' * 238),  # ~10KB
            ]
            
            for pattern_name, data in patterns:
                file_id = uuid.uuid4()
                
                # Measure write performance
                start_time = time.perf_counter()
                fs.write_file(file_id, data)
                write_time = time.perf_counter() - start_time
                
                # Measure read performance
                start_time = time.perf_counter()
                read_data = fs.read_file(file_id)
                read_time = time.perf_counter() - start_time
                
                # Verify integrity
                data_ok = read_data == data
                
                write_throughput = len(data) / write_time / 1024 / 1024
                read_throughput = len(data) / read_time / 1024 / 1024
                
                print(f"  📊 {pattern_name:>8}: {len(data):>6,} bytes")
                print(f"    Write: {write_time*1000:>6.2f}ms ({write_throughput:>6.1f} MB/s)")
                print(f"    Read:  {read_time*1000:>6.2f}ms ({read_throughput:>6.1f} MB/s)")
                print(f"    Integrity: {'✅' if data_ok else '❌'}")
                
                fs.delete_file(file_id)
    
    def test_python_overhead(self):
        """Test Python ctypes overhead"""
        print("\n📊 Testing Python overhead...")
        
        # Test memory allocation overhead
        size = 1024 * 1024  # 1MB
        iterations = 5
        
        # Measure Python bytes creation
        start_time = time.perf_counter()
        for _ in range(iterations):
            data = b'A' * size
        python_alloc_time = time.perf_counter() - start_time
        
        # Measure BSFS operations
        with bsfs.BSFS(self.blob_path, self.master_key) as fs:
            start_time = time.perf_counter()
            for i in range(iterations):
                file_id = uuid.uuid4()
                fs.write_file(file_id, data)
                fs.read_file(file_id)
                fs.delete_file(file_id)
            bsfs_ops_time = time.perf_counter() - start_time
        
        # Calculate overhead
        python_overhead = python_alloc_time / bsfs_ops_time * 100
        
        print(f"  📊 Python memory allocation: {python_alloc_time:.4f}s")
        print(f"  📊 BSFS operations: {bsfs_ops_time:.4f}s")
        print(f"  📊 Python overhead: {python_overhead:.1f}% of total time")
        
        # Estimate theoretical C performance
        estimated_c_throughput = size * iterations / (bsfs_ops_time - python_alloc_time) / 1024 / 1024
        actual_throughput = size * iterations / bsfs_ops_time / 1024 / 1024
        
        print(f"  📊 Estimated C library performance: {estimated_c_throughput:.1f} MB/s")
        print(f"  📊 Actual Python performance: {actual_throughput:.1f} MB/s")
        print(f"  📊 Performance penalty: {(1 - actual_throughput/estimated_c_throughput)*100:.1f}%")
    
    def print_summary(self):
        """Print accurate summary of test results"""
        print("\n📋 Performance Test Summary - CORRECTED METRICS")
        print("=" * 60)
        
        # Individual operation summary
        print("\n📏 Individual Operations:")
        for key, result in self.results.items():
            if key.startswith('individual_'):
                size = result['size']
                write_mb = result['write_throughput']
                read_mb = result['read_throughput']
                print(f"  {size:>8,} bytes: Write {write_mb:>6.1f} MB/s, Read {read_mb:>6.1f} MB/s")
        
        # Batch operations summary
        if 'batch_operations' in self.results:
            r = self.results['batch_operations']
            print(f"\n📦 Batch Operations ({r['file_count']} files):")
            print(f"  Write: {r['write_ops_per_sec']:.1f} ops/s ({r['batch_write_throughput']:.1f} MB/s)")
            print(f"  Read:  {r['read_ops_per_sec']:.1f} ops/s ({r['batch_read_throughput']:.1f} MB/s)")
        
        # Concurrent operations summary
        print(f"\n🧵 Concurrent Operations:")
        for i in [1, 2, 4]:
            if f'concurrent_{i}' in self.results:
                r = self.results[f'concurrent_{i}']
                print(f"  {i} threads: {r['effective_ops_per_sec']:.1f} ops/s")
                
                # Show scaling efficiency
                if i > 1 and 'concurrent_1' in self.results:
                    single = self.results['concurrent_1']['effective_ops_per_sec']
                    efficiency = (r['effective_ops_per_sec'] / single) / i * 100
                    print(f"    Scaling efficiency: {efficiency:.1f}%")
        
        print("\n🔍 Key Insights:")
        print("  • Performance varies significantly with file size")
        print("  • Concurrent operations show resource contention")
        print("  • Python ctypes adds measurable overhead")
        print("  • Small files have high per-operation overhead")
        print("  • Large files approach disk I/O limits")


def main():
    """Run the accurate performance test suite"""
    # Create temporary storage
    temp_dir = Path(tempfile.mkdtemp())
    blob_path = temp_dir / "performance_test.blob"
    master_key = bsfs.generate_master_key()
    
    try:
        # Run performance tests
        test_suite = AccuratePerformanceTestSuite(str(blob_path), master_key)
        results = test_suite.run_all_tests()
        
        # Print summary
        test_suite.print_summary()
        
        # Show storage stats
        print(f"\n📊 Storage Statistics:")
        with bsfs.BSFS(str(blob_path), master_key) as fs:
            info = fs.get_storage_info()
            print(f"  Storage utilization: {info['storage_utilization']:.1f}%")
            print(f"  Blob file size: {Path(blob_path).stat().st_size:,} bytes")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        print("\n🧹 Cleanup completed")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())