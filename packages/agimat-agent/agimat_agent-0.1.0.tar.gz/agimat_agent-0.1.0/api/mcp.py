from fastapi import HTTPException
from core.apps.mcp.mcp_utils import load_mcp_tools
from core.apps.mcp.model import MCPServerMetadataRequest, MCPServerMetadataResponse
from core.apps.mcp.mcp_utils import INTERNAL_SERVER_ERROR_DETAIL
from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mcp", tags=["mcp"])

@router.post("/metadata", response_model=MCPServerMetadataResponse)
async def mcp_server_metadata(request: MCPServerMetadataRequest):
    """Get information about an MCP server."""
    try:
        # Set default timeout with a longer value for this endpoint
        timeout = 300  # Default to 300 seconds for this endpoint

        # Use custom timeout from request if provided
        if request.timeout_seconds is not None:
            timeout = request.timeout_seconds

        # Load tools from the MCP server using the utility function
        tools = await load_mcp_tools(
            server_type=request.transport,
            command=request.command,
            args=request.args,
            url=request.url,
            env=request.env,
            timeout_seconds=timeout,
        )

        # Create the response with tools
        response = MCPServerMetadataResponse(
            transport=request.transport,
            command=request.command,
            args=request.args,
            url=request.url,
            env=request.env,
            tools=tools,
        )

        return response
    except Exception as e:
        logger.exception(f"Error in MCP server metadata endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="")
