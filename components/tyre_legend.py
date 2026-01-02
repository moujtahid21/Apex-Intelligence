from pathlib import Path
import base64
from .html_component import HTMLComponent


class TyreLegend(HTMLComponent):

    def __init__(self, compounds, assets, height=100):
        # Height is fixed to ensure it fits the single row comfortably
        super().__init__(height=height, scrolling=False)
        self.compounds = compounds
        self.assets = assets

    @staticmethod
    def _img_to_base64(path: str) -> str:
        data = Path(path).read_bytes()
        encoded = base64.b64encode(data).decode()
        return f"data:image/svg+xml;base64,{encoded}"

    def _build_html(self) -> str:
        html = """
        <html>
        <head>
            <style>
                * {
                    box-sizing: border-box;
                }

                body {
                    margin: 0;
                    padding: 0;
                    background: transparent;
                    font-family: "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    overflow: hidden; /* Hide main body scroll */
                }

                .legend-container {
                    display: flex;
                    flex-direction: row;
                    align-items: center;

                    /* KEY FIXES FOR SINGLE ROW */
                    justify-content: flex-start;
                    flex-wrap: nowrap; /* Forces items to stay on one line */
                    overflow-x: auto;  /* Enables horizontal scrolling if they don't fit */

                    gap: 12px;
                    padding: 10px 4px; /* Slight vertical padding for hover effects */
                    width: 100%;

                    /* Hide Scrollbar styling (makes it look like a clean carousel) */
                    -ms-overflow-style: none;  /* IE and Edge */
                    scrollbar-width: none;  /* Firefox */
                }

                /* Hide scrollbar for Chrome/Safari/Opera */
                .legend-container::-webkit-scrollbar {
                    display: none;
                }

                .tire-badge {
                    display: flex;
                    align-items: center;
                    background: #1e1e1e;
                    border: 1px solid #333;
                    border-radius: 6px;
                    padding: 6px 10px; /* Compact padding */

                    /* This ensures the badge doesn't shrink below this size */
                    flex: 0 0 auto; 
                    min-width: 140px; 

                    cursor: default;
                    transition: all 0.2s ease;
                    user-select: none;
                }

                .tire-badge:hover {
                    transform: translateY(-2px);
                    border-color: #555;
                    background: #252525;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                }

                .tire-img {
                    width: 24px; /* Slightly smaller to ensure fit */
                    height: 24px;
                    margin-right: 10px;
                    flex-shrink: 0;
                }

                .tire-info {
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    line-height: 1.1;
                }

                .tire-name {
                    color: #e0e0e0;
                    font-weight: 700;
                    font-size: 12px;
                    letter-spacing: 0.5px;
                    text-transform: uppercase;
                    white-space: nowrap;
                }

                .tire-desc {
                    color: #909090;
                    font-size: 9px;
                    font-weight: 400;
                    white-space: nowrap;
                }
            </style>
        </head>
        <body>
            <div class="legend-container">
        """

        for name, desc in self.compounds:
            src = self._img_to_base64(self.assets[name])
            html += f"""
                <div class="tire-badge" title="{desc}">
                    <img src="{src}" class="tire-img">
                    <div class="tire-info">
                        <div class="tire-name">{name}</div>
                        <div class="tire-desc">{desc}</div>
                    </div>
                </div>
            """

        html += """
            </div>
        </body>
        </html>
        """

        return html

    def show(self):
        self.render(self._build_html())