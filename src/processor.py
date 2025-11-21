
import streamlit as st
from typing import List, Dict, Any
from src.graph import app as graph_app
from src.db_utils import update_email_result, get_prompts

def process_email_batch(emails: List[Dict[str, Any]], batch_size: int = 10):
    """
    Processes a list of emails in batches using the LangGraph agent.
    Updates the database with the results.
    """
    total_emails = len(emails)
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    current_prompts = get_prompts()
    
    for i in range(0, total_emails, batch_size):
        batch_emails = emails[i : i + batch_size]
        status_text.text(f"Processing batch {i//batch_size + 1} (emails {i+1}-{min(i+batch_size, total_emails)})...")
        
        # Prepare Batch Input (Single State)
        batch_input_data = []
        for email in batch_emails:
            batch_input_data.append({
                "id": email['id'],
                "content": email['body'],
                "sender": email['sender'],
                "image_url": email.get('image_url')
            })
        
        initial_state = {
            "emails": batch_input_data,
            "results": {},
            "user_prompts": current_prompts
        }
        
        # Invoke Graph (Single Call for Batch)
        try:
            output_state = graph_app.invoke(initial_state)
            results = output_state.get("results", {})
            
            # Update DB with results
            for email in batch_emails:
                # Get result for this specific email ID
                res = results.get(email['id'], {})
                
                update_email_result(
                    email['id'],
                    res.get('category', 'Uncategorized'),
                    res.get('action_items', []),
                    res.get('generated_draft', ''),
                    res.get('summary', '')
                )
                
        except Exception as e:
            st.error(f"Error processing batch: {e}")
        
        progress_bar.progress(min((i + batch_size) / total_emails, 1.0))
    
    status_text.text("Processing complete!")
