import logging
from fastmcp import FastMCP
from mcp.server import Server
from starlette.requests import Request
from starlette.applications import Starlette
from mcp.server.sse import SseServerTransport
from starlette.routing import Mount, Route


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize FastMCP server
app = FastMCP("test2")
started: bool = False

@app.tool(description="Return num1 (even) to the power of num2")
async def even_exponent(num1: int, num2: int) -> str:
    logging.info(f"Finding {num1}^{num2}")
    """
    Return an even number num1 to the power of num2

    Args:
        num1: the base to raise by num2
        num1: the exponent to raise num1 to

    Returns:
        List of dictionaries containing status information
    """

    return num1 ** num2


def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can serve the provided mcp server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,  # noqa: SLF001
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

def startup():
    global started
    
    if started:
        return

    started = True
    try:
        app.run(transport="streamable-http", host="0.0.0.0", port=8092)
    except KeyboardInterrupt:
        pass
    finally:
        logging.info('Server test_server_2 successfully shut down.')

if __name__ == '__main__':
    startup()
