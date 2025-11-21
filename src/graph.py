from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import json

# --- 1. Define Batch State ---
class BatchState(TypedDict):
    emails: List[Dict[str, Any]]  # List of {id, content, sender}
    results: Dict[str, Dict[str, Any]] # Map id -> {category, action_items, generated_draft}
    user_prompts: Dict[str, str]

# --- 2. Define Batch Node ---

import base64
import requests
from langchain_core.messages import HumanMessage

def batch_processor_node(state: BatchState):
    """Processes a batch of emails in a single LLM call, supporting images."""
    print(f"--- Processing Batch of {len(state['emails'])} Emails ---")
    
    # Get user custom instructions
    cat_prompt = state['user_prompts'].get('categorization', "Categorize as Work, Personal, Spam, or Newsletter.")
    ext_prompt = state['user_prompts'].get('extraction', "Extract key action items.")
    draft_prompt = state['user_prompts'].get('auto_reply', "Draft a professional reply if not spam.")
    
    system_instruction = f"""
    You are an intelligent email assistant. Process the following batch of emails.
    Some emails may contain attached images. Use the image context to improve categorization and extraction (e.g., if it's a receipt or a screenshot of an error).
    
    For EACH email, you must provide:
    1. Category: {cat_prompt}
    2. Action Items: {ext_prompt} (Return as a list of strings)
    3. Draft Reply: {draft_prompt} (Return 'N/A' if Spam or no reply needed)
    4. Summary: A concise 1-2 sentence summary of the email content.
    
    RETURN ONLY JSON. The output must be a JSON object where keys are the Email IDs and values are objects containing 'category', 'action_items', 'generated_draft', and 'summary'.
    """
    
    # Construct Multimodal Message
    content_parts = []
    content_parts.append({"type": "text", "text": system_instruction})
    
    for email in state['emails']:
        # Add Text Content
        email_text = f"\n---\nEmail ID: {email['id']}\nFrom: {email['sender']}\nBody:\n{email['content']}\n"
        content_parts.append({"type": "text", "text": email_text})
        
        # Add Image Content if available
        if email.get('image_url'):
            try:
                # Fetch and encode image
                img_url = email['image_url']
                if img_url.startswith('http'):
                    response = requests.get(img_url, timeout=5)
                    if response.status_code == 200:
                        img_data = base64.b64encode(response.content).decode('utf-8')
                        content_parts.append({
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{img_data}"}
                        })
            except Exception as e:
                print(f"Failed to load image for {email['id']}: {e}")
    
    # Call LLM
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)
    
    # We use a direct HumanMessage invocation for multimodal
    message = HumanMessage(content=content_parts)
    
    # Use JsonOutputParser to parse the text result
    parser = JsonOutputParser()
    
    try:
        # Invoke with the message list
        response_msg = llm.invoke([message])
        content = response_msg.content
        
        # Strip markdown code blocks if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        # Parse the content of the response
        parsed_result = parser.parse(content)
        return {"results": parsed_result}
    except Exception as e:
        print(f"Batch Processing Error: {e}")
        return {"results": {}}

# --- 3. Build Graph ---

def build_batch_graph():
    workflow = StateGraph(BatchState)
    
    workflow.add_node("batch_processor", batch_processor_node)
    workflow.set_entry_point("batch_processor")
    workflow.add_edge("batch_processor", END)
    
    return workflow.compile()

# Create the app instance
app = build_batch_graph()
