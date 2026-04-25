"""
챗봇 상태 관리
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from .node import WorkflowNode, ExecutionStatus


@dataclass
class ChatbotState:
    """챗봇 전체 상태"""
    session_id: str
    user_message: str
    response: Optional[str] = None
    provider: str = "gemini"
    nodes: List[WorkflowNode] = field(default_factory=list)
    history: List[Dict[str, str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def add_node(self, node: WorkflowNode) -> None:
        """노드 추가"""
        self.nodes.append(node)
        self.updated_at = datetime.now().isoformat()
    
    def update_node(self, node_id: str, status: ExecutionStatus, 
                   output_data: Dict[str, Any] = None, 
                   error_message: str = None) -> None:
        """노드 상태 업데이트"""
        for node in self.nodes:
            if node.id == node_id:
                node.status = status
                if output_data:
                    node.output_data = output_data
                if error_message:
                    node.error_message = error_message
                node.timestamp = datetime.now().isoformat()
                self.updated_at = datetime.now().isoformat()
                break
    
    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            'session_id': self.session_id,
            'user_message': self.user_message,
            'response': self.response,
            'provider': self.provider,
            'nodes': [node.to_dict() for node in self.nodes],
            'history': self.history,
            'metadata': self.metadata,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """워크플로우 요약 조회"""
        total_nodes = len(self.nodes)
        success_nodes = len([n for n in self.nodes if n.status == ExecutionStatus.SUCCESS])
        error_nodes = len([n for n in self.nodes if n.status == ExecutionStatus.ERROR])
        running_nodes = len([n for n in self.nodes if n.status == ExecutionStatus.RUNNING])
        
        return {
            'total_nodes': total_nodes,
            'completed_nodes': success_nodes,
            'error_nodes': error_nodes,
            'running_nodes': running_nodes,
            'completion_rate': f"{(success_nodes / total_nodes * 100):.1f}%" if total_nodes > 0 else "0%"
        }
