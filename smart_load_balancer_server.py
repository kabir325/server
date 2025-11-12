#!/usr/bin/env python3
"""
Smart AI Load Balancer Server v3.0
Intelligent fog computing load balancer with automatic model discovery and assignment
"""

import grpc
from concurrent import futures
import threading
import time
import logging
import uuid
import socket
from typing import Dict, List
import subprocess
import json

# Import generated gRPC files
import load_balancer_pb2
import load_balancer_pb2_grpc

# Import smart components
from performance_evaluator import PerformanceEvaluator
from model_manager import SmartModelManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SmartLoadBalancerServer(load_balancer_pb2_grpc.LoadBalancerServicer):
    """Smart Load Balancer Server with intelligent model management"""
    
    def __init__(self):
        self.clients: Dict[str, Dict] = {}
        self.server_specs = PerformanceEvaluator.get_system_specs()
        self.model_manager = SmartModelManager()
        self._lock = threading.Lock()
        
        logger.info("🚀 Smart AI Load Balancer Server v3.0 Started")
        logger.info(f"Server Performance Score: {self.server_specs['performance_score']}")
        logger.info(f"Available Models: {len(self.model_manager.available_models)}")
        
        # Display available models
        for model in self.model_manager.available_models:
            logger.info(f"   📦 {model.name}: {self._format_parameters(model.parameters)} "
                       f"(complexity: {model.complexity_score}/10)")
        
        logger.info("Waiting for clients to connect...")
    
    def RegisterClient(self, request, context):
        """Register a new client with smart model assignment"""
        try:
            with self._lock:
                client_id = request.client_id
                specs = {
                    'cpu_cores': request.specs.cpu_cores,
                    'cpu_frequency_ghz': request.specs.cpu_frequency_ghz,
                    'ram_gb': request.specs.ram_gb,
                    'gpu_info': request.specs.gpu_info,
                    'gpu_memory_gb': request.specs.gpu_memory_gb,
                    'os_info': request.specs.os_info,
                    'performance_score': request.specs.performance_score
                }
                
                # Store client info
                self.clients[client_id] = {
                    'hostname': request.hostname,
                    'ip_address': request.ip_address,
                    'specs': specs,
                    'last_seen': time.time(),
                    'assigned_model': None,
                    'group': None
                }
                
                # Reassign models to all clients with new client included
                assignments = self.model_manager.assign_models_to_clients(self.clients)
                
                # Update client assignments
                for cid, model_name in assignments.items():
                    if cid in self.clients:
                        self.clients[cid]['assigned_model'] = model_name
                
                assigned_model = assignments.get(client_id, "llama3.2:3b")  # fallback
                model_info = self.model_manager.get_model_info(assigned_model)
                
                logger.info(f"✅ Client registered: {client_id}")
                logger.info(f"   Performance Score: {specs['performance_score']}")
                logger.info(f"   Assigned Model: {assigned_model}")
                logger.info(f"   Total Clients: {len(self.clients)}")
                
                # Log current assignment summary
                if len(self.clients) > 1:
                    logger.info("\n" + self.model_manager.get_assignment_summary())
                
                # Prepare model info for response
                model_pb = load_balancer_pb2.ModelInfo()
                if model_info:
                    model_pb.name = model_info.name
                    model_pb.parameters = model_info.parameters
                    model_pb.size_gb = model_info.size_gb
                    model_pb.complexity_score = model_info.complexity_score
                    model_pb.supports_vision = model_info.supports_vision
                
                return load_balancer_pb2.RegistrationResponse(
                    success=True,
                    message=f"Registered successfully. Smart assignment: {assigned_model}",
                    assigned_model=assigned_model,
                    model_info=model_pb,
                    total_clients=len(self.clients),
                    client_group=1  # Will be enhanced later
                )
                
        except Exception as e:
            logger.error(f"Error registering client: {e}")
            return load_balancer_pb2.RegistrationResponse(
                success=False,
                message=f"Registration failed: {str(e)}",
                assigned_model="",
                total_clients=len(self.clients),
                client_group=0
            )
    
    def GetAvailableModels(self, request, context):
        """Get list of available models"""
        try:
            models = []
            for model in self.model_manager.available_models:
                model_pb = load_balancer_pb2.ModelInfo(
                    name=model.name,
                    parameters=model.parameters,
                    size_gb=model.size_gb,
                    complexity_score=model.complexity_score,
                    supports_vision=model.supports_vision
                )
                models.append(model_pb)
            
            return load_balancer_pb2.AvailableModelsResponse(
                models=models,
                total_models=len(models)
            )
            
        except Exception as e:
            logger.error(f"Error getting available models: {e}")
            return load_balancer_pb2.AvailableModelsResponse(
                models=[],
                total_models=0
            )
    
    def ReassignModels(self, request, context):
        """Reassign models to all clients (for dynamic rebalancing)"""
        try:
            with self._lock:
                if not self.clients:
                    return load_balancer_pb2.ReassignmentResponse(
                        success=False,
                        message="No clients connected",
                        new_assignments=[]
                    )
                
                # Rediscover models
                self.model_manager.discover_available_models()
                
                # Reassign models
                assignments = self.model_manager.assign_models_to_clients(self.clients)
                
                # Update client assignments
                for client_id, model_name in assignments.items():
                    if client_id in self.clients:
                        self.clients[client_id]['assigned_model'] = model_name
                
                # Prepare response
                new_assignments = []
                for client_id, model_name in assignments.items():
                    assignment = load_balancer_pb2.ClientAssignment(
                        client_id=client_id,
                        assigned_model=model_name,
                        group_number=1  # Will be enhanced
                    )
                    new_assignments.append(assignment)
                
                logger.info("🔄 Models reassigned to all clients")
                logger.info("\n" + self.model_manager.get_assignment_summary())
                
                return load_balancer_pb2.ReassignmentResponse(
                    success=True,
                    message=f"Successfully reassigned models to {len(assignments)} clients",
                    new_assignments=new_assignments
                )
                
        except Exception as e:
            logger.error(f"Error reassigning models: {e}")
            return load_balancer_pb2.ReassignmentResponse(
                success=False,
                message=f"Reassignment failed: {str(e)}",
                new_assignments=[]
            )
    
    def ProcessAIRequest(self, request, context):
        """Process AI request (not used in this flow)"""
        return load_balancer_pb2.AIResponse(
            request_id=request.request_id,
            success=False,
            response_text="This method should not be called on server",
            processing_time=0.0,
            client_id="server",
            model_used="none",
            timestamp=int(time.time())
        )
    
    def ProcessRequest(self, request, context):
        """Process distributed AI request across all clients"""
        try:
            prompt = request.prompt
            images = list(request.images) if request.images else []
            response_text = self.process_distributed_query(prompt, images)
            
            return load_balancer_pb2.AIResponse(
                request_id=request.request_id,
                success=True,
                response_text=response_text,
                processing_time=0.0,
                client_id="server",
                model_used="distributed",
                timestamp=int(time.time())
            )
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return load_balancer_pb2.AIResponse(
                request_id=request.request_id,
                success=False,
                response_text=f"Error: {str(e)}",
                processing_time=0.0,
                client_id="server",
                model_used="none",
                timestamp=int(time.time())
            )
    
    def HealthCheck(self, request, context):
        """Health check endpoint"""
        active_models = len(set(client['assigned_model'] for client in self.clients.values() 
                               if client['assigned_model']))
        
        return load_balancer_pb2.HealthResponse(
            healthy=True,
            message=f"Server healthy. {len(self.clients)} clients, {active_models} active models.",
            connected_clients=len(self.clients),
            active_models=active_models
        )
    
    def process_distributed_query(self, prompt: str, images: List[str] = None) -> str:
        """Process a query across all connected clients with smart load balancing"""
        if not self.clients:
            return "❌ No clients connected. Please connect clients first."
        
        if images is None:
            images = []
        
        logger.info(f"🔄 Processing query: '{prompt}'")
        logger.info(f"📊 Smart distribution to {len(self.clients)} clients")
        if images:
            logger.info(f"🖼️  Processing with {len(images)} images")
        
        # Show smart assignments
        model_groups = {}
        for client_id, client_info in self.clients.items():
            model = client_info['assigned_model']
            if model not in model_groups:
                model_groups[model] = []
            model_groups[model].append((client_id, client_info['specs']['performance_score']))
        
        for model, clients in model_groups.items():
            model_info = self.model_manager.get_model_info(model)
            params = self._format_parameters(model_info.parameters) if model_info else "Unknown"
            logger.info(f"   🤖 {model} ({params}): {len(clients)} clients")
            for client_id, score in clients:
                logger.info(f"      • {client_id} (score: {score})")
        
        responses = []
        request_id = str(uuid.uuid4())
        
        # Send requests to all clients asynchronously and track progress
        client_threads = []
        responses_lock = threading.Lock()
        
        def process_client_request(client_id, client_info):
            try:
                client_address = f"{client_info['ip_address']}:50052"
                channel = grpc.insecure_channel(client_address)
                stub = load_balancer_pb2_grpc.LoadBalancerStub(channel)
                
                # Check if model supports vision
                model_info = self.model_manager.get_model_info(client_info['assigned_model'])
                supports_vision = model_info.supports_vision if model_info else False
                
                # Only send images to vision-capable models
                client_images = images if (supports_vision and images) else []
                
                ai_request = load_balancer_pb2.AIRequest(
                    request_id=request_id,
                    prompt=prompt,
                    assigned_model=client_info['assigned_model'],
                    timestamp=int(time.time()),
                    images=client_images
                )
                
                if client_images:
                    logger.info(f"📤 Sending to {client_id} ({client_info['assigned_model']}) with {len(client_images)} images...")
                else:
                    logger.info(f"📤 Sending to {client_id} ({client_info['assigned_model']})...")
                
                # Send request asynchronously (no timeout)
                response = stub.ProcessAIRequest(ai_request)
                
                if response.success:
                    logger.info(f"✅ Response from {client_id} ({response.processing_time:.1f}s)")
                    with responses_lock:
                        responses.append({
                            'client_id': client_id,
                            'model': client_info['assigned_model'],
                            'response': response.response_text,
                            'processing_time': response.processing_time,
                            'performance_score': client_info['specs']['performance_score']
                        })
                else:
                    logger.warning(f"❌ Failed response from {client_id}")
                
                channel.close()
                
            except Exception as e:
                logger.error(f"❌ Error communicating with {client_id}: {e}")
        
        # Start all client requests in parallel
        for client_id, client_info in self.clients.items():
            thread = threading.Thread(
                target=process_client_request,
                args=(client_id, client_info),
                name=f"Client-{client_id}"
            )
            thread.start()
            client_threads.append((thread, client_id, client_info))
        
        # Monitor progress and wait for completion
        self._monitor_client_progress(client_threads, request_id, responses, responses_lock)
        
        if not responses:
            return "❌ No successful responses from clients."
        
        # Create intelligent summary
        summary = self._create_intelligent_summary(responses)
        return summary
    
    def _create_intelligent_summary(self, responses: List[Dict]) -> str:
        """Create an intelligent summary using the best available method"""
        try:
            # Sort responses by model complexity (best model first)
            sorted_responses = sorted(responses, key=lambda x: x['performance_score'], reverse=True)
            best_client = sorted_responses[0]
            
            # Prepare summary prompt
            summary_prompt = "Analyze and synthesize the following AI responses into a comprehensive, unified answer:\n\n"
            
            for i, resp in enumerate(responses, 1):
                model_info = self.model_manager.get_model_info(resp['model'])
                params = self._format_parameters(model_info.parameters) if model_info else "Unknown"
                summary_prompt += f"Response {i} (Model: {resp['model']} - {params}):\n{resp['response']}\n\n"
            
            summary_prompt += ("Create a unified response that combines the best insights from all models. "
                             "Focus on accuracy, completeness, and clarity.")
            
            # Try local Ollama first
            try:
                logger.info("🤖 Creating intelligent summary using local Ollama...")
                
                # Use the best available model for summarization
                best_local_model = self._get_best_local_model()
                
                logger.info(f"🤖 Using {best_local_model} for summarization (no timeout)")
                result = subprocess.run([
                    'ollama', 'run', best_local_model, summary_prompt
                ], capture_output=True, text=True, encoding='utf-8', errors='ignore')
                
                if result.returncode == 0 and result.stdout.strip():
                    summary = result.stdout.strip()
                    logger.info("✅ Intelligent summary created successfully")
                    return self._format_final_response(responses, summary, "Local Ollama")
                
            except Exception as e:
                logger.warning(f"Local Ollama summarization failed: {e}")
            
            # Fallback: use the best client's response
            logger.info(f"📋 Using best client response as summary ({best_client['client_id']})")
            return self._format_final_response(responses, best_client['response'], "Best Client")
            
        except Exception as e:
            logger.error(f"Error creating intelligent summary: {e}")
            return self._format_final_response(responses, "Summary generation failed.", "Error")
    
    def _get_best_local_model(self) -> str:
        """Get the best available local model for summarization"""
        # Use gemma3:1b for fast summarization
        summarization_model = "gemma3:1b"
        
        # Check if the model exists in available models
        for model in self.model_manager.available_models:
            if model.name == summarization_model:
                return summarization_model
        
        # Fallback to the most complex model available
        if self.model_manager.available_models:
            best_model = max(self.model_manager.available_models, key=lambda x: x.complexity_score)
            return best_model.name
        
        return "gemma3:1b"  # final fallback
    
    def _format_final_response(self, responses: List[Dict], summary: str, summary_method: str) -> str:
        """Format the final response with detailed information in a professional structure"""
        
        # Main answer first (most important)
        result = f"{summary}\n\n"
        
        # Processing metadata in a clean, collapsible format
        result += f"\n{'='*80}\n"
        result += f"PROCESSING_DETAILS_START\n"
        result += f"{'='*80}\n\n"
        
        # Group by model
        model_groups = {}
        for resp in responses:
            model = resp['model']
            if model not in model_groups:
                model_groups[model] = []
            model_groups[model].append(resp)
        
        # Model distribution table
        result += f"📊 System Performance\n\n"
        result += f"Models Used: {len(set(r['model'] for r in responses))}\n"
        result += f"Total Clients: {len(responses)}\n"
        result += f"Summary Method: {summary_method}\n\n"
        
        result += f"🤖 Model Performance:\n\n"
        for model, model_responses in model_groups.items():
            model_info = self.model_manager.get_model_info(model)
            params = self._format_parameters(model_info.parameters) if model_info else "Unknown"
            avg_time = sum(r['processing_time'] for r in model_responses) / len(model_responses)
            
            result += f"  • {model} ({params})\n"
            result += f"    Clients: {len(model_responses)} | Avg Time: {avg_time:.1f}s\n"
            for resp in model_responses:
                result += f"    └─ {resp['client_id']}: {resp['processing_time']:.1f}s\n"
            result += f"\n"
        
        total_time = sum(resp['processing_time'] for resp in responses)
        result += f"⏱️  Total Processing: {total_time:.1f}s | Per Client: {total_time/len(responses):.1f}s\n\n"
        
        result += f"{'='*80}\n"
        result += f"✅ Distributed AI processing completed successfully\n"
        
        return result
    
    def _monitor_client_progress(self, client_threads, request_id, responses, responses_lock):
        """Monitor client progress and wait for completion"""
        completed_clients = set()
        start_time = time.time()
        
        while len(completed_clients) < len(client_threads):
            time.sleep(2)  # Check every 2 seconds
            
            for thread, client_id, client_info in client_threads:
                if client_id in completed_clients:
                    continue
                
                if not thread.is_alive():
                    completed_clients.add(client_id)
                    continue
                
                # Check client progress
                try:
                    client_address = f"{client_info['ip_address']}:50052"
                    channel = grpc.insecure_channel(client_address)
                    stub = load_balancer_pb2_grpc.LoadBalancerStub(channel)
                    
                    status_request = load_balancer_pb2.StatusRequest(
                        request_id=request_id,
                        client_id=client_id
                    )
                    
                    status_response = stub.GetProcessingStatus(status_request, timeout=5)
                    
                    if status_response.status == load_balancer_pb2.PROCESSING:
                        elapsed = time.time() - start_time
                        logger.info(f"🔄 {client_id}: {status_response.progress_percentage:.1f}% - "
                                  f"{status_response.current_step} (elapsed: {elapsed:.1f}s)")
                        
                        if status_response.estimated_remaining_seconds > 0:
                            logger.info(f"   ⏱️  Estimated remaining: {status_response.estimated_remaining_seconds}s")
                    
                    elif status_response.status == load_balancer_pb2.COMPLETED:
                        completed_clients.add(client_id)
                        logger.info(f"✅ {client_id}: Processing completed")
                    
                    elif status_response.status == load_balancer_pb2.ERROR:
                        completed_clients.add(client_id)
                        logger.error(f"❌ {client_id}: Processing failed - {status_response.current_step}")
                    
                    channel.close()
                    
                except Exception as e:
                    # If we can't get status, assume client is still working
                    elapsed = time.time() - start_time
                    logger.info(f"🔄 {client_id}: Processing... (elapsed: {elapsed:.1f}s)")
        
        # Wait for all threads to complete
        for thread, client_id, client_info in client_threads:
            thread.join(timeout=5)  # Give a small timeout for cleanup
        
        logger.info(f"🎯 All clients completed processing in {time.time() - start_time:.1f}s")
    
    def _format_parameters(self, parameters: int) -> str:
        """Format parameter count in human-readable form"""
        if parameters >= 1_000_000_000:
            return f"{parameters // 1_000_000_000}B"
        elif parameters >= 1_000_000:
            return f"{parameters // 1_000_000}M"
        else:
            return f"{parameters}"

