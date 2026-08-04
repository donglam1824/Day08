import streamlit as st

def render_citations(sources: list):
    """
    Renders citation cards based on the provided sources list.
    """
    if not sources:
        return
        
    st.markdown("<div style='margin-top: 1.5rem; margin-bottom: 0.5rem;'><strong>Nguồn tham khảo</strong></div>", unsafe_allow_html=True)
    
    # We can use columns to display them nicely
    cols = st.columns(min(len(sources), 2))
    
    for i, source in enumerate(sources):
        col = cols[i % 2]
        
        title = source.get("title", "Nguồn pháp lý")
        authority = source.get("authority", "Cơ quan ban hành")
        article = source.get("article", "")
        url = source.get("url", "#")
        
        card_html = f"""
        <div class="citation-card">
            <div class="citation-title">📄 {title}</div>
            <div class="citation-meta">{authority}</div>
            <div class="citation-meta" style="margin-bottom: 8px;">{article}</div>
            <a href="{url}" class="citation-link" target="_blank">[Xem nguồn]</a>
        </div>
        """
        col.markdown(card_html, unsafe_allow_html=True)

def render_search_indicator(num_sources: int):
    """
    Renders a small indicator that sources were searched.
    """
    if num_sources > 0:
        st.markdown(
            f"""
            <div class="source-badge">
                📚 {num_sources} nguồn pháp lý được sử dụng
            </div>
            """, 
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div class="source-badge">
                🔎 Đã tra cứu cơ sở pháp lý chung
            </div>
            """, 
            unsafe_allow_html=True
        )
