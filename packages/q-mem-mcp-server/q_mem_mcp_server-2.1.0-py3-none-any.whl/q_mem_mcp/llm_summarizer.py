"""
LLM-based Conversation Summarizer for Q Memory MCP Server
LLM에 위탁하여 대화 내용을 지능적으로 요약
"""

import json
import os
import requests
from typing import List, Dict, Any, Optional


class LLMSummarizer:
    """LLM 기반 대화 요약 클래스"""
    
    def __init__(self):
        # OpenAI API 설정 (환경변수에서 읽기)
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-3.5-turbo"
        self.max_retries = 2
        self.timeout = 30
    
    def _call_openai_api(self, prompt: str) -> Optional[str]:
        """OpenAI API 호출"""
        if not self.api_key:
            return None
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a helpful assistant that summarizes conversations accurately and concisely in Korean."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.3
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.api_url, 
                    headers=headers, 
                    json=data, 
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result['choices'][0]['message']['content'].strip()
                else:
                    print(f"OpenAI API error: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"OpenAI API call failed (attempt {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    return None
        
        return None
    
    def _format_conversation_for_llm(self, conv: Dict[str, Any]) -> str:
        """대화를 LLM이 이해할 수 있는 형태로 포맷팅"""
        user_msg = conv.get('user_message', '')
        ai_msg = conv.get('ai_response', '')
        timestamp = conv.get('timestamp', '')[:16].replace('T', ' ')
        
        return f"[{timestamp}] User: {user_msg}\nAssistant: {ai_msg}"
    
    def _create_batch_summary_prompt(self, conversations: List[Dict], summary_level: str) -> str:
        """배치 요약을 위한 프롬프트 생성"""
        conv_texts = []
        for i, conv in enumerate(conversations, 1):
            conv_text = self._format_conversation_for_llm(conv)
            conv_texts.append(f"=== 대화 {i} ===\n{conv_text}")
        
        all_conversations = "\n\n".join(conv_texts)
        
        if summary_level == "brief":
            instruction = """각 대화를 1-2줄로 간단히 요약해주세요. 
주요 주제와 결론만 포함하세요. 형식: "1. 주제: 결론"
예시: "1. Python 리스트 질문: 가변객체 특성과 주요 메서드 설명함"
"""
        elif summary_level == "medium":
            instruction = """각 대화를 3-4줄로 상세히 요약해주세요.
주요 내용, 예시, 결론을 포함하세요. 형식: "1. 주제: 상세내용"
예시: "1. 클래스 상속 설명: 부모클래스 속성 상속 방법, super() 사용법, 다중상속 주의사항 등을 코드 예시와 함께 설명함"
"""
        else:
            return ""
        
        prompt = f"""다음 {len(conversations)}개의 대화를 요약해주세요:

{instruction}

대화 내용:
{all_conversations}

요약 결과 (번호순으로):"""
        
        return prompt
    
    def _parse_batch_summary_response(self, response: str, original_count: int) -> List[str]:
        """배치 요약 응답을 파싱하여 개별 요약으로 분리"""
        if not response:
            return ["요약 실패"] * original_count
        
        lines = response.strip().split('\n')
        summaries = []
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith(tuple('123456789')) or line.startswith('•') or line.startswith('-')):
                # 번호나 불릿 포인트 제거
                clean_line = line
                for prefix in ['1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '•', '-']:
                    if clean_line.startswith(prefix):
                        clean_line = clean_line[len(prefix):].strip()
                        break
                
                if clean_line:
                    summaries.append(clean_line)
        
        # 원본 개수와 맞추기
        while len(summaries) < original_count:
            summaries.append("요약 생성됨")
        
        return summaries[:original_count]
    
    def summarize_conversations_batch(self, conversations: List[Dict], summary_level: str) -> List[str]:
        """대화 목록을 배치로 요약"""
        if not conversations:
            return []
        
        # 배치 크기 제한 (토큰 제한 고려)
        batch_size = 15 if summary_level == "brief" else 10
        all_summaries = []
        
        for i in range(0, len(conversations), batch_size):
            batch = conversations[i:i + batch_size]
            
            # LLM API 호출
            prompt = self._create_batch_summary_prompt(batch, summary_level)
            response = self._call_openai_api(prompt)
            
            if response:
                batch_summaries = self._parse_batch_summary_response(response, len(batch))
            else:
                # API 실패 시 폴백: 원본 AI 응답을 짧게 자르기
                batch_summaries = []
                for conv in batch:
                    ai_msg = conv.get('ai_response', '')
                    if summary_level == "brief":
                        fallback = ai_msg[:100] + "..." if len(ai_msg) > 100 else ai_msg
                    else:
                        fallback = ai_msg[:200] + "..." if len(ai_msg) > 200 else ai_msg
                    batch_summaries.append(fallback)
            
            all_summaries.extend(batch_summaries)
            
            # 진행상황 표시
            if len(conversations) > 20:
                progress = min(100, int((i + batch_size) / len(conversations) * 100))
                print(f"📊 Summarizing conversations... {progress}%")
        
        return all_summaries
    
    def format_conversations_with_llm_summary(self, conversations: List[Dict[str, Any]]) -> str:
        """LLM 요약을 사용하여 대화 목록을 포맷팅"""
        if not conversations:
            return "ℹ️ **No previous conversations found.**"
        
        total_count = len(conversations)
        
        print(f"🧠 Processing {total_count} conversations with LLM summarization...")
        
        if total_count < 100:
            # 100개 미만: 짧은 대화는 그대로, 긴 대화만 요약
            formatted_text = f"🧠 **All Conversations ({total_count} total):**\n\n"
            
            long_conversations = []
            long_indices = []
            
            # 긴 대화 식별
            for i, conv in enumerate(conversations):
                ai_msg = conv.get('ai_response', '')
                if len(ai_msg) > 300:  # 300자 이상인 경우만 요약
                    long_conversations.append(conv)
                    long_indices.append(i)
            
            # 긴 대화들을 배치로 요약
            if long_conversations:
                print(f"📝 Summarizing {len(long_conversations)} long conversations...")
                summaries = self.summarize_conversations_batch(long_conversations, "brief")
                summary_dict = dict(zip(long_indices, summaries))
            else:
                summary_dict = {}
            
            # 전체 대화 포맷팅
            for i, conv in enumerate(conversations, 1):
                user_msg = conv.get('user_message', '')
                ai_msg = conv.get('ai_response', '')
                timestamp = conv.get('timestamp', '')[:16].replace('T', ' ')
                
                # 긴 대화는 요약 사용, 짧은 대화는 그대로
                if i-1 in summary_dict:
                    ai_display = summary_dict[i-1]
                else:
                    ai_display = ai_msg
                
                formatted_text += f"**{i}. ({timestamp})**\n"
                formatted_text += f"**User**: {user_msg}\n"
                formatted_text += f"**Assistant**: {ai_display}\n\n"
            
            return formatted_text
        
        else:
            # 100개 이상: 퍼센트 기반 처리
            recent_5_percent = max(5, int(total_count * 0.05))
            middle_15_percent = max(10, int(total_count * 0.15))
            old_remainder = total_count - recent_5_percent - middle_15_percent
            
            formatted_text = f"🧠 **Complete Conversation History ({total_count} total conversations):**\n\n"
            
            # 오래된 대화들 (80% - Brief Summary)
            if old_remainder > 0:
                print(f"📚 Summarizing {old_remainder} older conversations...")
                old_conversations = conversations[:old_remainder]
                old_summaries = self.summarize_conversations_batch(old_conversations, "brief")
                
                formatted_text += f"📚 **Earlier Context ({old_remainder} conversations - AI summarized):**\n"
                for i, (conv, summary) in enumerate(zip(old_conversations, old_summaries), 1):
                    user_msg = conv.get('user_message', '')
                    timestamp = conv.get('timestamp', '')[:16].replace('T', ' ')
                    
                    formatted_text += f"{i}. ({timestamp}) User: {user_msg}\n"
                    formatted_text += f"   AI: {summary}\n\n"
                
                formatted_text += "\n"
            
            # 중간 대화들 (15% - Medium Summary)  
            if middle_15_percent > 0:
                print(f"💬 Summarizing {middle_15_percent} recent conversations...")
                middle_start = old_remainder
                middle_end = old_remainder + middle_15_percent
                middle_conversations = conversations[middle_start:middle_end]
                middle_summaries = self.summarize_conversations_batch(middle_conversations, "medium")
                
                formatted_text += f"💬 **Recent Context ({middle_15_percent} conversations - AI detailed summaries):**\n"
                
                for i, (conv, summary) in enumerate(zip(middle_conversations, middle_summaries), middle_start + 1):
                    user_msg = conv.get('user_message', '')
                    timestamp = conv.get('timestamp', '')[:16].replace('T', ' ')
                    
                    formatted_text += f"**{i}. ({timestamp})**\n"
                    formatted_text += f"**User**: {user_msg}\n"
                    formatted_text += f"**Assistant**: {summary}\n\n"
                
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
            
            formatted_text += "✅ **I now remember all our previous conversations with AI-powered summaries and can continue where we left off.**\n"
            formatted_text += "💡 **You can reference any of the above topics, and I'll understand the context perfectly.**"
            
            return formatted_text


# 전역 LLM 요약기 인스턴스
_llm_summarizer = None


def get_llm_summarizer() -> LLMSummarizer:
    """LLM 요약기 인스턴스 반환"""
    global _llm_summarizer
    if _llm_summarizer is None:
        _llm_summarizer = LLMSummarizer()
    return _llm_summarizer
