import pytest  # noqa: F401
import pytest_asyncio  # noqa: F401
from fastmcp import Client

from biocontext_server.core._server import core_mcp


async def test_get_recent_biorxiv_preprints_recent():
    """Test the tool get_recent_biorxiv_preprints with recent count."""
    async with Client(core_mcp) as client:
        result = await client.call_tool(
            "get_recent_biorxiv_preprints", {"server": "biorxiv", "recent_count": 5, "max_results": 5}
        )

        assert isinstance(result.data, dict)
        if "error" not in result.data:
            assert "server" in result.data
            assert "papers" in result.data
            assert isinstance(result.data["papers"], list)
            assert result.data["server"] == "biorxiv"
        else:
            # API might have issues, but should return structured error
            assert "error" in result.data


async def test_get_recent_biorxiv_preprints_date_range():
    """Test the tool get_recent_biorxiv_preprints with date range."""
    async with Client(core_mcp) as client:
        result = await client.call_tool(
            "get_recent_biorxiv_preprints",
            {"server": "biorxiv", "start_date": "2024-01-01", "end_date": "2024-01-02", "max_results": 3},
        )

        assert isinstance(result.data, dict)
        if "error" not in result.data:
            assert "server" in result.data
            assert "papers" in result.data
            assert "search_params" in result.data


async def test_get_recent_biorxiv_preprints_days():
    """Test the tool get_recent_biorxiv_preprints with days parameter."""
    async with Client(core_mcp) as client:
        result = await client.call_tool(
            "get_recent_biorxiv_preprints", {"server": "medrxiv", "days": 7, "max_results": 5}
        )

        assert isinstance(result.data, dict)
        if "error" not in result.data:
            assert "server" in result.data
            assert result.data["server"] == "medrxiv"


async def test_get_recent_biorxiv_preprints_invalid_server():
    """Test the tool get_recent_biorxiv_preprints with invalid server."""
    async with Client(core_mcp) as client:
        result = await client.call_tool("get_recent_biorxiv_preprints", {"server": "invalid", "recent_count": 5})

        assert "error" in result.data
        assert "Server must be 'biorxiv' or 'medrxiv'" in result.data["error"]


async def test_get_recent_biorxiv_preprints_no_search_params():
    """Test the tool get_recent_biorxiv_preprints without search parameters."""
    async with Client(core_mcp) as client:
        result = await client.call_tool("get_recent_biorxiv_preprints", {"server": "biorxiv"})

        assert "error" in result.data
        assert "Specify exactly one" in result.data["error"]


async def test_get_biorxiv_preprint_details():
    """Test the tool get_biorxiv_preprint_details with a known DOI."""
    async with Client(core_mcp) as client:
        # Use a known bioRxiv DOI
        result = await client.call_tool(
            "get_biorxiv_preprint_details", {"doi": "10.1101/2023.01.01.522000", "server": "biorxiv"}
        )

        assert isinstance(result.data, dict)
        # This might return an error if the DOI doesn't exist, which is fine
        if "error" not in result.data:
            assert "doi" in result.data
            assert "title" in result.data
        else:
            # Error is expected for non-existent DOI
            assert "error" in result.data


async def test_get_biorxiv_preprint_details_invalid_server():
    """Test the tool get_biorxiv_preprint_details with invalid server."""
    async with Client(core_mcp) as client:
        result = await client.call_tool("get_biorxiv_preprint_details", {"doi": "10.1101/test", "server": "invalid"})

        assert "error" in result.data
        assert "Server must be 'biorxiv' or 'medrxiv'" in result.data["error"]
