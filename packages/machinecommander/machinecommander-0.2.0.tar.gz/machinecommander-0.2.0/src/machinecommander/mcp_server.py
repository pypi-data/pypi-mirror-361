from mcp.server.fastmcp import FastMCP
import os
import requests

mcp = FastMCP("MachineCommander")

@mcp.tool()
def get_construction_machines_data(question: str) -> dict:
    """MachineCommander is a global system to manage all the construction machines working on construction projects. Use this tool to extract the data of construction machines and projects, and to answer construction related questions. The returned value includes a "result" field, which can be a table (a list of rows) or an answer (a string)."""
    url = f"https://gpt-agent.zhgcloud.com/paipai_mcp/{question}"
    try:
        response = requests.post(
            url,
            headers={"Authorization": "Basic emVhaG8tZ3B0LWFnZW50LWw0OnplYWhvXzkzMjQ2"},
            json={
                "APP_KEY": os.environ.get("APP_KEY", ""),
                "APP_SECRET": os.environ.get("APP_SECRET", "")
            }
        )
        response.raise_for_status()
        result = response.json()
    except Exception as e:
        result = {"result": f"请求失败: {str(e)}"}
    return result

@mcp.tool()
def manage_construction_machines(order: str) -> dict:
    """MachineCommander is a global system to manage all the construction machines working on construction projects. Use this tool to send orders to the construction machines."""
    return {"result": "nop"}

# Start the server
def main():
    mcp.run(transport="stdio")
