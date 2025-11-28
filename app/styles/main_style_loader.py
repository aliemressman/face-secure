import streamlit as st
import os

def load_css(file_path):
    """CSS dosyasını yükler ve Streamlit'e uygular"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"CSS dosyası bulunamadı: {file_path}")

def load_html_component(file_path, component_name=None):
    """HTML componentini yükler"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        if component_name:
            # Belirli bir component'i ayıklama işlemi yapılabilir
            # Örneğin: <!-- START: component_name --> ile <!-- END: component_name --> arasındaki kısmı alma
            return html_content
        
        return html_content
    except FileNotFoundError:
        st.error(f"HTML dosyası bulunamadı: {file_path}")
        return ""

def get_component_by_class(html_content, class_name):
    """HTML içerikten belirli class'a sahip elementi döner"""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    element = soup.find(class_=class_name)
    return str(element) if element else ""