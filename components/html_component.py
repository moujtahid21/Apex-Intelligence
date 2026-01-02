import streamlit as st
import streamlit.components.v1 as components

class HTMLComponent:
    """
    Base Class for Sandbox HTML Components
    """

    def __init__(self, height=200, scrolling=False):
        self.height = height
        self.scrolling = scrolling

    def render(self, html: str):
        components.html(html,
                        height=self.height,
                        scrolling=self.scrolling
        )
