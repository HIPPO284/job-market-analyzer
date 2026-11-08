import webview

WEBSITE_URL = "https://job-market-analyzer-web-hippo.swedencentral.cloudapp.azure.com/"

if __name__ == "__main__":
    webview.create_window(
        "Job Market Analyzer",
        WEBSITE_URL,
        width=1200,
        height=800
    )

    webview.start(gui="edgechromium", debug=False)