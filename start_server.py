#!/usr/bin/env python3
"""
Start Smart AI Load Balancer Server v3.0
"""

import subprocess
import sys
import os

def main():
    """Start the smart server with proper setup"""
    print("🚀 Starting Smart AI Load Balancer Server v3.0")
    print("="*60)
    
    # Check if gRPC files exist
    if not os.path.exists('load_balancer_pb2.py'):
        print("📦 Generating gRPC files...")
        try:
            subprocess.run([sys.executable, 'generate_grpc_files.py'], check=True)
        except subprocess.CalledProcessError:
            print("❌ Failed to generate gRPC files")
            print("Make sure grpcio-tools is installed: pip install grpcio-tools")
            return
    
    # Start the smart server
    print("🌐 Starting smart load balancer server...")
    print("💡 Features: Auto model discovery, intelligent assignment, performance grouping")
    try:
        subprocess.run([sys.executable, 'smart_load_balancer_server.py'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Smart server stopped by user")
    except Exception as e:
        print(f"❌ Smart server error: {e}")

if __name__ == '__main__':
    main()