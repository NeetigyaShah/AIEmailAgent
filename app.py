import streamlit as st
import os
import plotly.express as px
import pandas as pd
from src.db_utils import init_db, get_unprocessed_emails, update_email_result, get_prompts, update_prompt, get_all_emails
from src.ingestion import fetch_emails_mock, fetch_emails_imap
from src.processor import process_email_batch
from src.styles import CUSTOM_CSS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Page Config
st.set_page_config(page_title="Email Agent", page_icon="📧", layout="wide")

# Vivid Custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize DB
if 'db_initialized' not in st.session_state:
    init_db()
    st.session_state.db_initialized = True

# Sidebar
with st.sidebar:
    st.title("📧 Email Agent")
    st.markdown("---")
    mode = st.radio("Mode", ["Mock Inbox", "Real Gmail (IMAP)"])
    
    if mode == "Real Gmail (IMAP)":
        st.write("**Fetch Options**")
        fetch_limit = st.number_input("Number of emails to fetch", min_value=1, max_value=50, value=10)
        st.markdown("---")
        
        auth_method = st.radio("Auth Method", ["App Password", "Sign in with Google (OAuth)"])
        
        if auth_method == "App Password":
            st.info("Use your App Password, not your login password.")
            email_user = st.text_input("Email")
            email_pass = st.text_input("App Password", type="password")
            imap_server = st.text_input("IMAP Server", value="imap.gmail.com")
            
            if st.button("Fetch from Gmail"):
                if not email_user or not email_pass:
                    st.error("Please enter email and password.")
                else:
                    try:
                        with st.spinner("Connecting to Gmail..."):
                            count = fetch_emails_imap(email_user, email_pass, imap_server, limit=fetch_limit)
                        st.success(f"Successfully fetched {count} emails!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to fetch: {e}")

        else: # OAuth
            st.info("Requires 'client_secret.json' in project root.")
            if not os.path.exists("client_secret.json"):
                st.error("❌ client_secret.json not found. Please download it from Google Cloud Console.")
            else:
                from src.auth import get_auth_url, get_credentials_from_code
                
                if 'credentials' not in st.session_state:
                    auth_url, state = get_auth_url("client_secret.json", "http://localhost:8501")
                    st.markdown(f"[👉 Click here to Sign In]({auth_url})")
                    auth_code = st.text_input("Paste the code from the page here:")
                    
                    if auth_code and st.button("Authenticate"):
                        try:
                            creds = get_credentials_from_code("client_secret.json", "http://localhost:8501", auth_code)
                            st.session_state.credentials = creds
                            st.success("Authenticated!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Auth failed: {e}")
                
                if 'credentials' in st.session_state:
                    st.success("✅ Signed in with Google")
                    if st.button("Fetch Emails (OAuth)"):
                        try:
                            # Refresh token if expired
                            if st.session_state.credentials.expired:
                                from google.auth.transport.requests import Request
                                st.session_state.credentials.refresh(Request())
                                
                            # Get email address from profile (optional, or ask user)
                            # For now, we need the user to confirm their email or we fetch it
                            # Let's just ask for the email to be safe for IMAP login
                            email_addr = st.text_input("Confirm Email Address")
                            if email_addr:
                                count = fetch_emails_imap(email_addr, st.session_state.credentials.token, "imap.gmail.com", limit=fetch_limit)
                                st.success(f"Fetched {count} emails!")
                                st.rerun()
                        except Exception as e:
                            st.error(f"Fetch failed: {e}")
                    
    else: # Mock Mode
        if st.button("Fetch Mock Emails"):
            count = fetch_emails_mock()
            st.success(f"Loaded {count} mock emails!")
            st.rerun()

    st.markdown("---")
    st.write("### API Config")
    
    # Check if key is already set in session state or env, but don't show "Loaded" message permanently
    current_key = os.environ.get("GOOGLE_API_KEY", "")
    
    with st.form("api_key_form"):
        api_key_input = st.text_input("Google API Key", value=current_key, type="password")
        submitted = st.form_submit_button("Save API Key")
        
        if submitted:
            if api_key_input:
                os.environ["GOOGLE_API_KEY"] = api_key_input
                st.success("API Key saved for this session!")
            else:
                st.warning("Please enter an API Key.")

    st.markdown("---")
    st.write("**Danger Zone**")
    if st.button("🗑️ Delete All Emails"):
        from src.db_utils import clear_all_emails
        clear_all_emails()
        st.success("All emails deleted!")
        st.rerun()

# Tabs
tab1, tab2, tab3 = st.tabs(["📥 Smart Inbox", "🧠 Agent Brain", "🤖 Interactive Chat"])

