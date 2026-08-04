import streamlit as st
import os

# Must be the first Streamlit command
st.set_page_config(
    page_title="Shopee Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

from components.sidebar import render_sidebar
from components.chat import render_welcome_screen, render_chat_messages, process_user_input

def load_css():
    """Loads the custom CSS file"""
    css_path = os.path.join(os.path.dirname(__file__), 'styles', 'custom.css')
    if os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def init_session_state():
    """Initializes session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "topic_prompt" not in st.session_state:
        st.session_state.topic_prompt = None

def main():
    # Load custom styles
    load_css()
    
    # Initialize session state
    init_session_state()
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 20px;">
                <div style="font-size: 2rem;">⚖️</div>
                <div>
                    <h2 style="margin: 0; color: var(--primary-color);">Shopee Legal Assistant</h2>
                    <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">Trợ lý pháp lý thương mại điện tử</p>
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            """
            <div style="display: flex; justify-content: flex-end; align-items: center; height: 100%;">
                <div class="status-indicator">
                    <span class="status-dot"></span> AI đang hoạt động
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
    st.markdown("<hr style='margin: 0 0 1.5rem 0;'>", unsafe_allow_html=True)

    # Render Sidebar
    render_sidebar()
    
    # Main Chat Area
    # If no messages, show welcome screen
    if not st.session_state.messages:
        render_welcome_screen()
    else:
        # Show chat messages
        render_chat_messages()
        
    # Check if a prompt was triggered by a topic/suggestion click
    prompt = None
    if st.session_state.topic_prompt:
        prompt = st.session_state.topic_prompt
        # Reset the triggered prompt
        st.session_state.topic_prompt = None
        
    # User Input
    chat_input = st.chat_input("Nhập câu hỏi pháp lý của bạn... (Ví dụ: 'Shop có phải xuất hóa đơn không?')")
    
    # If user typed something, use that instead
    if chat_input:
        prompt = chat_input
        
    if prompt:
        process_user_input(prompt)
        
    # Global Legal Disclaimer at the bottom
    st.markdown(
        """
        <div style="text-align: center; color: var(--text-secondary); font-size: 0.8rem; margin-top: 30px; padding: 15px;">
            ⚠️ Thông tin trên chỉ mang tính chất tham khảo, không phải ý kiến tư vấn pháp lý chính thức. 
            Đối với các vấn đề quan trọng hoặc tranh chấp cụ thể, bạn nên tham khảo ý kiến luật sư hoặc chuyên gia pháp lý.
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
