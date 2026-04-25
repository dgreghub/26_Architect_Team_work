"""
워크플로우 및 LangGraph 통합 테스트
"""
import pytest
import tempfile
from uuid import uuid4
from chatbot.workflow import (
    WorkflowNode, NodeType, ExecutionStatus, ChatbotState, WorkflowTracker
)


class TestWorkflowNode:
    """워크플로우 노드 테스트"""

    def test_node_creation(self):
        """노드 생성"""
        node = WorkflowNode(
            id="test",
            type=NodeType.INPUT,
            name="테스트",
            description="테스트 노드"
        )
        
        assert node.id == "test"
        assert node.type == NodeType.INPUT
        assert node.status == ExecutionStatus.PENDING

    def test_node_to_dict(self):
        """노드를 딕셔너리로 변환"""
        node = WorkflowNode(
            id="test",
            type=NodeType.PROCESS,
            name="처리"
        )
        
        node_dict = node.to_dict()
        assert node_dict['type'] == 'process'
        assert node_dict['status'] == 'pending'


class TestChatbotState:
    """챗봇 상태 테스트"""

    def test_state_creation(self):
        """상태 생성"""
        state = ChatbotState(
            session_id="session1",
            user_message="안녕하세요"
        )
        
        assert state.session_id == "session1"
        assert state.user_message == "안녕하세요"
        assert len(state.nodes) == 0

    def test_add_node(self):
        """노드 추가"""
        state = ChatbotState(
            session_id="session1",
            user_message="테스트"
        )
        
        node = WorkflowNode(
            id="input",
            type=NodeType.INPUT,
            name="입력"
        )
        
        state.add_node(node)
        assert len(state.nodes) == 1
        assert state.nodes[0].id == "input"

    def test_update_node(self):
        """노드 상태 업데이트"""
        state = ChatbotState(
            session_id="session1",
            user_message="테스트"
        )
        
        node = WorkflowNode(
            id="test",
            type=NodeType.PROCESS,
            name="처리"
        )
        state.add_node(node)
        
        state.update_node(
            "test",
            ExecutionStatus.SUCCESS,
            output_data={"result": "완료"}
        )
        
        assert state.nodes[0].status == ExecutionStatus.SUCCESS
        assert state.nodes[0].output_data == {"result": "완료"}

    def test_workflow_summary(self):
        """워크플로우 요약"""
        state = ChatbotState(
            session_id="session1",
            user_message="테스트"
        )
        
        # 성공한 노드 추가
        node1 = WorkflowNode(
            id="node1",
            type=NodeType.INPUT,
            name="입력",
            status=ExecutionStatus.SUCCESS
        )
        
        # 실패한 노드 추가
        node2 = WorkflowNode(
            id="node2",
            type=NodeType.PROCESS,
            name="처리",
            status=ExecutionStatus.ERROR
        )
        
        state.add_node(node1)
        state.add_node(node2)
        
        summary = state.get_workflow_summary()
        assert summary['total_nodes'] == 2
        assert summary['completed_nodes'] == 1
        assert summary['error_nodes'] == 1


class TestWorkflowTracker:
    """워크플로우 추적 테스트"""

    def test_create_state(self):
        """상태 생성"""
        tracker = WorkflowTracker()
        state = tracker.create_state("session1", "테스트 메시지")
        
        assert state.session_id == "session1"
        assert state.user_message == "테스트 메시지"

    def test_get_state(self):
        """상태 조회"""
        tracker = WorkflowTracker()
        state = tracker.create_state("session1", "메시지")
        
        retrieved = tracker.get_state("session1")
        assert retrieved is not None
        assert retrieved.session_id == "session1"

    def test_generate_workflow_mermaid(self):
        """Mermaid 다이어그램 생성"""
        tracker = WorkflowTracker()
        state = tracker.create_state("session1", "테스트")
        
        node = WorkflowNode(
            id="input",
            type=NodeType.INPUT,
            name="입력",
            status=ExecutionStatus.SUCCESS
        )
        state.add_node(node)
        
        mermaid = tracker.generate_workflow_mermaid("session1")
        assert "graph LR" in mermaid
        assert "input" in mermaid
        assert "✓" in mermaid  # 성공 아이콘

    def test_generate_workflow_json(self):
        """JSON 워크플로우 데이터"""
        tracker = WorkflowTracker()
        state = tracker.create_state("session1", "테스트")
        
        node = WorkflowNode(
            id="test",
            type=NodeType.PROCESS,
            name="처리"
        )
        state.add_node(node)
        
        json_data = tracker.generate_workflow_json("session1")
        assert "state" in json_data
        assert "summary" in json_data
        assert "nodes" in json_data

    def test_generate_html_timeline(self):
        """HTML 타임라인 생성"""
        tracker = WorkflowTracker()
        state = tracker.create_state("session1", "테스트")
        
        node1 = WorkflowNode(
            id="node1",
            type=NodeType.INPUT,
            name="입력",
            status=ExecutionStatus.SUCCESS
        )
        
        node2 = WorkflowNode(
            id="node2",
            type=NodeType.ERROR,
            name="오류",
            status=ExecutionStatus.ERROR,
            error_message="테스트 오류"
        )
        
        state.add_node(node1)
        state.add_node(node2)
        
        html = tracker.generate_html_timeline("session1")
        assert "✓" in html  # 성공 아이콘
        assert "✗" in html  # 오류 아이콘
        assert "테스트 오류" in html


class TestExecutionStatus:
    """실행 상태 테스트"""

    def test_status_values(self):
        """상태 값 확인"""
        assert ExecutionStatus.PENDING.value == "pending"
        assert ExecutionStatus.RUNNING.value == "running"
        assert ExecutionStatus.SUCCESS.value == "success"
        assert ExecutionStatus.ERROR.value == "error"
        assert ExecutionStatus.SKIPPED.value == "skipped"


class TestNodeType:
    """노드 타입 테스트"""

    def test_node_types(self):
        """노드 타입 확인"""
        assert NodeType.INPUT.value == "input"
        assert NodeType.PROCESS.value == "process"
        assert NodeType.API_CALL.value == "api_call"
        assert NodeType.OUTPUT.value == "output"
        assert NodeType.DECISION.value == "decision"
        assert NodeType.ERROR.value == "error"
