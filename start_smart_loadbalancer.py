#!/usr/bin/env python3
"""
Unified Smart Load Balancer Startup Script
Starts both the gRPC server and HTTP wrapper in separate threads
"""

import threading
import time
import sys
import os

def start_grpc_server():
    """Start the gRPC smart load balancer server"""
    print("🚀 Starting gRPC Smart Load Balancer Server...")
    os.system('python smart_load_balancer_server.py')

def start_http_wrapper():
    """Start the HTTP wrapper for frontend communication"""
    # Give the gRPC server time to start
    time.sleep(2)
    print("🌐 Starting HTTP Wrapper...")
    os.system('python smart_load_balancer_http_wrapper_v4.py')

if __name__ == '__main__':
    print("="*60)
    print("🤖 SMART AI LOAD BALANCER v3.0 - UNIFIED STARTUP")
    print("="*60)
    print()
    print("This will start:")
    print("  1. gRPC Server (port 50051) - for client communication")
    print("  2. HTTP Wrapper (port 5001) - for frontend communication")
    print()
    print("Press Ctrl+C to stop all services")
    print("="*60)
    print()
    
    try:
        # Start gRPC server in a separate thread
        grpc_thread = threading.Thread(target=start_grpc_server, daemon=True)
        grpc_thread.start()
        
        # Start HTTP wrapper in a separate thread
        http_thread = threading.Thread(target=start_http_wrapper, daemon=True)
        http_thread.start()
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down Smart Load Balancer services...")
        print("Goodbye!")
        sys.exit(0)
