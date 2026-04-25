"""
워크플로우 추적 및 시각화
"""
from typing import Dict, Optional

from .node import ExecutionStatus
from .state import ChatbotState


class WorkflowTracker:
    """워크플로우 추적 및 시각화"""
    
    def __init__(self):
        self.states: Dict[str, ChatbotState] = {}
    
    def create_state(self, session_id: str, user_message: str, provider: str = "gemini") -> ChatbotState:
        """새로운 상태 생성"""
        state = ChatbotState(
            session_id=session_id,
            user_message=user_message,
            provider=provider
        )
        self.states[session_id] = state
        return state
    
    def get_state(self, session_id: str) -> Optional[ChatbotState]:
        """상태 조회"""
        return self.states.get(session_id)
    
    def generate_workflow_mermaid(self, session_id: str) -> str:
        """Mermaid 다이어그램 생성 (UI에서 시각화용)"""
        state = self.get_state(session_id)
        if not state:
            return ""
        
        mermaid_lines = ["graph LR"]
        
        # 노드 정의
        for node in state.nodes:
            # 상태별 색상
            color_map = {
                ExecutionStatus.SUCCESS: "#90EE90",
                ExecutionStatus.ERROR: "#FF6B6B",
                ExecutionStatus.RUNNING: "#FFA500",
                ExecutionStatus.PENDING: "#D3D3D3",
                ExecutionStatus.SKIPPED: "#87CEEB",
            }
            
            color = color_map.get(node.status, "#D3D3D3")
            status_symbol = {
                ExecutionStatus.SUCCESS: "✓",
                ExecutionStatus.ERROR: "✗",
                ExecutionStatus.RUNNING: "▶",
                ExecutionStatus.PENDING: "○",
                ExecutionStatus.SKIPPED: "-",
            }.get(node.status, "")
            
            label = f"{node.name} {status_symbol}"
            mermaid_lines.append(
                f"{node.id}[\"{label}\"] style {node.id} fill:{color}"
            )
        
        # 엣지 연결
        for i, node in enumerate(state.nodes[:-1]):
            next_node = state.nodes[i + 1]
            mermaid_lines.append(f"{node.id} --> {next_node.id}")
        
        return "\n".join(mermaid_lines)
    
    def generate_workflow_json(self, session_id: str) -> dict:
        """JSON 형식의 워크플로우 데이터"""
        state = self.get_state(session_id)
        if not state:
            return {}
        
        return {
            'state': state.to_dict(),
            'summary': state.get_workflow_summary(),
            'nodes': [node.to_dict() for node in state.nodes]
        }
    
    def generate_html_timeline(self, session_id: str) -> str:
        """HTML 타임라인 생성 (UI 표시용)"""
        state = self.get_state(session_id)
        if not state:
            return ""
        
        html_parts = [
            '<div style="max-height: 400px; overflow-y: auto; padding: 10px;">',
            '<div style="margin-bottom: 20px;"><h3>📊 워크플로우 진행상황</h3>'
        ]
        
        # 요약 정보
        summary = state.get_workflow_summary()
        html_parts.append(f"""
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 10px; margin-bottom: 20px;">
            <div style="background: #E8F5E9; padding: 10px; border-radius: 4px;">
                <strong>총 노드:</strong> {summary['total_nodes']}
            </div>
            <div style="background: #C8E6C9; padding: 10px; border-radius: 4px;">
                <strong>✓ 완료:</strong> {summary['completed_nodes']}
            </div>
            <div style="background: #FFCDD2; padding: 10px; border-radius: 4px;">
                <strong>✗ 오류:</strong> {summary['error_nodes']}
            </div>
            <div style="background: #FFE0B2; padding: 10px; border-radius: 4px;">
                <strong>▶ 진행중:</strong> {summary['running_nodes']}
            </div>
        </div>
        """)
        
        # 타임라인
        html_parts.append('<div style="border-left: 3px solid #2196F3; padding-left: 20px;">')
        
        for node in state.nodes:
            status_icon = {
                ExecutionStatus.SUCCESS: "✓",
                ExecutionStatus.ERROR: "✗",
                ExecutionStatus.RUNNING: "▶",
                ExecutionStatus.PENDING: "○",
                ExecutionStatus.SKIPPED: "-",
            }.get(node.status, "?")
            
            status_color = {
                ExecutionStatus.SUCCESS: "#4CAF50",
                ExecutionStatus.ERROR: "#F44336",
                ExecutionStatus.RUNNING: "#FF9800",
                ExecutionStatus.PENDING: "#9E9E9E",
                ExecutionStatus.SKIPPED: "#2196F3",
            }.get(node.status, "#666")
            
            html_parts.append(f"""
            <div style="margin-bottom: 15px; padding: 10px; background: #f5f5f5; border-radius: 4px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="color: {status_color}; font-weight: bold; font-size: 18px;">{status_icon}</span>
                    <div>
                        <strong>{node.name}</strong>
                        <div style="font-size: 12px; color: #666;">
                            {node.description}
                        </div>
                        <div style="font-size: 11px; color: #999; margin-top: 5px;">
                            {node.timestamp}
                        </div>
                    </div>
                </div>
                {f'<div style="margin-top: 8px; color: #F44336; font-size: 12px;">❌ {node.error_message}</div>' if node.error_message else ''}
            </div>
            """)
        
        html_parts.append('</div></div>')
        
        return "\n".join(html_parts)
