import streamlit as st

def render_sidebar():
    """Renders the sidebar components"""
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 20px;">
                <h2 style="color: var(--primary-color); margin-bottom: 5px;">⚖️ Shopee Legal</h2>
                <p style="color: var(--text-secondary); font-size: 0.9em; margin-top: 0;">Trợ lý pháp lý TMĐT</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # New Chat Button
        if st.button("＋ Cuộc trò chuyện mới", use_container_width=True, type="primary"):
            st.session_state.messages = []
            st.session_state.current_topic = None
            st.rerun()
            
        st.markdown("<hr style='margin: 1rem 0;'>", unsafe_allow_html=True)
        
        # History
        st.markdown("### Lịch sử trò chuyện")
        history = [
            "Thuế khi bán hàng trên Shopee",
            "Quy định hoàn trả hàng",
            "Trách nhiệm của người bán",
            "Xuất hóa đơn điện tử",
            "Vi phạm sở hữu trí tuệ"
        ]
        
        for item in history:
            # We use markdown with links or buttons for history
            # For simplicity, using a small button that doesn't look like a primary button
            if st.button(f"💬 {item}", key=f"hist_{item}", help="Xem lại cuộc trò chuyện này"):
                st.toast(f"Đã tải lịch sử: {item}")
                
        st.markdown("<hr style='margin: 1rem 0;'>", unsafe_allow_html=True)
        
        # Topics shortcuts
        st.markdown("### Chủ đề pháp lý")
        st.markdown("<div class='topics-container'>", unsafe_allow_html=True)
        
        topics = [
            ("🏪", "Đăng ký kinh doanh", "Tôi có cần đăng ký kinh doanh khi bán hàng trên Shopee không?"),
            ("💰", "Thuế & hóa đơn", "Bán hàng trên Shopee có phải đóng thuế không?"),
            ("📦", "Đơn hàng & giao nhận", "Shop có được tự ý hủy đơn hàng không?"),
            ("🔄", "Đổi trả & hoàn tiền", "Khách hàng hoàn hàng thì người bán có quyền từ chối không?"),
            ("⚖️", "Tranh chấp", "Shopee có trách nhiệm gì khi xảy ra tranh chấp giữa người mua và người bán?"),
            ("©️", "Sở hữu trí tuệ", "Sử dụng hình ảnh thương hiệu khác để bán hàng có vi phạm không?")
        ]
        
        for icon, title, prompt in topics:
            if st.button(f"{icon} {title}", key=f"topic_{title}"):
                st.session_state.topic_prompt = prompt
                
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Bottom section
        st.markdown("<div style='flex-grow: 1;'></div>", unsafe_allow_html=True)
        st.markdown("<hr style='margin: 2rem 0 1rem 0;'>", unsafe_allow_html=True)
        
        cols = st.columns(2)
        with cols[0]:
            if st.button("⚙️ Cài đặt"):
                st.toast("Mở cài đặt")
        with cols[1]:
            if st.button("❓ Trợ giúp"):
                st.toast("Mở trợ giúp")
                
        st.markdown(
            "<p style='font-size: 0.75rem; color: var(--text-secondary); text-align: center; margin-top: 10px;'>Shopee Legal Assistant v1.0<br>Powered by AI</p>",
            unsafe_allow_html=True
        )
