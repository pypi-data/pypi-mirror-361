import requests
import logging
from typing import Optional, Dict, Any, List, Union

class GraphDBAdapter:
    """
    Adapter for interacting with Ontotext GraphDB via its REST API.

    Capabilities:
        - Connection/authentication management
        - Repository management (create, delete, list, configure)
        - SPARQL endpoint wrappers (SELECT, CONSTRUCT, ASK, UPDATE)
        - Bulk loading of RDF data
        - Transaction support (begin, commit, rollback)
        - Lucene full-text search integration
        - Vector/semantic search (if supported)
        - Federated SPARQL query support
        - Ontology loading
        - Utility methods for version/feature checks
    """
    def __init__(self, url, user=None, password=None, use_https=True):
        """
        Initialize the GraphDBAdapter.

        Args:
            url (str): Base URL of the GraphDB instance.
            user (Optional[str]): Username for authentication.
            password (Optional[str]): Password for authentication.
            use_https (bool): Whether to use HTTPS (default: True).
        """
        self.url = url.rstrip('/')
        self.user = user
        self.password = password
        self.use_https = use_https
        self.session = requests.Session()
        if user and password:
            self.session.auth = (user, password)

    def test_connection(self):
        """
        Test connection to GraphDB by listing repositories.

        Returns:
            bool: True if connection is successful, False otherwise.

        Example:
            >>> adapter = GraphDBAdapter('http://localhost:7200')
            >>> adapter.test_connection()
            True
        """
        try:
            resp = self.session.get(f"{self.url}/rest/repositories")
            resp.raise_for_status()
            return True
        except Exception as e:
            print(f"GraphDB connection failed: {e}")
            return False

    def load_ontology(self, repo_id, ontology_path):
        """
        Load ontology data (Turtle) into the specified repository using SPARQL UPDATE.

        Args:
            repo_id (str): The GraphDB repository ID.
            ontology_path (str): Path to the ontology Turtle file.

        Returns:
            bool: True if ontology loaded successfully, False otherwise.

        Example:
            >>> adapter.load_ontology('myrepo', 'docs/axiusmem_ontology.ttl')
            True
        """
        with open(ontology_path, "r", encoding="utf-8") as f:
            turtle_data = f.read()
        update_query = f"""
        INSERT DATA {{
        {turtle_data}
        }}
        """
        endpoint = f"{self.url}/repositories/{repo_id}/statements"
        headers = {"Content-Type": "application/sparql-update"}
        resp = self.session.post(endpoint, data=update_query.encode("utf-8"), headers=headers)
        resp.raise_for_status()
        return resp.status_code == 204 

    def list_repositories(self) -> List[Dict[str, Any]]:
        """
        List all repositories in the GraphDB instance.

        Returns:
            List[Dict[str, Any]]: List of repository metadata dicts.
        """
        try:
            resp = self.session.get(f"{self.url}/rest/repositories")
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logging.error(f"Failed to list repositories: {e}")
            return []

    def create_repository(self, repo_config: Dict[str, Any]) -> bool:
        """
        Create a new repository with the given configuration.

        Args:
            repo_config (Dict[str, Any]): Repository configuration as a dict (GraphDB expects RDF/XML or config params).

        Returns:
            bool: True if created successfully, False otherwise.
        """
        try:
            headers = {"Content-Type": "application/json"}
            resp = self.session.post(f"{self.url}/rest/repositories", json=repo_config, headers=headers)
            resp.raise_for_status()
            return resp.status_code in (200, 201, 204)
        except Exception as e:
            logging.error(f"Failed to create repository: {e}")
            return False

    def delete_repository(self, repo_id: str) -> bool:
        """
        Delete a repository by ID.

        Args:
            repo_id (str): Repository ID.

        Returns:
            bool: True if deleted successfully, False otherwise.
        """
        try:
            resp = self.session.delete(f"{self.url}/rest/repositories/{repo_id}")
            resp.raise_for_status()
            return resp.status_code in (200, 204)
        except Exception as e:
            logging.error(f"Failed to delete repository {repo_id}: {e}")
            return False

    def set_repository_config(self, repo_id: str, config: Dict[str, Any]) -> bool:
        """
        Update repository configuration.

        Args:
            repo_id (str): Repository ID.
            config (Dict[str, Any]): Configuration parameters.

        Returns:
            bool: True if updated successfully, False otherwise.
        """
        try:
            headers = {"Content-Type": "application/json"}
            resp = self.session.put(f"{self.url}/rest/repositories/{repo_id}", json=config, headers=headers)
            resp.raise_for_status()
            return resp.status_code in (200, 204)
        except Exception as e:
            logging.error(f"Failed to update repository config: {e}")
            return False

    def sparql_select(self, repo_id: str, query: str, infer: bool = True, timeout: int = 60) -> Union[List[Dict[str, Any]], None]:
        """
        Execute a SPARQL SELECT query.

        Args:
            repo_id (str): Repository ID.
            query (str): SPARQL SELECT query string.
            infer (bool): Whether to enable reasoning/inferencing.
            timeout (int): Query timeout in seconds.

        Returns:
            List[Dict[str, Any]]: Query results as a list of dicts, or None on error.
        """
        try:
            params = {"infer": str(infer).lower(), "timeout": timeout}
            headers = {"Accept": "application/sparql-results+json"}
            resp = self.session.post(
                f"{self.url}/repositories/{repo_id}",
                data={"query": query},
                params=params,
                headers=headers,
                timeout=timeout
            )
            resp.raise_for_status()
            return resp.json().get("results", {}).get("bindings", [])
        except Exception as e:
            logging.error(f"SPARQL SELECT failed: {e}")
            return None

    def sparql_construct(self, repo_id: str, query: str, infer: bool = True, timeout: int = 60) -> Optional[str]:
        """
        Execute a SPARQL CONSTRUCT query.

        Args:
            repo_id (str): Repository ID.
            query (str): SPARQL CONSTRUCT query string.
            infer (bool): Whether to enable reasoning/inferencing.
            timeout (int): Query timeout in seconds.

        Returns:
            Optional[str]: RDF data in Turtle format, or None on error.
        """
        try:
            params = {"infer": str(infer).lower(), "timeout": timeout}
            headers = {"Accept": "text/turtle"}
            resp = self.session.post(
                f"{self.url}/repositories/{repo_id}",
                data={"query": query},
                params=params,
                headers=headers,
                timeout=timeout
            )
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            logging.error(f"SPARQL CONSTRUCT failed: {e}")
            return None

    def sparql_ask(self, repo_id: str, query: str, infer: bool = True, timeout: int = 60) -> Optional[bool]:
        """
        Execute a SPARQL ASK query.

        Args:
            repo_id (str): Repository ID.
            query (str): SPARQL ASK query string.
            infer (bool): Whether to enable reasoning/inferencing.
            timeout (int): Query timeout in seconds.

        Returns:
            Optional[bool]: True/False result, or None on error.
        """
        try:
            params = {"infer": str(infer).lower(), "timeout": timeout}
            headers = {"Accept": "application/sparql-results+json"}
            resp = self.session.post(
                f"{self.url}/repositories/{repo_id}",
                data={"query": query},
                params=params,
                headers=headers,
                timeout=timeout
            )
            resp.raise_for_status()
            return resp.json().get("boolean")
        except Exception as e:
            logging.error(f"SPARQL ASK failed: {e}")
            return None

    def sparql_update(self, repo_id: str, update_query: str, timeout: int = 60) -> bool:
        """
        Execute a SPARQL UPDATE query.

        Args:
            repo_id (str): Repository ID.
            update_query (str): SPARQL UPDATE query string.
            timeout (int): Query timeout in seconds.

        Returns:
            bool: True if update succeeded, False otherwise.
        """
        try:
            headers = {"Content-Type": "application/sparql-update"}
            resp = self.session.post(
                f"{self.url}/repositories/{repo_id}/statements",
                data=update_query.encode("utf-8"),
                headers=headers,
                timeout=timeout
            )
            resp.raise_for_status()
            return resp.status_code == 204
        except Exception as e:
            logging.error(f"SPARQL UPDATE failed: {e}")
            return False

    def bulk_load(self, repo_id: str, rdf_path: str, rdf_format: str = "text/turtle") -> bool:
        """
        Bulk load RDF data into the repository using GraphDB's REST API.

        Args:
            repo_id (str): Repository ID.
            rdf_path (str): Path to RDF file.
            rdf_format (str): MIME type (e.g., "text/turtle", "application/rdf+xml").

        Returns:
            bool: True if loaded successfully, False otherwise.
        """
        try:
            with open(rdf_path, "rb") as f:
                data = f.read()
            headers = {"Content-Type": rdf_format}
            resp = self.session.post(
                f"{self.url}/repositories/{repo_id}/statements",
                data=data,
                headers=headers
            )
            resp.raise_for_status()
            return resp.status_code == 204
        except Exception as e:
            logging.error(f"Bulk load failed: {e}")
            return False

    # Transaction support (GraphDB supports transactions via HTTP, but limited)
    def begin_transaction(self, repo_id: str) -> Optional[str]:
        """
        Begin a transaction. Returns transaction ID if supported.

        Args:
            repo_id (str): Repository ID.

        Returns:
            Optional[str]: Transaction ID, or None if not supported/failed.
        """
        try:
            resp = self.session.post(f"{self.url}/repositories/{repo_id}/transactions")
            resp.raise_for_status()
            tx_id = resp.headers.get("location")
            return tx_id
        except Exception as e:
            logging.warning(f"Transaction begin not supported or failed: {e}")
            return None

    def commit_transaction(self, tx_id: str) -> bool:
        """
        Commit a transaction by transaction ID.

        Args:
            tx_id (str): Transaction ID (URL).

        Returns:
            bool: True if committed, False otherwise.
        """
        try:
            resp = self.session.put(f"{tx_id}?action=COMMIT")
            resp.raise_for_status()
            return resp.status_code == 200
        except Exception as e:
            logging.warning(f"Transaction commit failed: {e}")
            return False

    def rollback_transaction(self, tx_id: str) -> bool:
        """
        Rollback a transaction by transaction ID.

        Args:
            tx_id (str): Transaction ID (URL).

        Returns:
            bool: True if rolled back, False otherwise.
        """
        try:
            resp = self.session.put(f"{tx_id}?action=ROLLBACK")
            resp.raise_for_status()
            return resp.status_code == 200
        except Exception as e:
            logging.warning(f"Transaction rollback failed: {e}")
            return False

    # Lucene, vector, and federated search stubs
    def check_repository_exists(self, repo_id: str) -> bool:
        """
        Check if a repository exists in GraphDB.

        Args:
            repo_id (str): Repository ID.

        Returns:
            bool: True if repository exists, False otherwise.
        """
        try:
            resp = self.session.get(f"{self.url}/rest/repositories/{repo_id}")
            return resp.status_code == 200
        except Exception as e:
            logging.error(f"Repository existence check failed: {e}")
            return False

    def get_graphdb_version(self) -> Optional[str]:
        """
        Get the GraphDB server version string.

        Returns:
            Optional[str]: Version string, or None if not available.
        """
        try:
            resp = self.session.get(f"{self.url}/rest/info/version")
            resp.raise_for_status()
            return resp.json().get("version")
        except Exception as e:
            logging.warning(f"Could not retrieve GraphDB version: {e}")
            return None

    def lucene_search(self, repo_id: str, lucene_query: str, field: str = "", limit: int = 10) -> Any:
        """
        Perform a Lucene full-text search using GraphDB's Lucene connector.

        Args:
            repo_id (str): Repository ID.
            lucene_query (str): Lucene query string (e.g., 'text:memory').
            field (str): Field to search (optional).
            limit (int): Maximum number of results.

        Returns:
            Any: Query results (list of bindings or None).

        Example:
            >>> adapter.lucene_search('myrepo', 'memory', field='label', limit=5)
        """
        sparql = f"""
        PREFIX luc: <http://www.ontotext.com/owlim/lucene#>
        SELECT ?s ?score WHERE {{
            ?s luc:search '{lucene_query}' .
            ?s luc:score ?score .
        }} LIMIT {limit}
        """
        return self.sparql_select(repo_id, sparql)

    def vector_search(self, repo_id: str, vector_query: Any, limit: int = 10) -> Any:
        """
        Perform a vector/semantic search if GraphDB supports it (stub if not).

        Args:
            repo_id (str): Repository ID.
            vector_query (Any): Vector or embedding query (format depends on backend).
            limit (int): Maximum number of results.

        Returns:
            Any: Query results or None.
        """
        logging.info("Vector search integration is not implemented; GraphDB support required.")
        return None

    def federated_query(self, repo_id: str, query: str, timeout: int = 60) -> Any:
        """
        Execute a federated SPARQL query (using SERVICE clauses).

        Args:
            repo_id (str): Repository ID.
            query (str): SPARQL query string with SERVICE clause(s).
            timeout (int): Query timeout in seconds.

        Returns:
            Any: Query results or None.
        """
        # This is just a wrapper for sparql_select/construct with federated query support
        return self.sparql_select(repo_id, query, timeout=timeout) 