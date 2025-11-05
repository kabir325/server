#!/usr/bin/env python3
"""
Smart Model Manager v3.0
Automatically discovers available models and manages intelligent assignment
"""

import subprocess
import logging
import re
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import random

logger = logging.getLogger(__name__)

@dataclass
class ModelInfo:
    """Information about an available model"""
    name: str
    parameters: int  # Number of parameters (e.g., 1B = 1000000000)
    size_gb: float   # Model size in GB
    complexity_score: int  # 1-10 scale for computational requirements
    
    def __post_init__(self):
        """Calculate complexity score based on parameters"""
        if self.complexity_score == 0:  # Auto-calculate if not provided
            if self.parameters >= 70_000_000_000:  # 70B+
                self.complexity_score = 10
            elif self.parameters >= 30_000_000_000:  # 30B+
                self.complexity_score = 9
            elif self.parameters >= 13_000_000_000:  # 13B+
                self.complexity_score = 8
            elif self.parameters >= 8_000_000_000:   # 8B+
                self.complexity_score = 7
            elif self.parameters >= 7_000_000_000:   # 7B+
                self.complexity_score = 6
            elif self.parameters >= 3_000_000_000:   # 3B+
                self.complexity_score = 5
            elif self.parameters >= 1_000_000_000:   # 1B+
                self.complexity_score = 4
            elif self.parameters >= 500_000_000:     # 500M+
                self.complexity_score = 3
            elif self.parameters >= 100_000_000:     # 100M+
                self.complexity_score = 2
            else:
                self.complexity_score = 1

