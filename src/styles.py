
CUSTOM_CSS = """
<style>
    /* Global Theme */
    .stApp {
        background: linear-gradient(135deg, #1e1e2f 0%, #2d2b42 100%);
        color: #ffffff;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #252538;
        border-right: 1px solid #3f3d56;
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #ff8a00 0%, #e52e71 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        color: white;
    }
    
    /* Cards */
    .email-card {
        background-color: #333247;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #4b4966;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Badges */
    .category-badge {
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        color: white;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    .badge-work { background-color: #4CAF50; }
    .badge-personal { background-color: #2196F3; }
    .badge-spam { background-color: #F44336; }
    .badge-newsletter { background-color: #FF9800; }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Helvetica Neue', sans-serif;
    }
    
    /* Inputs */
    .stTextInput>div>div>input {
        background-color: #333247;
        color: white;
        border: 1px solid #4b4966;
    }
    .stTextArea>div>div>textarea {
        background-color: #333247;
        color: white;
        border: 1px solid #4b4966;
    }
    /* Reduce vertical spacing */
    .st-emotion-cache-1y4p8pa { padding-top: 0rem; padding-bottom: 0rem; } /* Adjust generic block padding */
    .st-emotion-cache-1r6slb0 { gap: 0.5rem; } /* Reduce column gap */
    div[data-testid="column"] { padding: 0 !important; }
    
    /* Compact Expander */
    .streamlit-expanderHeader {
        padding-top: 0.25rem !important;
        padding-bottom: 0.25rem !important;
        background-color: #262730;
        border-radius: 5px;
    }
    .streamlit-expanderContent {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
    }
    
    /* Checkbox alignment */
    div[data-testid="stCheckbox"] {
        margin-top: 5px; 
    }
</style>
"""

