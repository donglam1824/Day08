import streamlit as st
from services.chatbot import generate_mock_response
from components.citations import render_citations, render_search_indicator

def render_welcome_screen():
    """Renders the welcome screen when there are no messages"""
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 0; margin-bottom: 1rem;">
            <h1 style="color: var(--primary-color); font-size: 2.2rem; margin-bottom: 10px;">Xin chào! Tôi là Shopee Legal Assistant 👋</h1>
            <p style="font-size: 1.1rem; color: var(--text-color); max-width: 600px; margin: 0 auto;">
                Tôi có thể giúp bạn tìm hiểu các vấn đề pháp lý liên quan đến hoạt động thương mại điện tử trên Shopee.
            </p>
            <div class="legal-disclaimer" style="max-width: 500px; margin: 20px auto;">
                Thông tin cung cấp nhằm mục đích tham khảo và không thay thế tư vấn pháp lý chuyên nghiệp.
            </div>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    st.markdown("<h3 style='margin-top: 20px; margin-bottom: 20px;'>Các câu hỏi thường gặp</h3>", unsafe_allow_html=True)
    
    # Grid of suggestions
    col1, col2 = st.columns(2)
    
    suggestions = [
        ("💰 Thuế & hóa đơn", "Bán hàng trên Shopee có phải đóng thuế không?"),
        ("📦 Đơn hàng", "Người bán có được tự ý hủy đơn hàng không?"),
        ("🔄 Hoàn trả", "Khách trả hàng thì shop có quyền từ chối không?"),
        ("©️ Sở hữu trí tuệ", "Sử dụng hình ảnh thương hiệu khác để bán hàng có hợp pháp không?")
    ]
    
    for i, (title, text) in enumerate(suggestions):
        col = col1 if i % 2 == 0 else col2
        with col:
            # We use a trick with st.button to make the card clickable and trigger a prompt
            if st.button(f"**{title}**\n\n{text}", key=f"sugg_{i}", use_container_width=True):
                st.session_state.topic_prompt = text
                st.rerun()

def render_chat_messages():
    """Renders the chat history"""
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
            # If it's an assistant message, render citations and suggestions if they exist
            if msg["role"] == "assistant":
                if "sources" in msg and msg["sources"]:
                    render_search_indicator(len(msg["sources"]))
                    render_citations(msg["sources"])
                
                # Render suggestions
                if "suggestions" in msg and msg["suggestions"]:
                    st.markdown("<div style='margin-top: 15px;'><strong>Bạn có thể muốn hỏi thêm:</strong></div>", unsafe_allow_html=True)
                    sug_cols = st.columns(len(msg["suggestions"]))
                    for idx, sug in enumerate(msg["suggestions"]):
                        with sug_cols[idx]:
                            if st.button(sug, key=f"sug_btn_{msg['id']}_{idx}"):
                                st.session_state.topic_prompt = sug
                                st.rerun()
                
                # Feedback buttons
                st.markdown(
                    """
                    <div class="feedback-container">
                        <button class="feedback-btn" title="Hữu ích">👍</button>
                        <button class="feedback-btn" title="Chưa hữu ích">👎</button>
                        <button class="feedback-btn" title="Sao chép">📋 Sao chép</button>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )

def process_user_input(prompt: str):
    """Handles new user input, generating and displaying the response"""
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Đang phân tích câu hỏi và tra cứu căn cứ pháp lý..."):
            response_data = generate_mock_response(prompt)
            
        answer = response_data["answer"]
        sources = response_data.get("sources", [])
        suggestions = response_data.get("suggestions", [])
        
        # Display the text response
        st.markdown(answer)
        
        # Display the source indicator and citations
        render_search_indicator(len(sources))
        render_citations(sources)
        
        # Display suggestions
        if suggestions:
            st.markdown("<div style='margin-top: 15px;'><strong>Bạn có thể muốn hỏi thêm:</strong></div>", unsafe_allow_html=True)
            # Cannot use buttons easily immediately after yielding response without rerun
            # So we store them in state to render on next rerun
        
        # Add assistant message to state
        # Create a unique ID for the message to key the suggestion buttons later
        import uuid
        msg_id = str(uuid.uuid4())
        st.session_state.messages.append({
            "id": msg_id,
            "role": "assistant", 
            "content": answer,
            "sources": sources,
            "suggestions": suggestions
        })
        
        # Rerun to render buttons properly
        st.rerun()
