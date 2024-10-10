import streamlit as st
from scrape import (
    scrape_website,
    extract_body_content,
    clean_body_content,
    split_dom_content,
)
from parse import parse_with_ollama
import requests  


st.set_page_config(page_title="Bisosad Web Scraper", page_icon="🔍")


st.title("🔍 Bisosad Web Scraper")


st.markdown("""
### Công cụ thu thập dữ liệu từ các trang web
Nhập URL của trang web bạn muốn thu thập dữ liệu và mô tả thông tin cần phân tích.
""")


st.sidebar.header("Tùy chọn")
url = st.sidebar.text_input("Nhập URL trang web:", placeholder="Ví dụ: https://example.com")

if st.sidebar.button("Thu thập Dữ liệu"):
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