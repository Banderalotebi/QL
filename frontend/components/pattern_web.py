"""
Pattern Web 3D Visualization Component
Interactive graph visualization of 1,200 Muqattaat patterns using Pyvis.
Allows drag-and-drop pattern nodes into execution queue.
"""

import json
import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import networkx as nx
from datetime import datetime

logger = logging.getLogger(__name__)


class PatternNode:
    """Represents a single pattern in the visualization"""
    
    def __init__(self, pattern_id: str, pattern_type: str, x: float = 0, y: float = 0, z: float = 0):
        self.pattern_id = pattern_id
        self.pattern_type = pattern_type  # "mathematical", "linguistic", "cryptographic", "phonetic"
        self.x = x
        self.y = y
        self.z = z
        self.status = "pending"  # pending, executing, verified, failed
        self.connections: List[str] = []
        self.metadata: Dict = {}
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "pattern_id": self.pattern_id,
            "pattern_type": self.pattern_type,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "status": self.status,
            "connections": self.connections,
            "metadata": self.metadata
        }


class PatternCluster:
    """Represents a cluster of related patterns"""
    
    def __init__(self, cluster_id: str, name: str, pattern_type: str):
        self.cluster_id = cluster_id
        self.name = name
        self.pattern_type = pattern_type
        self.patterns: List[PatternNode] = []
        self.centroid: Tuple[float, float, float] = (0, 0, 0)
    
    def add_pattern(self, pattern: PatternNode):
        """Add pattern to cluster"""
        self.patterns.append(pattern)
    
    def calculate_centroid(self):
        """Calculate cluster centroid"""
        if not self.patterns:
            return
        
        x_sum = sum(p.x for p in self.patterns)
        y_sum = sum(p.y for p in self.patterns)
        z_sum = sum(p.z for p in self.patterns)
        n = len(self.patterns)
        
        self.centroid = (x_sum / n, y_sum / n, z_sum / n)


