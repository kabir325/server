#!/usr/bin/env python3
"""
HTTP Wrapper for Smart Load Balancer Server v4.0
Enhanced with RAG, Chat History, and Image Support
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import grpc
import sys
import os
import logging
import base64
import time
import uuid

# Add the server directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import gRPC definitions
import load_balancer_pb2
import load_balancer_pb2_grpc

# Import managers
from rag_manager import RAGManager
from chat_manager import ChatManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# gRPC server address
GRPC_SERVER_ADDRESS = 'localhost:50051'

# Initialize managers
try:
    rag_manager = RAGManager()
    chat_manager = ChatManager()
    logger.info("✅ RAG and Chat managers initialized")
except Exception as e:
    logger.error(f"❌ Failed to initialize managers: {e}")
    rag_manager = None
    chat_manager = None

def get_grpc_stub():
    """Get a gRPC stub for communicating with the load balancer server"""
    channel = grpc.insecure_channel(GRPC_SERVER_ADDRESS)
    return load_balancer_pb2_grpc.LoadBalancerStub(channel)

@app.route('/')
def home():
    return jsonify({
        'service': 'Smart AI Load Balancer HTTP Wrapper',
        'version': '4.0',
        'status': 'running',
        'features': ['distributed_ai', 'rag', 'chat_history', 'multimodal']
    })

@app.route('/query', methods=['POST'])
def process_query():
    """Process a distributed AI query with RAG and chat history support"""
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        session_id = data.get('session_id')
        use_rag = data.get('use_rag', False)
        images = data.get('images', [])
        
        if not prompt:
            return jsonify({
                'success': False,
                'error': 'Prompt is required'
            }), 400
        
        logger.info(f"📥 Received query (RAG: {use_rag}, Session: {session_id}, Images: {len(images)})")
        
        # Create or get chat session
        if not session_id and chat_manager:
            session_id = chat_manager.create_session(title=prompt[:50] + "...")
        
        # Add user message to chat history
        if session_id and chat_manager:
            chat_manager.add_message(session_id, 'user', prompt, images)
        
        # System prompt for farming assistant - enhanced for vision
        if images:
            # Vision-specific prompt for disease detection
            system_prompt = (
                "You are a highly knowledgeable agricultural expert specializing in crop disease identification. "
                "You are analyzing an image of a Wheat or Maize crop to identify diseases, pests, or health issues.\n\n"
                "IMPORTANT INSTRUCTIONS:\n"
                "1. Carefully examine the image provided\n"
                "2. Identify any visible symptoms such as:\n"
                "   - Leaf discoloration (yellowing, browning, spots)\n"
                "   - Lesions, spots, or patches on leaves/stems\n"
                "   - Wilting, stunted growth, or deformities\n"
                "   - Presence of pests or fungal growth\n"
                "   - Any abnormal patterns or textures\n"
                "3. Based on the symptoms, identify the most likely disease(s) or condition\n"
                "4. Provide the disease name and a brief description\n"
                "5. Suggest immediate treatment or management steps\n"
                "6. Recommend preventive measures for the future\n\n"
                "If the image shows a healthy crop, state that clearly. "
                "If you can see symptoms but cannot definitively identify the disease, describe what you observe "
                "and suggest possible causes based on the visible symptoms.\n\n"
                "Format your response as:\n"
                "**Disease Identified:** [Name or 'Unable to determine']\n"
                "**Symptoms Observed:** [List visible symptoms]\n"
                "**Description:** [Brief explanation]\n"
                "**Treatment:** [Recommended actions]\n"
                "**Prevention:** [Future preventive measures]\n\n"
            )
        else:
            # Standard text-only prompt
            system_prompt = (
                "You are a highly knowledgeable and helpful assistant for farmers. "
                "You specialize in answering questions related to Wheat and Maize crops. "
                "Your goal is to provide accurate, clear, and practical advice on farming practices, "
                "pest control, irrigation, soil nutrition, and disease prevention.\n\n"
                "When answering questions:\n"
                "- Give direct, practical answers that farmers can implement immediately\n"
                "- Use simple language that's easy to understand\n"
                "- Include specific details like quantities, timings, and methods\n"
                "- Be concise but thorough\n"
                "- If you don't know something, say so honestly\n\n"
                "Always respond as a knowledgeable farming expert providing helpful solutions.\n\n"
            )
        
        # Build enhanced prompt with context
        enhanced_prompt = system_prompt
        context_info = []
        
        # Add RAG context if requested
        if use_rag and rag_manager:
            rag_context = rag_manager.create_rag_context(prompt, top_k=3)
            if rag_context:
                enhanced_prompt += rag_context
                context_info.append("RAG context added")
        
        # Add chat history context
        if session_id and chat_manager:
            chat_context = chat_manager.get_conversation_context(session_id, max_messages=5)
            if chat_context:
                enhanced_prompt += chat_context
                context_info.append("Chat history added")
        
        # Add the actual user prompt
        enhanced_prompt += f"\nUser Question: {prompt}"
        
        # Call gRPC server for distributed processing
        try:
            stub = get_grpc_stub()
            
            # Create gRPC request
            request_id = str(uuid.uuid4())
            grpc_request = load_balancer_pb2.AIRequest(
                request_id=request_id,
                prompt=enhanced_prompt,
                assigned_model="",  # Server will distribute to clients
                timestamp=int(time.time()),
                images=images  # Pass images for vision models
            )
            
            logger.info(f"🔄 Sending request {request_id} to gRPC server (with {len(images)} images)...")
            
            # Send request without timeout - use ProcessRequest for distributed processing
            # AI processing can take several minutes depending on model complexity
            grpc_response = stub.ProcessRequest(grpc_request)
            
            if grpc_response.success:
                response_text = grpc_response.response_text
                
                # Add metadata about processing
                metadata = {
                    'client_id': grpc_response.client_id,
                    'model_used': grpc_response.model_used,
                    'processing_time': grpc_response.processing_time,
                    'context_used': context_info,
                    'images_received': len(images),
                    'rag_enabled': use_rag
                }
                
                logger.info(f"✅ Request processed by {grpc_response.client_id} using {grpc_response.model_used} in {grpc_response.processing_time:.2f}s")
            else:
                response_text = f"Error processing request: {grpc_response.response_text}"
                metadata = {
                    'error': True,
                    'context_used': context_info,
                    'images_received': len(images),
                    'rag_enabled': use_rag
                }
                logger.error(f"❌ Request failed: {grpc_response.response_text}")
            
        except grpc.RpcError as e:
            logger.error(f"gRPC error: {e}")
            response_text = f"Load balancer server unavailable. Please ensure:\n"
            response_text += f"1. Server is running on port 50051\n"
            response_text += f"2. At least one client is connected\n\n"
            response_text += f"Error: {str(e)}"
            
            metadata = {
                'error': True,
                'error_type': 'grpc_unavailable',
                'context_used': context_info,
                'images_received': len(images),
                'rag_enabled': use_rag
            }
        
        # Add assistant response to chat history
        if session_id and chat_manager:
            chat_manager.add_message(session_id, 'assistant', response_text)
        
        return jsonify({
            'success': True,
            'response': response_text,
            'session_id': session_id,
            'metadata': {
                'context_used': context_info,
                'images_received': len(images),
                'rag_enabled': use_rag
            }
        })
        
    except Exception as e:
        logger.error(f"Query processing error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Get the current status of the load balancer"""
    try:
        stub = get_grpc_stub()
        
        empty_request = load_balancer_pb2.Empty()
        health_response = stub.HealthCheck(empty_request, timeout=5)
        models_response = stub.GetAvailableModels(empty_request, timeout=5)
        
        available_models = [model.name for model in models_response.models]
        
        # Add RAG and chat stats
        rag_stats = rag_manager.get_stats() if rag_manager else {}
        chat_stats = chat_manager.get_stats() if chat_manager else {}
        
        return jsonify({
            'total_clients': health_response.connected_clients,
            'active_clients': health_response.connected_clients,
            'available_models': available_models,
            'clients': [],
            'healthy': health_response.healthy,
            'message': health_response.message,
            'rag_stats': rag_stats,
            'chat_stats': chat_stats
        })
        
    except grpc.RpcError as e:
        logger.error(f"gRPC error: {e}")
        return jsonify({
            'success': False,
            'error': f'gRPC server not available: {str(e)}',
            'total_clients': 0,
            'active_clients': 0,
            'available_models': [],
            'clients': []
        }), 200
        
    except Exception as e:
        logger.error(f"Status error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# RAG Endpoints
@app.route('/rag/documents', methods=['POST'])
def add_document():
    """Add a document to the RAG store"""
    try:
        if not rag_manager:
            return jsonify({'success': False, 'error': 'RAG not initialized'}), 500
        
        data = request.get_json()
        content = data.get('content')
        title = data.get('title', 'Untitled')
        metadata = data.get('metadata', {})
        
        if not content:
            return jsonify({'success': False, 'error': 'Content is required'}), 400
        
        doc_id = rag_manager.add_document(content, title, metadata)
        
        return jsonify({
            'success': True,
            'doc_id': doc_id,
            'message': 'Document added successfully'
        })
        
    except Exception as e:
        logger.error(f"Error adding document: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/rag/search', methods=['POST'])
def search_documents():
    """Search for relevant documents"""
    try:
        if not rag_manager:
            return jsonify({'success': False, 'error': 'RAG not initialized'}), 500
        
        data = request.get_json()
        query = data.get('query')
        top_k = data.get('top_k', 3)
        
        if not query:
            return jsonify({'success': False, 'error': 'Query is required'}), 400
        
        documents, scores = rag_manager.search_documents(query, top_k)
        
        return jsonify({
            'success': True,
            'documents': documents,
            'scores': scores
        })
        
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/rag/documents/<doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    """Delete a document"""
    try:
        if not rag_manager:
            return jsonify({'success': False, 'error': 'RAG not initialized'}), 500
        
        success = rag_manager.delete_document(doc_id)
        
        return jsonify({
            'success': success,
            'message': 'Document deleted' if success else 'Document not found'
        })
        
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Chat History Endpoints
@app.route('/chat/sessions', methods=['GET'])
def get_chat_sessions():
    """Get all chat sessions"""
    try:
        if not chat_manager:
            return jsonify({'success': False, 'error': 'Chat manager not initialized'}), 500
        
        limit = request.args.get('limit', 50, type=int)
        sessions = chat_manager.get_all_sessions(limit)
        
        return jsonify({
            'success': True,
            'sessions': sessions
        })
        
    except Exception as e:
        logger.error(f"Error getting chat sessions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/chat/sessions', methods=['POST'])
def create_chat_session():
    """Create a new chat session"""
    try:
        if not chat_manager:
            return jsonify({'success': False, 'error': 'Chat manager not initialized'}), 500
        
        data = request.get_json() or {}
        title = data.get('title', 'New Chat')
        
        session_id = chat_manager.create_session(title)
        
        return jsonify({
            'success': True,
            'session_id': session_id
        })
        
    except Exception as e:
        logger.error(f"Error creating chat session: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/chat/sessions/<session_id>', methods=['GET'])
def get_chat_history(session_id):
    """Get chat history for a session"""
    try:
        if not chat_manager:
            return jsonify({'success': False, 'error': 'Chat manager not initialized'}), 500
        
        session = chat_manager.get_session(session_id)
        
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        return jsonify({
            'success': True,
            'session': session
        })
        
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/chat/sessions/<session_id>', methods=['DELETE'])
def delete_chat_session(session_id):
    """Delete a chat session"""
    try:
        if not chat_manager:
            return jsonify({'success': False, 'error': 'Chat manager not initialized'}), 500
        
        success = chat_manager.delete_session(session_id)
        
        return jsonify({
            'success': success,
            'message': 'Session deleted' if success else 'Session not found'
        })
        
    except Exception as e:
        logger.error(f"Error deleting chat session: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/chat/sessions/<session_id>/title', methods=['PUT'])
def update_session_title(session_id):
    """Update session title"""
    try:
        if not chat_manager:
            return jsonify({'success': False, 'error': 'Chat manager not initialized'}), 500
        
        data = request.get_json()
        title = data.get('title')
        
        if not title:
            return jsonify({'success': False, 'error': 'Title is required'}), 400
        
        success = chat_manager.update_session_title(session_id, title)
        
        return jsonify({
            'success': success,
            'message': 'Title updated' if success else 'Session not found'
        })
        
    except Exception as e:
        logger.error(f"Error updating session title: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/reassign', methods=['POST'])
def reassign_models():
    """Trigger model reassignment via gRPC"""
    try:
        stub = get_grpc_stub()
        
        empty_request = load_balancer_pb2.Empty()
        reassign_response = stub.ReassignModels(empty_request, timeout=10)
        
        if reassign_response.success:
            assignments = {}
            for assignment in reassign_response.new_assignments:
                assignments[assignment.client_id] = assignment.assigned_model
            
            return jsonify({
                'success': True,
                'message': reassign_response.message,
                'assignments': assignments
            })
        else:
            return jsonify({
                'success': False,
                'error': reassign_response.message
            }), 400
        
    except grpc.RpcError as e:
        logger.error(f"gRPC error: {e}")
        return jsonify({
            'success': False,
            'error': f'gRPC server not available: {str(e)}'
        }), 500
        
    except Exception as e:
        logger.error(f"Reassignment error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        stub = get_grpc_stub()
        
        empty_request = load_balancer_pb2.Empty()
        health_response = stub.HealthCheck(empty_request, timeout=5)
        
        return jsonify({
            'healthy': health_response.healthy,
            'connected_clients': health_response.connected_clients,
            'active_models': health_response.active_models,
            'message': health_response.message,
            'rag_available': rag_manager is not None,
            'chat_available': chat_manager is not None
        })
        
    except grpc.RpcError as e:
        logger.error(f"gRPC health check error: {e}")
        return jsonify({
            'healthy': False,
            'error': 'gRPC server not available',
            'connected_clients': 0,
            'active_models': 0,
            'rag_available': rag_manager is not None,
            'chat_available': chat_manager is not None
        }), 200
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'healthy': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("="*60)
    print("🚀 Smart Load Balancer HTTP Wrapper v4.0")
    print("="*60)
    print()
    print("📡 HTTP API available on http://localhost:5000")
    print("⚠️  Make sure smart_load_balancer_server.py is running on port 50051")
    print()
    print("New Features:")
    print("  ✨ RAG with ChromaDB")
    print("  ✨ Chat History Management")
    print("  ✨ Multimodal Image Support")
    print()
    print("Endpoints:")
    print("  GET  /          - Service info")
    print("  POST /query     - Process query (with RAG & chat)")
    print("  GET  /status    - Get system status")
    print("  POST /reassign  - Trigger model reassignment")
    print("  GET  /health    - Health check")
    print()
    print("  RAG Endpoints:")
    print("  POST   /rag/documents        - Add document")
    print("  POST   /rag/search           - Search documents")
    print("  DELETE /rag/documents/<id>   - Delete document")
    print()
    print("  Chat Endpoints:")
    print("  GET    /chat/sessions              - List sessions")
    print("  POST   /chat/sessions              - Create session")
    print("  GET    /chat/sessions/<id>         - Get session")
    print("  DELETE /chat/sessions/<id>         - Delete session")
    print("  PUT    /chat/sessions/<id>/title   - Update title")
    print()
    print("="*60)
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
