"""
워크플로우 노드 정의 및 열거형
"""
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class NodeType(Enum):
    """워크플로우 노드 타입"""
    INPUT = "input"
    PROCESS = "process"
    API_CALL = "api_call"
    OUTPUT = "output"
    DECISION = "decision"
    ERROR = "error"


class ExecutionStatus(Enum):
    """실행 상태"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    SKIPPED = "skipped"


@dataclass
class WorkflowNode:
    """워크플로우 노드"""
    id: str
    type: NodeType
    name: str
    description: str = ""
    status: ExecutionStatus = ExecutionStatus.PENDING
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    error_message: Optional[str] = None
    
    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        data = asdict(self)
        data['type'] = self.type.value
        data['status'] = self.status.value
        return data