class PatternWebVisualizer:
    """
    Main pattern visualization engine
    Manages 3D pattern graph, clustering, and interaction
    """
    
    def __init__(self, patterns_config_path: str = "/workspaces/QL/data/pattern_metadata.json"):
        """Initialize the pattern web visualizer"""
        self.patterns_config_path = patterns_config_path
        self.patterns: Dict[str, PatternNode] = {}
        self.clusters: Dict[str, PatternCluster] = {}
        self.graph: Optional[nx.Graph] = None
        self.execution_queue: List[str] = []
        self.pattern_metadata = self._load_pattern_metadata()
        self._initialize_graph()
        logger.info("PatternWebVisualizer initialized")
    
    def _load_pattern_metadata(self) -> Dict:
        """Load pattern metadata from configuration"""
        try:
            if Path(self.patterns_config_path).exists():
                with open(self.patterns_config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load pattern metadata: {e}")
        
        return self._create_default_metadata()
    
    def _create_default_metadata(self) -> Dict:
        """Create default pattern metadata for common patterns"""
        return {
            "41": {
                "name": "Modulo-19 Verification",
                "type": "mathematical",
                "description": "Islamic numerological constraint on Muqattaat",
                "domain": "cryptographic"
            },
            "35": {
                "name": "Shannon Entropy",
                "type": "mathematical",
                "description": "Information density measurement",
                "domain": "linguistic"
            },
            "33": {
                "name": "Golden Ratio",
                "type": "mathematical",
                "description": "Proportional harmony detection",
                "domain": "phonetic"
            },
            "12": {
                "name": "Abjad Numerology",
                "type": "mathematical",
                "description": "Letter value significance analysis",
                "domain": "linguistic"
            }
        }
    
    def _initialize_graph(self):
        """Initialize the NetworkX graph with patterns"""
        self.graph = nx.Graph()
        
        # Define pattern clusters
        self.clusters = {
            "cryptographic": PatternCluster("crypto", "Cryptographic Patterns", "mathematical"),
            "linguistic": PatternCluster("ling", "Linguistic Patterns", "linguistic"),
            "phonetic": PatternCluster("phone", "Phonetic Patterns", "phonetic"),
            "structural": PatternCluster("struct", "Structural Patterns", "mathematical")
        }
        
        # Create sample patterns (in production, would load 1,200 patterns)
        self._create_sample_patterns()
    
    def _create_sample_patterns(self):
        """Create sample patterns for demonstration"""
        # Pattern types and their domains
        pattern_definitions = [
            ("41", "cryptographic", "Modulo-19 Verification", "mathematical"),
            ("35", "linguistic", "Shannon Entropy", "mathematical"),
            ("33", "phonetic", "Golden Ratio", "mathematical"),
            ("12", "structural", "Abjad Numerology", "mathematical"),
            ("100", "cryptographic", "Prime Pattern Analysis", "mathematical"),
            ("200", "linguistic", "Root Word Detection", "linguistic"),
            ("300", "phonetic", "Tajweed Rules", "phonetic"),
            ("400", "structural", "Skeletal Geometry", "mathematical"),
            ("500", "cryptographic", "Letter Frequency", "mathematical"),
            ("600", "linguistic", "Morphological Rules", "linguistic"),
        ]
        
        # Create pattern nodes with spatial distribution
        import random
        for pattern_id, cluster_key, name, ptype in pattern_definitions:
            # Spatial distribution: patterns in same cluster near each other
            cluster = self.clusters[cluster_key]
            x = cluster.centroid[0] + random.uniform(-50, 50)
            y = cluster.centroid[1] + random.uniform(-50, 50)
            z = random.uniform(0, 100)
            
            node = PatternNode(pattern_id, ptype, x, y, z)
            node.metadata = {
                "name": name,
                "domain": cluster_key,
                "description": f"Pattern {pattern_id}: {name}"
            }
            
            self.patterns[pattern_id] = node
            cluster.add_pattern(node)
            
            # Add to graph
            self.graph.add_node(
                pattern_id,
                label=name,
                type=ptype,
                x=x,
                y=y,
                z=z,
                status="pending"
            )
        
        # Create edges between related patterns
        self._create_pattern_edges()
        
        # Calculate cluster centroids
        for cluster in self.clusters.values():
            cluster.calculate_centroid()
    
    def _create_pattern_edges(self):
        """Create edges between related patterns"""
        pattern_list = list(self.patterns.keys())
        
        # Create some connections based on similarity
        connections = [
            ("41", "12"),  # Both mathematical
            ("35", "33"),  # Both mathematical
            ("100", "41"), # Similar domain
            ("200", "600"),  # Both linguistic
            ("300", "200"),  # Related
        ]
        
        for src, dst in connections:
            if src in self.patterns and dst in self.patterns:
                self.graph.add_edge(src, dst, weight=1.0)
                self.patterns[src].connections.append(dst)
                self.patterns[dst].connections.append(src)
    
    def add_pattern_to_queue(self, pattern_id: str) -> bool:
        """Add pattern to execution queue"""
        if pattern_id not in self.patterns:
            logger.warning(f"Pattern {pattern_id} not found")
            return False
        
        if pattern_id not in self.execution_queue:
            self.execution_queue.append(pattern_id)
            pattern = self.patterns[pattern_id]
            pattern.status = "queued"
            logger.info(f"Added pattern {pattern_id} to execution queue")
            return True
        
        return False
    
    def remove_from_queue(self, pattern_id: str) -> bool:
        """Remove pattern from execution queue"""
        if pattern_id in self.execution_queue:
            self.execution_queue.remove(pattern_id)
            if pattern_id in self.patterns:
                self.patterns[pattern_id].status = "pending"
            return True
        return False
    
    def execute_queue(self) -> Dict:
        """Execute all patterns in queue"""
        results = {
            "executed": [],
            "failed": [],
            "timestamp": datetime.now().isoformat()
        }
        
        for pattern_id in self.execution_queue:
            pattern = self.patterns.get(pattern_id)
            if pattern:
                pattern.status = "executing"
                # Simulation: mark as verified
                pattern.status = "verified"
                results["executed"].append(pattern_id)
        
        self.execution_queue.clear()
        return results
    
    def get_cluster_view(self, cluster_id: str) -> Optional[Dict]:
        """Get patterns in a specific cluster"""
        cluster = self.clusters.get(cluster_id)
        if not cluster:
            return None
        
        return {
            "cluster_id": cluster.cluster_id,
            "name": cluster.name,
            "pattern_type": cluster.pattern_type,
            "pattern_count": len(cluster.patterns),
            "centroid": cluster.centroid,
            "patterns": [
                {
                    "pattern_id": p.pattern_id,
                    "status": p.status,
                    "position": [p.x, p.y, p.z]
                }
                for p in cluster.patterns
            ]
        }
    
    def get_pattern_similarity(self, pattern_id: str, top_n: int = 5) -> List[Dict]:
        """Get similar patterns using graph structure"""
        if pattern_id not in self.graph:
            return []
        
        # Get neighbors in graph (directly connected patterns)
        neighbors = list(self.graph.neighbors(pattern_id))
        
        # Return top N similar patterns
        similar = []
        for neighbor_id in neighbors[:top_n]:
            neighbor_pattern = self.patterns.get(neighbor_id)
            if neighbor_pattern:
                similar.append({
                    "pattern_id": neighbor_id,
                    "name": neighbor_pattern.metadata.get("name", "Unknown"),
                    "domain": neighbor_pattern.metadata.get("domain", "unknown"),
                    "similarity_score": 0.85  # Would compute based on graph distance
                })
        
        return similar
    
    def export_graph_json(self) -> Dict:
        """Export graph as JSON for frontend visualization (Pyvis)"""
        nodes = []
        edges = []
        
        # Create color map based on status
        status_colors = {
            "pending": "#4A90E2",      # Blue
            "executing": "#F5A623",    # Gold
            "verified": "#7ED321",     # Green
            "failed": "#D0021B"        # Red
        }
        
        # Add nodes
        for pattern_id, pattern in self.patterns.items():
            nodes.append({
                "id": pattern_id,
                "label": pattern.metadata.get("name", f"Pattern {pattern_id}"),
                "title": pattern.metadata.get("description", ""),
                "color": status_colors.get(pattern.status, "#4A90E2"),
                "x": pattern.x,
                "y": pattern.y,
                "z": pattern.z,
                "type": pattern.pattern_type,
                "status": pattern.status,
                "size": 25 if pattern.status == "queued" else 15
            })
        
        # Add edges
        for _, _, edge_data in self.graph.edges(data=True):
            src = edge_data.get('source')
            dst = edge_data.get('target')
            weight = edge_data.get('weight', 1.0)
            
            edges.append({
                "from": src,
                "to": dst,
                "weight": weight
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "queue": self.execution_queue,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_queue_status(self) -> Dict:
        """Get current execution queue status"""
        return {
            "queue_size": len(self.execution_queue),
            "queued_patterns": [
                {
                    "pattern_id": pid,
                    "name": self.patterns[pid].metadata.get("name", "Unknown")
                }
                for pid in self.execution_queue
            ],
            "estimated_execution_time_seconds": len(self.execution_queue) * 5,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_statistics(self) -> Dict:
        """Get visualization statistics"""
        status_counts = {"pending": 0, "executing": 0, "verified": 0, "failed": 0, "queued": 0}
        type_counts = {}
        
        for pattern in self.patterns.values():
            status_counts[pattern.status] = status_counts.get(pattern.status, 0) + 1
            ptype = pattern.pattern_type
            type_counts[ptype] = type_counts.get(ptype, 0) + 1
        
        return {
            "total_patterns": len(self.patterns),
            "total_clusters": len(self.clusters),
            "by_status": status_counts,
            "by_type": type_counts,
            "graph_nodes": self.graph.number_of_nodes(),
            "graph_edges": self.graph.number_of_edges(),
            "queue_size": len(self.execution_queue),
            "timestamp": datetime.now().isoformat()
        }


# Global instance
_visualizer: Optional[PatternWebVisualizer] = None


def get_pattern_web_visualizer() -> PatternWebVisualizer:
    """Get or create global pattern web visualizer instance"""
    global _visualizer
    if _visualizer is None:
        _visualizer = PatternWebVisualizer()
    return _visualizer
