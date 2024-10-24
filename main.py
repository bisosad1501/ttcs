import streamlit as st
from scrape import (
    scrape_website,
    extract_body_content,
    clean_body_content,
    split_dom_content,
)
from parse import parse_with_ollama
from crawl import crawl_website  # Import hàm crawl
import requests  

st.set_page_config(page_title="Bisosad Web Scraper & Crawler", page_icon="🔍")

st.title("🔍 Bisosad Web Scraper & Crawler")

st.markdown("""
### Công cụ thu thập và crawl dữ liệu từ các trang web
Nhập URL của trang web bạn muốn thu thập dữ liệu và mô tả thông tin cần phân tích.
""")

st.sidebar.header("Tùy chọn")
url = st.sidebar.text_input("Nhập URL trang web:", placeholder="Ví dụ: https://example.com")

if st.sidebar.button("Crawl Website"):
    st.write("Đang crawl dữ liệu từ trang web...")
    
    crawled_data = crawl_website(url)

    if crawled_data:
        st.success("Dữ liệu đã được crawl thành công!")
        for i, (content, page_url) in enumerate(crawled_data):
            with st.expander(f"Nội dung trang {i + 1}"):
                st.text_area(f"Nội dung trang {i + 1}", content, height=300)
                st.markdown(f"[Truy cập trang này]({page_url})", unsafe_allow_html=True)  # Thêm liên kết đến trang
    else:
        st.warning("Không tìm thấy dữ liệu nào.")

if st.sidebar.button("Scrape Website"):
    st.write("Đang thu thập dữ liệu từ trang web...")
    
    try:
        result = scrape_website(url)
        body_content = extract_body_content(result)
        cleaned_content = clean_body_content(body_content)

        st.session_state.dom_content = cleaned_content

        with st.expander("Xem nội dung DOM"):
            st.text_area("Nội dung DOM", cleaned_content, height=300)

    except requests.ConnectionError:
        st.error("Kết nối mạng không ổn định. Vui lòng thử lại.")
    except Exception as e:
        st.error(f"Có lỗi xảy ra: {e}")

if "dom_content" in st.session_state:
    parse_description = st.text_area("Mô tả thông tin bạn muốn phân tích:", placeholder="Nhập mô tả tại đây...")

    if st.button("Phân tích Nội dung"):
        if parse_description:
            st.write("Đang phân tích nội dung...")

            dom_chunks = split_dom_content(st.session_state.dom_content)
            try:
                result = parse_with_ollama(dom_chunks, parse_description)
                if result:
                    st.success("Kết quả phân tích:")
                    st.write(result)
                else:
                    st.warning("Không tìm thấy thông tin phù hợp.")
            except Exception as e:
                st.error(f"Có lỗi xảy ra khi phân tích: {e}")