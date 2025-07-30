import argparse

def main():
    parser = argparse.ArgumentParser(description='VectorX MCP Server')
    parser.add_argument('--transport', 
                        choices=['stdio', 'sse', 'streamable-http'], 
                       default='stdio')
    parser.add_argument('--port', type=int, 
                        default=8000)
    
    parser.add_argument('--host', type=str,
                        default='127.0.0.1')
    
    args = parser.parse_args()

    from mcp_server_vecx.server import mcp

    if args.transport == 'stdio':
        mcp.run(transport='stdio')
    elif args.transport == 'sse':
        mcp.run(transport='sse', host=args.host, port=args.port)
    elif args.transport == 'streamable-http':
        mcp.run(transport='streamable-http', host=args.host, port=args.port)

if __name__=="__main__":
    main()