# __main__.py

import sys
import argparse
from mcp_server_funcat.server import mcp

def main():
     # 启动 MCP 服务器
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", choices=["stdio", "sse", "http"], default="stdio")
    parser.add_argument("--port", type=int, default=8900, help="服务器端口号")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="服务器主机地址")
    args = parser.parse_args()

    if args.transport == "http":
        sys.stdout.write("Starting MCP http server...\n")
        sys.stdout.flush()
        mcp.run(transport="http", host=args.host, port=args.port, path="/mcp")
    elif args.transport == "sse":
        # 对于 stdio 和 sse 传输方式，直接运行
        sys.stdout.write("Starting MCP sse server...\n")
        sys.stdout.flush()
        mcp.run(transport="sse", host=args.host, port=args.port, path="/sse")
    else:
        mcp.run(transport="stdio")

if __name__ == "__main__":
    main()