def main():
    """Main server function"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=20))
    load_balancer_service = SmartLoadBalancerServer()
    
    load_balancer_pb2_grpc.add_LoadBalancerServicer_to_server(
        load_balancer_service, server
    )
    
    listen_addr = '[::]:50051'
    server.add_insecure_port(listen_addr)
    server.start()
    
    logger.info(f"🌐 Smart server listening on {listen_addr}")
    logger.info("💡 Features: Auto model discovery, intelligent assignment, performance grouping")
    logger.info("📱 Clients should connect to this server's IP on port 50051")
    
    try:
        # Interactive prompt loop
        while True:
            try:
                print("\n" + "="*60)
                print("🤖 SMART AI LOAD BALANCER v3.0")
                print("Commands: 'reassign' to rebalance, 'stats' for info, 'quit' to exit")
                prompt = input("Enter your prompt: ").strip()
                
                if prompt.lower() in ['quit', 'exit', 'q']:
                    break
                elif prompt.lower() == 'reassign':
                    # Trigger model reassignment
                    load_balancer_service.model_manager.discover_available_models()
                    assignments = load_balancer_service.model_manager.assign_models_to_clients(
                        load_balancer_service.clients
                    )
                    for client_id, model_name in assignments.items():
                        if client_id in load_balancer_service.clients:
                            load_balancer_service.clients[client_id]['assigned_model'] = model_name
                    
                    print("🔄 Models reassigned!")
                    print(load_balancer_service.model_manager.get_assignment_summary())
                    continue
                elif prompt.lower() == 'stats':
                    stats = load_balancer_service.model_manager.get_stats()
                    print(f"📊 Server Stats:")
                    print(f"   Connected clients: {len(load_balancer_service.clients)}")
                    print(f"   Available models: {stats['total_models']}")
                    print(f"   Active assignments: {stats['total_assignments']}")
                    print("\n" + load_balancer_service.model_manager.get_assignment_summary())
                    continue
                elif not prompt:
                    continue
                
                # Process the query
                result = load_balancer_service.process_distributed_query(prompt)
                print(f"\n{result}\n")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Error processing prompt: {e}")
    
    finally:
        logger.info("🛑 Shutting down smart server...")
        server.stop(0)

if __name__ == '__main__':
    main()