class SmartModelManager:
    """Intelligent model discovery and assignment manager"""
    
    def __init__(self):
        self.available_models: List[ModelInfo] = []
        self.model_assignments: Dict[str, str] = {}  # client_id -> model_name
        self.client_groups: List[List[str]] = []     # Groups of client_ids
        
        # Known model patterns for automatic detection
        self.known_models = {
            # Llama models
            r'llama3\.2:(\d+)b': lambda m: int(m.group(1)) * 1_000_000_000,
            r'llama3\.1:(\d+)b': lambda m: int(m.group(1)) * 1_000_000_000,
            r'llama3:(\d+)b': lambda m: int(m.group(1)) * 1_000_000_000,
            r'llama2:(\d+)b': lambda m: int(m.group(1)) * 1_000_000_000,
            
            # Mistral models
            r'mistral:(\d+)b': lambda m: int(m.group(1)) * 1_000_000_000,
            r'mixtral:(\d+)x(\d+)b': lambda m: int(m.group(1)) * int(m.group(2)) * 1_000_000_000,
            
            # CodeLlama models
            r'codellama:(\d+)b': lambda m: int(m.group(1)) * 1_000_000_000,
            
            # Gemma models
            r'gemma:(\d+)b': lambda m: int(m.group(1)) * 1_000_000_000,
            
            # Phi models
            r'phi3:(\d+)b': lambda m: int(m.group(1)) * 1_000_000_000,
            
            # Qwen models
            r'qwen2:(\d+)b': lambda m: int(m.group(1)) * 1_000_000_000,
        }
        
        self.discover_available_models()
    
    def discover_available_models(self) -> None:
        """Automatically discover available Ollama models"""
        try:
            logger.info("🔍 Discovering available models...")
            
            # Get list of installed Ollama models
            result = subprocess.run(['ollama', 'list'], 
                                  capture_output=True, text=True, timeout=10, encoding='utf-8', errors='ignore')
            
            if result.returncode != 0:
                logger.warning("Could not get Ollama model list. Using default models.")
                self._use_default_models()
                return
            
            models_found = []
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            
            for line in lines:
                if not line.strip():
                    continue
                
                parts = line.split()
                if len(parts) >= 1:
                    model_name = parts[0]
                    model_info = self._parse_model_info(model_name)
                    if model_info:
                        models_found.append(model_info)
            
            if models_found:
                self.available_models = sorted(models_found, key=lambda x: x.parameters)
                logger.info(f"✅ Found {len(self.available_models)} models:")
                for model in self.available_models:
                    logger.info(f"   {model.name}: {self._format_parameters(model.parameters)} "
                              f"(complexity: {model.complexity_score}/10)")
            else:
                logger.warning("No compatible models found. Using defaults.")
                self._use_default_models()
                
        except Exception as e:
            logger.error(f"Error discovering models: {e}")
            self._use_default_models()
    
    def _parse_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """Parse model name to extract parameter information"""
        try:
            # Try to match against known patterns
            for pattern, param_extractor in self.known_models.items():
                match = re.search(pattern, model_name.lower())
                if match:
                    parameters = param_extractor(match)
                    size_gb = self._estimate_model_size(parameters)
                    
                    return ModelInfo(
                        name=model_name,
                        parameters=parameters,
                        size_gb=size_gb,
                        complexity_score=0  # Will be auto-calculated
                    )
            
            # If no pattern matches, try to extract numbers
            numbers = re.findall(r'(\d+)b', model_name.lower())
            if numbers:
                parameters = int(numbers[0]) * 1_000_000_000
                size_gb = self._estimate_model_size(parameters)
                
                return ModelInfo(
                    name=model_name,
                    parameters=parameters,
                    size_gb=size_gb,
                    complexity_score=0
                )
            
            logger.warning(f"Could not parse model: {model_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error parsing model {model_name}: {e}")
            return None
    
    def _estimate_model_size(self, parameters: int) -> float:
        """Estimate model size in GB based on parameters"""
        # Rough estimation: 1B parameters ≈ 2GB (16-bit precision)
        return round((parameters / 1_000_000_000) * 2.0, 1)
    
    def _use_default_models(self) -> None:
        """Use default model set if discovery fails"""
        self.available_models = [
            ModelInfo("llama3.2:1b", 1_000_000_000, 2.0, 0),
            ModelInfo("llama3.2:3b", 3_000_000_000, 6.0, 0),
            ModelInfo("llama3.1:8b", 8_000_000_000, 16.0, 0),  # Updated to 3.1
        ]
        logger.info("Using default model set")
    
    def assign_models_to_clients(self, clients: Dict[str, Dict]) -> Dict[str, str]:
        """
        Intelligently assign models to clients using performance-based grouping
        
        Args:
            clients: Dict of client_id -> client_info (with performance_score)
            
        Returns:
            Dict of client_id -> assigned_model_name
        """
        if not clients:
            return {}
        
        if not self.available_models:
            logger.error("No models available for assignment")
            return {}
        
        logger.info(f"🎯 Assigning models to {len(clients)} clients using {len(self.available_models)} models")
        
        # Sort clients by performance score (descending)
        sorted_clients = sorted(clients.items(), 
                              key=lambda x: x[1]['specs']['performance_score'], 
                              reverse=True)
        
        # Create performance-based groups
        num_models = len(self.available_models)
        groups = self._create_performance_groups(sorted_clients, num_models)
        
        # Assign models to groups (best model to best group)
        assignments = {}
        sorted_models = sorted(self.available_models, key=lambda x: x.complexity_score, reverse=True)
        
        for group_idx, client_group in enumerate(groups):
            if group_idx < len(sorted_models):
                assigned_model = sorted_models[group_idx]
                
                # Randomly select one client from the group to get this model
                selected_client = random.choice(client_group)
                assignments[selected_client] = assigned_model.name
                
                logger.info(f"📊 Group {group_idx + 1}: {assigned_model.name} "
                          f"({self._format_parameters(assigned_model.parameters)}) "
                          f"→ {selected_client} (from {len(client_group)} clients)")
        
        # Assign remaining clients to available models (round-robin)
        assigned_clients = set(assignments.keys())
        remaining_clients = [cid for cid, _ in sorted_clients if cid not in assigned_clients]
        
        if remaining_clients:
            for i, client_id in enumerate(remaining_clients):
                model_idx = i % len(self.available_models)
                assignments[client_id] = self.available_models[model_idx].name
        
        self.model_assignments = assignments
        return assignments
    
    def _create_performance_groups(self, sorted_clients: List[Tuple], num_groups: int) -> List[List[str]]:
        """Create performance-based groups of clients"""
        if num_groups <= 0 or not sorted_clients:
            return []
        
        total_clients = len(sorted_clients)
        
        if total_clients <= num_groups:
            # Each client gets their own group
            return [[client_id] for client_id, _ in sorted_clients]
        
        # Calculate group sizes
        base_size = total_clients // num_groups
        extra_clients = total_clients % num_groups
        
        groups = []
        start_idx = 0
        
        for group_idx in range(num_groups):
            # First few groups get one extra client if there are remainders
            group_size = base_size + (1 if group_idx < extra_clients else 0)
            end_idx = start_idx + group_size
            
            group_clients = [client_id for client_id, _ in sorted_clients[start_idx:end_idx]]
            groups.append(group_clients)
            
            start_idx = end_idx
        
        return groups
    
    def get_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """Get information about a specific model"""
        for model in self.available_models:
            if model.name == model_name:
                return model
        return None
    
    def get_assignment_summary(self) -> str:
        """Get a formatted summary of current assignments"""
        if not self.model_assignments:
            return "No model assignments yet."
        
        summary = "📊 MODEL ASSIGNMENTS:\n"
        summary += "=" * 50 + "\n"
        
        # Group by model
        model_groups = {}
        for client_id, model_name in self.model_assignments.items():
            if model_name not in model_groups:
                model_groups[model_name] = []
            model_groups[model_name].append(client_id)
        
        for model_name, client_list in model_groups.items():
            model_info = self.get_model_info(model_name)
            if model_info:
                summary += f"\n🤖 {model_name} ({self._format_parameters(model_info.parameters)}):\n"
                for client_id in client_list:
                    summary += f"   • {client_id}\n"
        
        return summary
    
    def _format_parameters(self, parameters: int) -> str:
        """Format parameter count in human-readable form"""
        if parameters >= 1_000_000_000:
            return f"{parameters // 1_000_000_000}B"
        elif parameters >= 1_000_000:
            return f"{parameters // 1_000_000}M"
        else:
            return f"{parameters}"
    
    def add_custom_model(self, name: str, parameters: int, size_gb: float = None) -> None:
        """Add a custom model to the available models"""
        if size_gb is None:
            size_gb = self._estimate_model_size(parameters)
        
        model_info = ModelInfo(name, parameters, size_gb, 0)
        self.available_models.append(model_info)
        self.available_models.sort(key=lambda x: x.parameters)
        
        logger.info(f"➕ Added custom model: {name} ({self._format_parameters(parameters)})")
    
    def get_stats(self) -> Dict:
        """Get statistics about the model manager"""
        return {
            'total_models': len(self.available_models),
            'total_assignments': len(self.model_assignments),
            'models': [
                {
                    'name': model.name,
                    'parameters': self._format_parameters(model.parameters),
                    'complexity': model.complexity_score,
                    'size_gb': model.size_gb
                }
                for model in self.available_models
            ]
        }

if __name__ == "__main__":
    # Test the model manager
    logging.basicConfig(level=logging.INFO)
    
    manager = SmartModelManager()
    
    # Test with sample clients
    sample_clients = {
        'client-1': {'specs': {'performance_score': 95.0}},
        'client-2': {'specs': {'performance_score': 85.0}},
        'client-3': {'specs': {'performance_score': 75.0}},
        'client-4': {'specs': {'performance_score': 65.0}},
        'client-5': {'specs': {'performance_score': 55.0}},
        'client-6': {'specs': {'performance_score': 45.0}},
        'client-7': {'specs': {'performance_score': 35.0}},
    }
    
    assignments = manager.assign_models_to_clients(sample_clients)
    print(manager.get_assignment_summary())
    print(f"\nStats: {manager.get_stats()}")