# Tab 1: Smart Inbox (Moved from Tab 2)
with tab1:
    st.header("Smart Inbox")
    
    # Analytics Dashboard
    all_emails = get_all_emails()
    
    # Refresh Button
    col_head, col_btn = st.columns([4, 1])
    with col_head:
        st.subheader("📊 Inbox Analytics")
    with col_btn:
        if st.button("🔄 Refresh Data"):
            st.rerun()

    if all_emails:
        # Metrics
        total = len(all_emails)
        processed = len([e for e in all_emails if e['is_processed']])
        action_items_count = sum([len(e['action_items']) for e in all_emails if e['action_items']])
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Emails", total)
        m2.metric("Processed", processed)
        m3.metric("Action Items", action_items_count)
        m4.metric("Drafts Generated", len([e for e in all_emails if e['generated_draft']]))
        
        # Charts
        if processed > 0:
            df = pd.DataFrame(all_emails)
            # Filter only processed for charts
            df_proc = df[df['is_processed'] == True].copy()
            
            if not df_proc.empty:
                c1, c2 = st.columns(2)
                with c1:
                    # Category Distribution
                    fig_cat = px.pie(df_proc, names='category', title='Email Categories', hole=0.4, 
                                     color_discrete_sequence=px.colors.qualitative.Pastel)
                    fig_cat.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
                    st.plotly_chart(fig_cat, use_container_width=True)
                
                with c2:
                    # Timeline
                    try:
                        # Fix: Use utc=True to handle mixed timezones and format='mixed' for different string formats
                        df_proc['timestamp'] = pd.to_datetime(df_proc['timestamp'], format='mixed', errors='coerce', utc=True)
                        df_proc = df_proc.dropna(subset=['timestamp'])
                        
                        if not df_proc.empty:
                            # Determine date span to choose granularity
                            min_date = df_proc['timestamp'].min()
                            max_date = df_proc['timestamp'].max()
                            time_span = max_date - min_date
                            total_seconds = time_span.total_seconds()
                            
                            if total_seconds < 7200: # Less than 2 hours
                                # Granularity: Minute
                                df_proc['time_group'] = df_proc['timestamp'].dt.strftime('%H:%M')
                                title_text = "Emails per Minute"
                                x_axis_title = "Time"
                            elif total_seconds < 172800: # Less than 48 hours
                                # Granularity: Hour
                                df_proc['time_group'] = df_proc['timestamp'].dt.strftime('%H:00')
                                title_text = "Emails per Hour"
                                x_axis_title = "Hour"
                            else:
                                # Granularity: Day
                                df_proc['time_group'] = df_proc['timestamp'].dt.strftime('%Y-%m-%d')
                                title_text = "Emails per Day"
                                x_axis_title = "Date"

                            df_grouped = df_proc.groupby('time_group').size().reset_index(name='count')
                            df_grouped = df_grouped.sort_values('time_group')
                            
                            # Switch back to Plotly as requested
                            fig_time = px.bar(df_grouped, x='time_group', y='count', title=title_text,
                                              color_discrete_sequence=['#ff8a00'])
                            
                            # Handle single-bar width issue
                            num_groups = len(df_grouped)
                            gap = 0.9 if num_groups == 1 else 0.2
                            
                            fig_time.update_layout(
                                paper_bgcolor="rgba(0,0,0,0)", 
                                plot_bgcolor="rgba(0,0,0,0)", 
                                font_color="white",
                                xaxis_title=x_axis_title,
                                yaxis_title="Count",
                                xaxis=dict(type='category'), # Force categorical axis
                                bargap=gap
                            )
                            st.plotly_chart(fig_time, use_container_width=True)
                            
                        else:
                            st.info("No valid dates found for timeline.")
                    except Exception as e:
                        st.error(f"Error generating timeline: {e}")
        
        st.divider()

    col_act, col_stat = st.columns([1, 3])
    with col_act:
        if st.button("Run LangGraph Agent", type="primary"):
            unprocessed = get_unprocessed_emails()
            if not unprocessed:
                st.info("No new emails to process.")
            else:
                # Filter to only selected emails
                emails_to_process = [e for e in unprocessed if e['id'] in st.session_state.get('selected_emails', [])]
                
                if not emails_to_process:
                    st.warning("Please select at least one email to process.")
                else:
                    process_email_batch(emails_to_process)
                    # Clear selection after processing
                    st.session_state.selected_emails = []
                    st.rerun()

    # Display Emails
    if not all_emails:
        st.info("📭 Your inbox is empty! Use the Sidebar to fetch emails.")
    else:
        if 'selected_emails' not in st.session_state:
            st.session_state.selected_emails = []

        # Selection Controls
        c1, c2 = st.columns([1, 4])
        with c1:
            # Initialize previous state if not exists
            if "select_all_state" not in st.session_state:
                st.session_state.select_all_state = False
            
            # The checkbox widget
            select_all = st.checkbox("Select All Unprocessed", key="select_all_checkbox")
            
            # Detect Change
            if select_all != st.session_state.select_all_state:
                st.session_state.select_all_state = select_all
                unprocessed_ids = [e['id'] for e in all_emails if not e['is_processed']]
                
                if select_all:
                    # Select All
                    st.session_state.selected_emails = list(set(st.session_state.selected_emails + unprocessed_ids))
                    # Force update individual checkbox widgets
                    for uid in unprocessed_ids:
                        st.session_state[f"chk_{uid}"] = True
                else:
                    # Deselect All Unprocessed
                    st.session_state.selected_emails = [uid for uid in st.session_state.selected_emails if uid not in unprocessed_ids]
                    # Force update individual checkbox widgets
                    for uid in unprocessed_ids:
                        st.session_state[f"chk_{uid}"] = False
                
                st.rerun()

        with c2:
             if st.button("Load More Emails (IMAP)"):
                 st.warning("Use the Sidebar 'Fetch from Gmail' with a higher limit to load more.")
                
        for email in all_emails:
            # Determine badge color
            cat_lower = str(email['category']).lower()
            badge_class = "badge-work" # default
            if "personal" in cat_lower: badge_class = "badge-personal"
            elif "spam" in cat_lower: badge_class = "badge-spam"
            elif "newsletter" in cat_lower: badge_class = "badge-newsletter"
            # Dynamic badge for new categories
            if badge_class == "badge-work" and cat_lower not in ["work", "personal", "spam", "newsletter", "uncategorized"]:
                 badge_class = "badge-work" # Fallback or add new CSS dynamically if needed, but reusing existing is safer for now
            
            # Checkbox for selection (only for unprocessed)
            is_selected = email['id'] in st.session_state.selected_emails
            
            # Use a tighter layout
            col_check, col_content = st.columns([0.05, 0.95])
            
            with col_check:
                if not email['is_processed']:
                    # Fix: Provide a non-empty label and hide it for accessibility compliance
                    if st.checkbox("Select", key=f"chk_{email['id']}", value=is_selected, label_visibility="hidden"):
                        if email['id'] not in st.session_state.selected_emails:
                            st.session_state.selected_emails.append(email['id'])
                    else:
                        if email['id'] in st.session_state.selected_emails:
                            st.session_state.selected_emails.remove(email['id'])
                else:
                    # Placeholder to align processed emails with unprocessed ones
                    st.write("") 
            
            with col_content:
                with st.expander(f"{'✅' if email['is_processed'] else '🆕'} {email['sender']}: {email['subject']}"):
                    # Render HTML Body safely
                    import html
                    body_content = email['body']
                    # Simple check if it looks like HTML
                    if "<html" in body_content.lower() or "<div" in body_content.lower() or "<p>" in body_content.lower():
                         # It's HTML, render it in an iframe or directly if safe. 
                         # Streamlit's st.markdown(..., unsafe_allow_html=True) can do it but might break layout.
                         # Better to use st.components.v1.html for full isolation if it's complex, 
                         # but let's try a sanitized div first for better integration.
                         # Actually, for "like Google", an iframe is safest and most accurate.
                         import streamlit.components.v1 as components
                         components.html(body_content, height=300, scrolling=True)
                    else:
                        # Text content
                        st.markdown(f"""
                        <div class="email-card">
                            <img src="{email.get('image_url') or 'https://picsum.photos/seed/default/600/300'}" style="width:100%; height:150px; object-fit:cover; border-radius:8px; margin-bottom:10px;">
                            <p><strong>From:</strong> {email['sender']}</p>
                            <p><strong>Time:</strong> {email['timestamp']}</p>
                            <hr style="border-color: #4b4966;">
                            <p>{html.escape(body_content)}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    if email['is_processed']:
                        st.markdown(f'<span class="category-badge {badge_class}">{email["category"]}</span>', unsafe_allow_html=True)
                        
                        # Summary Section
                        if email.get('summary'):
                            st.info(f"**📝 Summary:** {email['summary']}")
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            if email['action_items']:
                                st.write("**Action Items:**")
                                for item in email['action_items']:
                                    st.write(f"- {item}")
                        with c2:
                            if email['generated_draft']:
                                st.success("**Draft Reply:**")
                                # Display Draft for Copying
                                st.code(email['generated_draft'], language="text")
                                st.caption("Click the copy icon in the top right of the box above to copy to clipboard.")
                            elif "spam" in cat_lower:
                                st.warning("Marked as Spam - No Reply Drafted")

# Tab 2: Agent Brain (Moved from Tab 1)
with tab2:
    st.header("Agent Brain Configuration")
    st.write("Customize the prompts used by the agent nodes.")
    
    prompts = get_prompts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Categorizer Prompt")
        cat_prompt = st.text_area("Instructions for Categorizer Node", value=prompts.get('categorization', ''), height=150)
        if st.button("Save Categorizer Prompt"):
            update_prompt('categorization', cat_prompt)
            st.success("Saved!")

        st.subheader("Extractor Prompt")
        ext_prompt = st.text_area("Instructions for Extractor Node", value=prompts.get('extraction', ''), height=150)
        if st.button("Save Extractor Prompt"):
            update_prompt('extraction', ext_prompt)
            st.success("Saved!")

    with col2:
        st.subheader("Auto-Reply Prompt")
        rep_prompt = st.text_area("Instructions for Drafter Node", value=prompts.get('auto_reply', ''), height=400)
        if st.button("Save Auto-Reply Prompt"):
            update_prompt('auto_reply', rep_prompt)
            st.success("Saved!")

# Tab 3: Interactive Chat
with tab3:
    st.header("Chat with your Email")
    
    all_emails = get_all_emails()
    if not all_emails:
        st.info("Please fetch emails first.")
    else:
        # Add "All Emails" option
        email_options = {"All Emails": "all"}
        # Use ID in key to ensure uniqueness and stability
        email_options.update({f"{e['sender']}: {e['subject']} ({e['id']})": e for e in all_emails})
        
        # Fix: Add key to selectbox to persist selection across reruns
        selected_option = st.selectbox("Select an email to chat about:", list(email_options.keys()), key="chat_email_selector")
        
        if selected_option:
            # Determine context based on selection
            if selected_option == "All Emails":
                current_id = "all"
            else:
                current_id = email_options[selected_option]['id']
            
            # Initialize chat state if needed
            if "current_chat_id" not in st.session_state:
                st.session_state.current_chat_id = current_id
                st.session_state.messages = []
            
            # Check for context switch
            if st.session_state.current_chat_id != current_id:
                st.session_state.messages = []
                st.session_state.current_chat_id = current_id

            # Context Content Generation
            if selected_option == "All Emails":
                context_content = "Here is a summary of all emails in the inbox:\n\n"
                for e in all_emails:
                    # Enrich context with timestamp and metadata for better reasoning
                    context_content += f"""
                    - ID: {e['id']}
                    - From: {e['sender']}
                    - Subject: {e['subject']}
                    - Date/Time: {e['timestamp']}
                    - Category: {e['category']}
                    - Summary: {e.get('summary', 'N/A')}
                    - Action Items: {e.get('action_items', [])}
                    - Body Snippet: {e['body'][:300]}...
                    --------------------------------------------------
                    """
                st.info("Chatting with context from ALL emails.")
            else:
                selected_email = email_options[selected_option]
                context_content = f"From: {selected_email['sender']}\nSubject: {selected_email['subject']}\nBody:\n{selected_email['body']}"
                
                st.markdown(f"""
                <div class="email-card">
                    <h3>{selected_email['subject']}</h3>
                    <p>{selected_email['body']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Chat Interface
            col_header, col_clear = st.columns([4, 1])
            with col_header:
                st.write("### Conversation")
            with col_clear:
                if st.button("🗑️ Clear Chat"):
                    st.session_state.messages = []
                    st.rerun()

            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            if prompt := st.chat_input("Ask something..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    # Fetch current prompts to make the chat "Prompt-Aware"
                    current_prompts = get_prompts()
                    
                    system_prompt = f"""You are a helpful email assistant. 
                    Answer the user's question based ONLY on the provided email context.
                    
                    GUIDELINES:
                    1. If the user asks to CATEGORIZE, use this rule: {current_prompts.get('categorization')}
                    2. If the user asks to EXTRACT TASKS, use this rule: {current_prompts.get('extraction')}
                    3. If the user asks to DRAFT A REPLY, use this rule: {current_prompts.get('auto_reply')}
                    4. For all other questions (e.g., "Which email is urgent?", "Summarize this", "Who sent this?"), answer naturally based on the context. 
                       - DO NOT use the 'N/A' rule from the auto-reply section unless the user specifically asks to DRAFT a reply.
                       - If the user asks "Which email to reply to", analyze the content/urgency and give a recommendation, BUT IGNORE any emails from "noreply" or "no-reply" addresses.
                       - IMPORTANT: When referring to a specific email, refer to it by its SENDER and SUBJECT (e.g., "The email from Google about Security Alert"). DO NOT refer to it by its 'ID' (e.g., "Email 32379").
                       - If you cannot find an answer or no emails match the criteria, politely explain why (e.g., "I didn't find any urgent emails needing a reply.") instead of saying "N/A".
                    
                    Context:
                    {{context}}
                    
                    Question: {{question}}
                    """
                    
                    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)
                    chat_prompt = ChatPromptTemplate.from_template(system_prompt)
                    chain = chat_prompt | llm | StrOutputParser()
                    response = chain.invoke({"context": context_content, "question": prompt})
                    
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
