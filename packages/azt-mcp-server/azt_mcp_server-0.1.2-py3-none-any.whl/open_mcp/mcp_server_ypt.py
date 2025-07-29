import requests
from mcp.server.fastmcp import FastMCP

API_URL = "https://esbmp.easysign.cn/gateway/UUMS/test/getApiInfo"

mcp = FastMCP("open-mcp")

@mcp.tool()
def _get_test() -> str:
        return "111"

def main():
    mcp.run()
