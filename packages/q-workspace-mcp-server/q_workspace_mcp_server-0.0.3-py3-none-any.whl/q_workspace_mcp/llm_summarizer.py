"""
Q CLI LLM-based Conversation Summarizer for Q Workspace MCP Server
Q CLI의 LLM을 활용하여 대화 내용을 지능적으로 요약
"""

from typing import List, Dict, Any


class QCLILLMSummarizer:
    """Q CLI LLM 기반 대화 요약 클래스"""
    
    def __init__(self):
        pass
    
    def _format_conversation_for_summary(self, conv: Dict[str, Any]) -> str:
        """대화를 요약용으로 포맷팅"""
        user_msg = conv.get('user_message', '')
        ai_msg = conv.get('ai_response', '')
        timestamp = conv.get('timestamp', '')[:16].replace('T', ' ')
        
        return f"[{timestamp}] User: {user_msg}\nAssistant: {ai_msg}"
    
    def _create_summary_request_for_qcli(self, conversations: List[Dict], summary_level: str) -> str:
        """Q CLI LLM에게 전달할 요약 요청 생성"""
        conv_texts = []
        for i, conv in enumerate(conversations, 1):
            conv_text = self._format_conversation_for_summary(conv)
            conv_texts.append(f"=== 대화 {i} ===\n{conv_text}")
        
        all_conversations = "\n\n".join(conv_texts)
        
        if summary_level == "brief":
            instruction = """다음 대화들을 각각 최소 2줄, 최대 3줄로 간단히 요약해주세요. 주요 주제와 결론을 포함하세요.
형식: "1. 주제: 결론"
예시: "1. Python 리스트 질문: 가변객체 특성과 주요 메서드 설명함"
"""
        elif summary_level == "medium":
            instruction = """다음 대화들을 각각 최소3줄, 최대 5줄로 상세히 요약해주세요. 주요 내용, 예시, 결론을 포함하세요.
형식: "1. 주제: 상세내용"
예시: "1. 클래스 상속 설명: 부모클래스 속성 상속 방법, super() 사용법, 다중상속 주의사항 등을 코드 예시와 함께 설명함"
"""
        else:
            return ""
        
        summary_request = f"""🤖 **Q CLI LLM 요약 요청**

{instruction}

대화 내용:
{all_conversations}

요약 결과 (번호순으로):"""
        
        return summary_request
    
    def format_conversations_with_qcli_summary(self, conversations: List[Dict[str, Any]]) -> str:
        """Q CLI LLM 요약을 요청하는 형태로 대화 목록 포맷팅"""
        if not conversations:
            return "ℹ️ **No previous conversations found.**"
        
        total_count = len(conversations)
        
        if total_count < 100:
            # 100개 미만: 짧은 대화는 그대로, 긴 대화는 Q CLI LLM에게 요약 요청
            formatted_text = f"🧠 **All Conversations ({total_count} total):**\n\n"
            
            long_conversations = []
            short_conversations = []
            
            # 대화 분류
            for i, conv in enumerate(conversations):
                ai_msg = conv.get('ai_response', '')
                if len(ai_msg) > 300:  # 300자 이상인 경우 요약 대상
                    long_conversations.append((i, conv))
                else:
                    short_conversations.append((i, conv))
            
            # 긴 대화가 있으면 Q CLI LLM에게 요약 요청
            if long_conversations:
                summary_request = self._create_summary_request_for_qcli(
                    [conv for _, conv in long_conversations], 
                    "brief"
                )
                
                formatted_text += f"📝 **요약이 필요한 {len(long_conversations)}개 대화가 있습니다.**\n\n"
                formatted_text += summary_request + "\n\n"
                formatted_text += "---\n\n"
            
            # 모든 대화 표시 (짧은 것은 그대로, 긴 것은 표시만)
            for i, conv in enumerate(conversations, 1):
                user_msg = conv.get('user_message', '')
                ai_msg = conv.get('ai_response', '')
                timestamp = conv.get('timestamp', '')[:16].replace('T', ' ')
                
                formatted_text += f"**{i}. ({timestamp})**\n"
                formatted_text += f"**User**: {user_msg}\n"
                
                if len(ai_msg) > 300:
                    formatted_text += f"**Assistant**: [위에서 요약 요청된 긴 응답]\n\n"
                else:
                    formatted_text += f"**Assistant**: {ai_msg}\n\n"
            
            return formatted_text
        
        else:
            # 100개 이상: 퍼센트 기반으로 Q CLI LLM에게 요약 요청
            recent_5_percent = max(5, int(total_count * 0.05))
            middle_15_percent = max(10, int(total_count * 0.15))
            old_remainder = total_count - recent_5_percent - middle_15_percent
            
            formatted_text = f"🧠 **Complete Conversation History ({total_count} total conversations):**\n\n"
            
            # Q CLI LLM에게 요약 요청들 생성
            summary_requests = []
            
            # 오래된 대화들 (80% - Brief Summary)
            if old_remainder > 0:
                old_conversations = conversations[:old_remainder]
                old_summary_request = self._create_summary_request_for_qcli(old_conversations, "brief")
                summary_requests.append(("earlier", old_remainder, old_summary_request))
            
            # 중간 대화들 (15% - Medium Summary)
            if middle_15_percent > 0:
                middle_start = old_remainder
                middle_end = old_remainder + middle_15_percent
                middle_conversations = conversations[middle_start:middle_end]
                medium_summary_request = self._create_summary_request_for_qcli(middle_conversations, "medium")
                summary_requests.append(("recent", middle_15_percent, medium_summary_request))
            
            # Q CLI LLM에게 요약 요청
            for request_type, count, request in summary_requests:
                if request_type == "earlier":
                    formatted_text += f"📚 **Earlier Context ({count} conversations) - 요약 요청:**\n\n"
                else:
                    formatted_text += f"💬 **Recent Context ({count} conversations) - 상세 요약 요청:**\n\n"
                
                formatted_text += request + "\n\n"
                formatted_text += "---\n\n"
            
            # 최근 대화들 (5% - Full Detail)
            recent_start = total_count - recent_5_percent
            recent_conversations = conversations[recent_start:]
            
            formatted_text += f"🔥 **Latest Conversations ({recent_5_percent} conversations - full detail):**\n"
            
            for i, conv in enumerate(recent_conversations, recent_start + 1):
                user_msg = conv.get('user_message', '')
                ai_msg = conv.get('ai_response', '')
                timestamp = conv.get('timestamp', '')[:16].replace('T', ' ')
                
                formatted_text += f"**{i}. ({timestamp})**\n"
                formatted_text += f"**User**: {user_msg}\n"
                formatted_text += f"**Assistant**: {ai_msg}\n\n"
            
            formatted_text += "\n🤖 **위의 요약 요청들을 처리해주시면, 모든 이전 대화의 맥락을 완벽히 이해하고 대화를 이어갈 수 있습니다.**\n"
            formatted_text += "💡 **요약이 완료되면 이전 주제들을 자유롭게 참조하실 수 있습니다.**"
            
            return formatted_text


# 전역 Q CLI LLM 요약기 인스턴스
_qcli_llm_summarizer = None


def get_qcli_llm_summarizer() -> QCLILLMSummarizer:
    """Q CLI LLM 요약기 인스턴스 반환"""
    global _qcli_llm_summarizer
    if _qcli_llm_summarizer is None:
        _qcli_llm_summarizer = QCLILLMSummarizer()
    return _qcli_llm_summarizer
