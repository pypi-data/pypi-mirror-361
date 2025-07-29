"""
Conversation Summarizer for Q Memory MCP Server
AI 응답을 효율적으로 요약하는 기능
"""

import re
from typing import List, Dict, Any


class ConversationSummarizer:
    """대화 내용 요약 클래스"""
    
    def __init__(self):
        # 기술 용어 패턴들
        self.tech_patterns = [
            r'\b[A-Z][a-z]*[A-Z][a-zA-Z]*\b',  # CamelCase
            r'\b[a-z]+\(\)\b',                  # 함수명()
            r'\b[a-z_]+\.[a-z_]+\b',           # 모듈.함수
            r'\b[A-Z]{2,}\b',                  # 대문자 약어
            r'`[^`]+`',                        # 백틱 코드
            r'\.[a-z]{2,4}\b',                 # 파일 확장자
        ]
        
        # 결론 키워드들
        self.conclusion_keywords = [
            '결론', '요약', '정리', '따라서', '그러므로', '결과적으로',
            'conclusion', 'summary', 'therefore', 'result', 'finally'
        ]
    
    def extract_technical_terms(self, text: str) -> List[str]:
        """기술 용어 추출"""
        terms = set()
        
        for pattern in self.tech_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            terms.update(matches)
        
        # 중복 제거 및 정렬
        return sorted(list(terms))[:10]  # 최대 10개
    
    def extract_conclusion(self, text: str) -> str:
        """결론 부분 추출"""
        sentences = text.split('.')
        
        # 결론 키워드가 포함된 문장 찾기
        for sentence in reversed(sentences[-3:]):  # 마지막 3문장에서 찾기
            for keyword in self.conclusion_keywords:
                if keyword in sentence.lower():
                    return sentence.strip()
        
        # 결론 키워드가 없으면 마지막 문장
        if sentences:
            return sentences[-1].strip()
        
        return ""
    
    def extract_main_concepts(self, text: str) -> str:
        """주요 개념 추출"""
        # 첫 번째 문장 (보통 주제 설명)
        first_sentence = text.split('.')[0] if '.' in text else text[:100]
        
        # 동작 동사 패턴 찾기
        action_patterns = [
            r'(설명|소개|제공|구현|생성|분석|해결|개선|수정)(?:했습니다|함|해드렸습니다)',
            r'(explained|provided|implemented|created|analyzed|solved|improved|fixed)'
        ]
        
        for pattern in action_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                action = match.group(1)
                return f"{first_sentence[:50]}... ({action}함)"
        
        return first_sentence[:80] + "..." if len(first_sentence) > 80 else first_sentence
    
    def summarize_ai_response(self, response: str, summary_level: str) -> str:
        """AI 응답 요약"""
        if summary_level == "full" or len(response) <= 100:
            return response
        
        # 기본 정보 추출
        main_concepts = self.extract_main_concepts(response)
        conclusion = self.extract_conclusion(response)
        tech_terms = self.extract_technical_terms(response)
        
        # 코드 블록 확인
        code_blocks = len(re.findall(r'```', response))
        has_code = code_blocks > 0
        
        if summary_level == "brief":
            # 짧은 요약 (오래된 대화용)
            summary = main_concepts
            if conclusion and conclusion != main_concepts:
                summary += f" {conclusion}"
            if tech_terms:
                summary += f" (키워드: {', '.join(tech_terms[:3])})"
            if has_code:
                summary += " [코드 포함]"
            return summary
        
        elif summary_level == "medium":
            # 중간 요약 (중간 대화용)
            summary = main_concepts
            if conclusion:
                summary += f" {conclusion}"
            
            # 주요 포인트 추출 (불릿 포인트나 번호 목록)
            bullet_points = re.findall(r'[•\-\*]\s*([^\n]+)', response)
            numbered_points = re.findall(r'\d+\.\s*([^\n]+)', response)
            
            key_points = bullet_points + numbered_points
            if key_points:
                summary += f" 주요 내용: {', '.join(key_points[:3])}"
            
            if tech_terms:
                summary += f" (기술용어: {', '.join(tech_terms[:5])})"
            
            if has_code:
                summary += f" [코드 예시 {code_blocks//2}개 포함]"
            
            return summary
        
        return response  # fallback
    
    def format_conversations_with_context(self, conversations: List[Dict[str, Any]]) -> str:
        """대화 목록을 컨텍스트 형태로 포맷팅"""
        if not conversations:
            return "ℹ️ **No previous conversations found.**"
        
        total_count = len(conversations)
        
        if total_count < 100:
            # 100개 미만: 단순 처리
            formatted_text = f"🧠 **All Conversations ({total_count} total):**\n\n"
            
            for i, conv in enumerate(conversations, 1):
                user_msg = conv.get('user_message', '')
                ai_msg = conv.get('ai_response', '')
                timestamp = conv.get('timestamp', '')[:16].replace('T', ' ')
                
                # AI 응답만 요약 (사용자 메시지는 전체)
                ai_summary = self.summarize_ai_response(ai_msg, "brief")
                
                formatted_text += f"**{i}. ({timestamp})**\n"
                formatted_text += f"**User**: {user_msg}\n"
                formatted_text += f"**Assistant**: {ai_summary}\n\n"
            
            return formatted_text
        
        else:
            # 100개 이상: 퍼센트 기반 처리
            recent_5_percent = max(5, int(total_count * 0.05))
            middle_15_percent = max(10, int(total_count * 0.15))
            old_remainder = total_count - recent_5_percent - middle_15_percent
            
            formatted_text = f"🧠 **Complete Conversation History ({total_count} total conversations):**\n\n"
            
            # 오래된 대화들 (80% - Brief Summary)
            if old_remainder > 0:
                formatted_text += f"📚 **Earlier Context ({old_remainder} conversations - brief summaries):**\n"
                
                old_conversations = conversations[:old_remainder]
                for i, conv in enumerate(old_conversations, 1):
                    user_msg = conv.get('user_message', '')
                    ai_msg = conv.get('ai_response', '')
                    timestamp = conv.get('timestamp', '')[:16].replace('T', ' ')
                    
                    ai_summary = self.summarize_ai_response(ai_msg, "brief")
                    
                    formatted_text += f"{i}. ({timestamp}) User: {user_msg}\n"
                    formatted_text += f"   AI: {ai_summary}\n\n"
                
                formatted_text += "\n"
            
            # 중간 대화들 (15% - Medium Summary)
            if middle_15_percent > 0:
                middle_start = old_remainder
                middle_end = old_remainder + middle_15_percent
                middle_conversations = conversations[middle_start:middle_end]
                
                formatted_text += f"💬 **Recent Context ({middle_15_percent} conversations - detailed summaries):**\n"
                
                for i, conv in enumerate(middle_conversations, middle_start + 1):
                    user_msg = conv.get('user_message', '')
                    ai_msg = conv.get('ai_response', '')
                    timestamp = conv.get('timestamp', '')[:16].replace('T', ' ')
                    
                    ai_summary = self.summarize_ai_response(ai_msg, "medium")
                    
                    formatted_text += f"**{i}. ({timestamp})**\n"
                    formatted_text += f"**User**: {user_msg}\n"
                    formatted_text += f"**Assistant**: {ai_summary}\n\n"
                
                formatted_text += "\n"
            
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
            
            formatted_text += "✅ **I now remember all our previous conversations and can continue where we left off.**\n"
            formatted_text += "💡 **You can reference any of the above topics, and I'll understand the context.**"
            
            return formatted_text


# 전역 요약기 인스턴스
_summarizer = ConversationSummarizer()


def get_summarizer() -> ConversationSummarizer:
    """요약기 인스턴스 반환"""
    return _summarizer
