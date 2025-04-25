import os
import json
import re
from typing import Dict, Any, List, Optional
import asyncio
import logging
from langchain.llms import Qwen
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get Qwen API key from environment
QWEN_API_KEY = os.environ.get("QWEN_API_KEY")

# Initialize Qwen LLM
def get_llm():
    if not QWEN_API_KEY:
        raise ValueError("QWEN_API_KEY not set in environment variables")
    
    return Qwen(
        qwen_api_key=QWEN_API_KEY,
        model_name="qwen-max",  # Use the appropriate model
        temperature=0.3,  # Lower temperature for more factual responses
    )

async def generate_summary(transcript: str, language: str) -> Dict[str, Any]:
    """
    Generate summary, action items, and decisions from transcript using LangChain with Qwen
    
    Args:
        transcript: Transcription text
        language: Language of the transcript
        
    Returns:
        Dictionary containing summary, action items, decisions, participants, and duration
    """
    
    if not transcript or transcript.strip() == "":
        raise ValueError("Empty transcript")
    
    # Extract participants from transcript
    participants = extract_participants(transcript)
    
    # Estimate duration based on transcript length
    # This is a rough estimate - in a real implementation, you would get this from the audio file
    word_count = len(transcript.split())
    estimated_minutes = max(5, round(word_count / 150))  # Assuming 150 words per minute
    duration = f"{estimated_minutes} min"
    
    # Split transcript into chunks if it's too long
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=4000,
        chunk_overlap=200,
        length_function=len,
    )
    
    docs = [Document(page_content=transcript)]
    if len(transcript) > 4000:
        docs = text_splitter.split_documents(docs)
    
    # Initialize LLM
    llm = get_llm()
    
    # Create summarization chain
    summary_chain = load_summarize_chain(
        llm,
        chain_type="map_reduce",
        verbose=True
    )
    
    # Generate summary
    summary_result = await asyncio.to_thread(
        summary_chain.run, docs
    )
    
    # Create action items extraction chain
    action_items_template = get_action_items_template(language)
    action_items_prompt = PromptTemplate(
        template=action_items_template,
        input_variables=["text"]
    )
    action_items_chain = LLMChain(llm=llm, prompt=action_items_prompt)
    
    # Generate action items
    action_items_result = await asyncio.to_thread(
        action_items_chain.run, transcript
    )
    action_items = parse_action_items(action_items_result)
    
    # Create decisions extraction chain
    decisions_template = get_decisions_template(language)
    decisions_prompt = PromptTemplate(
        template=decisions_template,
        input_variables=["text"]
    )
    decisions_chain = LLMChain(llm=llm, prompt=decisions_prompt)
    
    # Generate decisions
    decisions_result = await asyncio.to_thread(
        decisions_chain.run, transcript
    )
    decisions = parse_decisions(decisions_result)
    
    return {
        "summary": summary_result,
        "action_items": action_items,
        "decisions": decisions,
        "participants": participants,
        "duration": duration
    }

def extract_participants(transcript: str) -> List[Dict[str, str]]:
    """Extract participants from transcript"""
    participants = set()
    
    # Simple regex to extract names from transcript
    lines = transcript.strip().split('\n')
    for line in lines:
        if ':' in line:
            name = line.split(':', 1)[0].strip()
            if name:
                participants.add(name)
    
    return [{"name": name} for name in participants]

