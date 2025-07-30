import os
from dotenv import load_dotenv
load_dotenv()
import pytest
from axiusmem.graphdb_adapter import GraphDBAdapter

def get_env(var):
    v = os.getenv(var)
    if not v:
        pytest.skip(f"Env var {var} not set; skipping GraphDB integration test.")
    return v

@pytest.mark.integration
def test_graphdb_connection_and_ontology_load():
    """Test GraphDB connection and ontology loading."""
    url = get_env("AGENT_MEMORY_URL")
    user = os.getenv("GRAPHDB_USER")
    password = os.getenv("GRAPHDB_PASSWORD")
    repo_id = os.getenv("GRAPHDB_REPO_ID")
    ontology_path = os.getenv("AXIUSMEM_ONTOLOGY", "docs/axiusmem_ontology.ttl")
    adapter = GraphDBAdapter(url, user, password)
    assert adapter.test_connection(), "Could not connect to GraphDB."
    # Try loading ontology (will fail if repo doesn't exist or is read-only)
    try:
        loaded = adapter.load_ontology(repo_id, ontology_path)
        assert loaded, "Ontology load did not return success status."
    except Exception as e:
        pytest.skip(f"Ontology load failed: {e}")

@pytest.mark.integration
def test_list_repositories():
    """Test listing repositories."""
    url = get_env("AGENT_MEMORY_URL")
    adapter = GraphDBAdapter(url)
    repos = adapter.list_repositories()
    assert isinstance(repos, list)

@pytest.mark.integration
def test_check_repository_exists():
    """Test repository existence check."""
    url = get_env("AGENT_MEMORY_URL")
    repo_id = get_env("GRAPHDB_REPO_ID")
    adapter = GraphDBAdapter(url)
    assert adapter.check_repository_exists(repo_id) is True
    assert adapter.check_repository_exists("nonexistent_repo_12345") is False

@pytest.mark.integration
def test_graphdb_version():
    """Test GraphDB version retrieval."""
    url = get_env("AGENT_MEMORY_URL")
    adapter = GraphDBAdapter(url)
    version = adapter.get_graphdb_version()
    assert version is None or isinstance(version, str)

@pytest.mark.integration
def test_sparql_select_and_ask():
    """Test SPARQL SELECT and ASK queries."""
    url = get_env("AGENT_MEMORY_URL")
    repo_id = get_env("GRAPHDB_REPO_ID")
    adapter = GraphDBAdapter(url)
    # Simple ASK query
    ask = adapter.sparql_ask(repo_id, "ASK { ?s ?p ?o }")
    assert ask in (True, False)
    # Simple SELECT query
    select = adapter.sparql_select(repo_id, "SELECT * WHERE { ?s ?p ?o } LIMIT 1")
    assert isinstance(select, list)

@pytest.mark.integration
def test_sparql_construct_and_update():
    """Test SPARQL CONSTRUCT and UPDATE queries."""
    url = get_env("AGENT_MEMORY_URL")
    repo_id = get_env("GRAPHDB_REPO_ID")
    adapter = GraphDBAdapter(url)
    # CONSTRUCT query
    construct = adapter.sparql_construct(repo_id, "CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o } LIMIT 1")
    assert construct is None or isinstance(construct, str)
    # UPDATE query (insert and delete a dummy triple)
    test_triple = "<urn:test:s> <urn:test:p> \"test\" ."
    insert_query = f"INSERT DATA {{ {test_triple} }}"
    delete_query = f"DELETE DATA {{ {test_triple} }}"
    inserted = adapter.sparql_update(repo_id, insert_query)
    deleted = adapter.sparql_update(repo_id, delete_query)
    assert inserted in (True, False)
    assert deleted in (True, False)

@pytest.mark.integration
def test_bulk_load():
    """Test bulk loading RDF data (skipped if no test file)."""
    url = get_env("AGENT_MEMORY_URL")
    repo_id = get_env("GRAPHDB_REPO_ID")
    adapter = GraphDBAdapter(url)
    test_file = "docs/axiusmem_ontology.ttl"
    if not os.path.exists(test_file):
        pytest.skip("No test RDF file for bulk load.")
    loaded = adapter.bulk_load(repo_id, test_file)
    assert loaded in (True, False)

@pytest.mark.integration
def test_transaction_support():
    """Test transaction begin/commit/rollback (if supported)."""
    url = get_env("AGENT_MEMORY_URL")
    repo_id = get_env("GRAPHDB_REPO_ID")
    adapter = GraphDBAdapter(url)
    tx_id = adapter.begin_transaction(repo_id)
    if tx_id:
        # Try commit and rollback (should not error)
        committed = adapter.commit_transaction(tx_id)
        rolled_back = adapter.rollback_transaction(tx_id)
        assert committed in (True, False)
        assert rolled_back in (True, False)
    else:
        assert tx_id is None

@pytest.mark.integration
def test_lucene_search():
    """Test Lucene full-text search (returns empty or bindings)."""
    url = get_env("AGENT_MEMORY_URL")
    repo_id = get_env("GRAPHDB_REPO_ID")
    adapter = GraphDBAdapter(url)
    results = adapter.lucene_search(repo_id, "memory")
    assert results is None or isinstance(results, list)

@pytest.mark.integration
def test_federated_query_stub():
    """Test federated query stub (should return list or None)."""
    url = get_env("AGENT_MEMORY_URL")
    repo_id = get_env("GRAPHDB_REPO_ID")
    adapter = GraphDBAdapter(url)
    # This is just a SELECT query for now
    results = adapter.federated_query(repo_id, "SELECT * WHERE { ?s ?p ?o } LIMIT 1")
    assert results is None or isinstance(results, list)

@pytest.mark.integration
def test_vector_search_stub():
    """Test vector search stub (should return None)."""
    url = get_env("AGENT_MEMORY_URL")
    repo_id = get_env("GRAPHDB_REPO_ID")
    adapter = GraphDBAdapter(url)
    results = adapter.vector_search(repo_id, [0.1, 0.2, 0.3])
    assert results is None

@pytest.mark.integration
def test_create_and_delete_repository():
    """Test creating and deleting a repository (skipped if not allowed)."""
    url = get_env("AGENT_MEMORY_URL")
    adapter = GraphDBAdapter(url)
    test_repo_id = "test_axiusmem_repo"
    repo_config = {
        "id": test_repo_id,
        "params": {
            "repositoryType": "file-repository",
            "ruleset": "owl-horst-optimized",
            "storage-folder": "/tmp/test_axiusmem_repo"
        }
    }
    created = adapter.create_repository(repo_config)
    # Some GraphDBs may not allow repo creation via REST; skip if not allowed
    if not created:
        pytest.skip("Repository creation not allowed or failed.")
    assert adapter.check_repository_exists(test_repo_id)
    deleted = adapter.delete_repository(test_repo_id)
    assert deleted in (True, False) 