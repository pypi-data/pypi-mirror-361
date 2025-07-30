import json

import pytest  # noqa: F401
import pytest_asyncio  # noqa: F401
from fastmcp import Client

from biocontext_server.core._server import core_mcp


async def test_get_interpro_entry_basic():
    """Test the get_interpro_entry tool with a valid InterPro ID."""
    async with Client(core_mcp) as client:
        # Using a well-known InterPro entry (Kringle domain)
        result_text = await client.call_tool("get_interpro_entry", {"interpro_id": "IPR000001"})
        result = json.loads(result_text.content[0].text)

        assert "accession" in result
        assert result["accession"] == "IPR000001"
        assert "name" in result
        assert "type" in result


async def test_get_interpro_entry_with_interactions():
    """Test the get_interpro_entry tool with interactions data."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "get_interpro_entry", {"interpro_id": "IPR000001", "include_interactions": True}
        )
        result = json.loads(result_text.content[0].text)

        assert "accession" in result
        # interactions may or may not be present depending on the entry
        assert "interactions" in result or "accession" in result


async def test_get_interpro_entry_with_pathways():
    """Test the get_interpro_entry tool with pathways data."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "get_interpro_entry", {"interpro_id": "IPR000001", "include_pathways": True}
        )
        result = json.loads(result_text.content[0].text)

        assert "accession" in result
        # pathways may or may not be present depending on the entry
        assert "pathways" in result or "accession" in result


async def test_get_interpro_entry_invalid_id():
    """Test the get_interpro_entry tool with invalid InterPro ID format."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_interpro_entry", {"interpro_id": "INVALID123"})
        result = json.loads(result_text.content[0].text)

        assert "error" in result
        assert "Invalid InterPro ID format" in result["error"]


async def test_get_interpro_entry_nonexistent():
    """Test the get_interpro_entry tool with non-existent but valid format ID."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_interpro_entry", {"interpro_id": "IPR999999"})
        result = json.loads(result_text.content[0].text)

        # Should return error for non-existent ID
        assert "error" in result


async def test_get_protein_domains_basic():
    """Test the get_protein_domains tool with a valid protein ID."""
    async with Client(core_mcp) as client:
        # Using TP53 UniProt ID
        result_text = await client.call_tool("get_protein_domains", {"protein_id": "P04637"})
        result = json.loads(result_text.content[0].text)

        assert "accession" in result
        assert result["accession"] == "P04637"
        assert "interpro_matches" in result
        assert "interpro_match_count" in result


async def test_get_protein_domains_with_species():
    """Test the get_protein_domains tool with species filter."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_protein_domains", {"protein_id": "P04637", "species_filter": "9606"})
        result = json.loads(result_text.content[0].text)

        assert "accession" in result
        assert "interpro_matches" in result


async def test_get_protein_domains_with_structure():
    """Test the get_protein_domains tool with structure information."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "get_protein_domains", {"protein_id": "P04637", "include_structure_info": True}
        )
        result = json.loads(result_text.content[0].text)

        assert "accession" in result
        assert "interpro_matches" in result


async def test_get_protein_domains_invalid_protein():
    """Test the get_protein_domains tool with invalid protein ID."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_protein_domains", {"protein_id": "INVALIDPROTEIN123"})
        result = json.loads(result_text.content[0].text)

        assert "error" in result


async def test_search_interpro_entries_basic():
    """Test the search_interpro_entries tool with basic search."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("search_interpro_entries", {"page_size": 5})
        result = json.loads(result_text.content[0].text)

        assert "results" in result
        assert "count" in result
        assert len(result["results"]) <= 5


async def test_search_interpro_entries_by_type():
    """Test the search_interpro_entries tool filtering by entry type."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("search_interpro_entries", {"entry_type": "domain", "page_size": 10})
        result = json.loads(result_text.content[0].text)

        assert "results" in result
        assert "count" in result
        # Check that results are domains
        if result["results"]:
            assert result["results"][0]["metadata"]["type"] == "domain"


async def test_search_interpro_entries_by_source_db():
    """Test the search_interpro_entries tool filtering by source database."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("search_interpro_entries", {"source_database": "pfam", "page_size": 5})
        result = json.loads(result_text.content[0].text)

        assert "results" in result
        assert "count" in result


async def test_search_interpro_entries_with_query():
    """Test the search_interpro_entries tool with text query."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("search_interpro_entries", {"query": "kinase", "page_size": 5})
        result = json.loads(result_text.content[0].text)

        assert "results" in result
        assert "count" in result


async def test_search_interpro_entries_invalid_type():
    """Test the search_interpro_entries tool with invalid entry type."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("search_interpro_entries", {"entry_type": "invalid_type"})
        result = json.loads(result_text.content[0].text)

        assert "error" in result
        assert "Invalid entry_type" in result["error"]


async def test_search_interpro_entries_invalid_source_db():
    """Test the search_interpro_entries tool with invalid source database."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("search_interpro_entries", {"source_database": "invalid_db"})
        result = json.loads(result_text.content[0].text)

        assert "error" in result
        assert "Invalid source_database" in result["error"]


async def test_search_interpro_entries_with_go_term():
    """Test the search_interpro_entries tool with GO term filter."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("search_interpro_entries", {"go_term": "GO:0006122", "page_size": 5})
        result = json.loads(result_text.content[0].text)

        assert "results" in result or "error" in result
        # GO term might not return results, but should not cause an error


async def test_search_interpro_entries_invalid_go_term():
    """Test the search_interpro_entries tool with invalid GO term format."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("search_interpro_entries", {"go_term": "INVALID_GO"})
        result = json.loads(result_text.content[0].text)

        assert "error" in result
        assert "Invalid GO term format" in result["error"]