def get_action_items_template(language: str) -> str:
    """Get action items extraction prompt template based on language"""
    if language.lower() == "english":
        return """
        Extract all action items from the following meeting transcript. 
        For each action item, identify:
        1. The task to be done
        2. The person assigned to the task (if mentioned)
        3. The due date or deadline (if mentioned)

        Format your response as a JSON array with objects containing "text", "assignee", and "due_date" fields.
        If assignee or due date is not specified, leave those fields empty.

        Example:
        [
            {
                "text": "Prepare the quarterly report",
                "assignee": "John",
                "due_date": "2023-04-15"
            },
            {
                "text": "Schedule the client meeting",
                "assignee": "Sarah",
                "due_date": ""
            }
        ]

        Transcript:
        {text}
        """
    elif language.lower() == "mandarin":
        return """
        从以下会议记录中提取所有行动项目。
        对于每个行动项目，请确定：
        1. 需要完成的任务
        2. 分配给该任务的人员（如果提到）
        3. 截止日期或期限（如果提到）

        将您的回复格式化为包含"text"、"assignee"和"due_date"字段的JSON数组。
        如果未指定负责人或截止日期，请将这些字段留空。

        示例：
        [
            {
                "text": "准备季度报告",
                "assignee": "张三",
                "due_date": "2023-04-15"
            },
            {
                "text": "安排客户会议",
                "assignee": "李四",
                "due_date": ""
            }
        ]

        会议记录：
        {text}
        """
    elif language.lower() == "cantonese":
        return """
        從以下會議記錄中提取所有行動項目。
        對於每個行動項目，請確定：
        1. 需要完成嘅任務
        2. 分配俾該任務嘅人員（如果提到）
        3. 截止日期或期限（如果提到）

        將您嘅回覆格式化為包含"text"、"assignee"同"due_date"字段嘅JSON數組。
        如果未指定負責人或截止日期，請將呢啲字段留空。

        示例：
        [
            {
                "text": "準備季度報告",
                "assignee": "張三",
                "due_date": "2023-04-15"
            },
            {
                "text": "安排客戶會議",
                "assignee": "李四",
                "due_date": ""
            }
        ]

        會議記錄：
        {text}
        """
    else:  # mixed or other
        return """
        Extract all action items from the following meeting transcript in any language.
        For each action item, identify:
        1. The task to be done
        2. The person assigned to the task (if mentioned)
        3. The due date or deadline (if mentioned)

        Format your response as a JSON array with objects containing "text", "assignee", and "due_date" fields.
        If assignee or due date is not specified, leave those fields empty.

        Example:
        [
            {
                "text": "Prepare the quarterly report",
                "assignee": "John",
                "due_date": "2023-04-15"
            },
            {
                "text": "安排客户会议",
                "assignee": "李四",
                "due_date": ""
            }
        ]

        Transcript:
        {text}
        """

def get_decisions_template(language: str) -> str:
    """Get decisions extraction prompt template based on language"""
    if language.lower() == "english":
        return """
        Extract all key decisions made during the meeting from the following transcript.
        Format your response as a JSON array with objects containing "text" field for each decision.

        Example:
        [
            {
                "text": "Approved the budget increase for Q2"
            },
            {
                "text": "Decided to postpone the product launch until September"
            }
        ]

        Transcript:
        {text}
        """
    elif language.lower() == "mandarin":
        return """
        从以下会议记录中提取会议期间做出的所有关键决定。
        将您的回复格式化为包含每个决定的"text"字段的JSON数组。

        示例：
        [
            {
                "text": "批准了第二季度的预算增加"
            },
            {
                "text": "决定将产品发布推迟到9月"
            }
        ]

        会议记录：
        {text}
        """
    elif language.lower() == "cantonese":
        return """
        從以下會議記錄中提取會議期間做出嘅所有關鍵決定。
        將您嘅回覆格式化為包含每個決定嘅"text"字段嘅JSON數組。

        示例：
        [
            {
                "text": "批准咗第二季度嘅預算增加"
            },
            {
                "text": "決定將產品發佈推遲到9月"
            }
        ]

        會議記錄：
        {text}
        """
    else:  # mixed or other
        return """
        Extract all key decisions made during the meeting from the following transcript in any language.
        Format your response as a JSON array with objects containing "text" field for each decision.

        Example:
        [
            {
                "text": "Approved the budget increase for Q2"
            },
            {
                "text": "决定将产品发布推迟到9月"
            }
        ]

        Transcript:
        {text}
        """

def parse_action_items(action_items_text: str) -> List[Dict[str, str]]:
    """Parse action items from LLM response"""
    try:
        # Find JSON array in the text
        match = re.search(r'\[.*\]', action_items_text, re.DOTALL)
        if match:
            action_items_json = match.group(0)
            return json.loads(action_items_json)
        else:
            logger.warning(f"Could not find JSON array in action items response: {action_items_text}")
            return []
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse action items: {e}")
        return []

def parse_decisions(decisions_text: str) -> List[Dict[str, str]]:
    """Parse decisions from LLM response"""
    try:
        # Find JSON array in the text
        match = re.search(r'\[.*\]', decisions_text, re.DOTALL)
        if match:
            decisions_json = match.group(0)
            return json.loads(decisions_json)
        else:
            logger.warning(f"Could not find JSON array in decisions response: {decisions_text}")
            return []
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse decisions: {e}")
        return []
