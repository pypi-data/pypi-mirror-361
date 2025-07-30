from fastmcp import FastMCP
from typing import Annotated, Literal
from pydantic import Field
from .cat import get_funcat_url, Tag

# 初始化 MCP 服务器
# https://gofastmcp.com/servers/tools
mcp = FastMCP(
    name="mcp-server-funcat",
    version="0.1.0",
    instructions="This is a MCP server for fun cat.",
        dependencies=[
        "mcp-server-funcat@git+https://github.com/jlowin/fastmcp.git#subdirectory=mcp-server-funcat",
    ],
)

@mcp.tool(
    description = "Get a cat image URL with text",   
)
def get_cat_url(
    text_to_say: Annotated [str, Field(description="The text(ONLY ENGLISH) you want to show in pic")] = "", 
    tag: Annotated [Tag, Field(description="The tag you like")] = None
) -> str:

    return get_funcat_url(text_to_say, tag)
