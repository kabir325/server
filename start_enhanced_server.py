#!/usr/bin/env python3
"""
Start Enhanced Smart AI Load Balancer Server v3.1
With progress tracking and no timeout constraints
"""

import subprocess
import sys
import os

def main():
    """Start the enhanced smart server"""
    print("🚀 Starting Enhanced Smart AI Load Balancer Server v3.1")
    print("="*70)
    print("🆕 NEW FEATURES:")
    print("   ✅ No timeout constraints - clients can take as long as needed")
    print("   ✅ Real-time progress tracking for all clients")
    print("   ✅ Intelligent waiting with status updates")
    print("   ✅ Parallel processing with progress monitoring")
    print("="*70)
    
    # Check if gRPC files exist
    if not os.path.exists('load_balancer_pb2.py'):
        print("📦 Generating enhanced gRPC files...")
        try:
            subprocess.run([sys.executable, 'generate_grpc_files.py'], check=True)
            os.chdir('../..')
        except subprocess.CalledProcessError:
            print("❌ Failed to generate gRPC files")
            print("Make sure grpcio-tools is installed: pip install grpcio-tools")
            return
    
    # Start the enhanced server
    print("🌐 Starting enhanced smart load balancer server...")
    print("💡 Features:")
    print("   • Auto model discovery")
    print("   • Intelligent assignment") 
    print("   • Performance grouping")
    print("   • Progress tracking")
    print("   • No timeout limits")
    print()
    
    try:
        subprocess.run([sys.executable, 'smart_load_balancer_server.py'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Enhanced smart server stopped by user")
    except Exception as e:
        print(f"❌ Enhanced smart server error: {e}")
    finally:
        os.chdir('../..')

if __name__ == '__main__':
    main()