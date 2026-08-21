import os
import logging
from typing import Optional
from .causal_engine import causal_engine

logger = logging.getLogger("caios.neo4j")

def sync_causal_graphs_to_neo4j(
    uri: str = "bolt://localhost:7687",
    user: str = "neo4j",
    password: str = "caios_causal_pass"
) -> bool:
    """
    Syncs all CAIOS Causal Graphs into the active Neo4j graph database.
    Creates CausalNode labels, properties, and directed :CAUSES relationships.
    """
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        with driver.session() as session:
            # Clear existing test nodes
            session.run("MATCH (n:CausalNode) DETACH DELETE n")
            
            for domain_id, graph in causal_engine.domains.items():
                # 1. Create Nodes
                for node in graph.nodes:
                    session.run(
                        """
                        MERGE (n:CausalNode {id: $id, domain: $domain})
                        SET n.label = $label,
                            n.node_type = $node_type,
                            n.baseline_value = $baseline_value,
                            n.unit = $unit,
                            n.description = $description
                        """,
                        id=f"{domain_id}_{node.id}",
                        domain=domain_id,
                        label=node.label,
                        node_type=node.node_type,
                        baseline_value=node.baseline_value,
                        unit=node.unit,
                        description=node.description
                    )

                # 2. Create Directed Causal Edges
                for edge in graph.edges:
                    session.run(
                        """
                        MATCH (src:CausalNode {id: $src_id})
                        MATCH (tgt:CausalNode {id: $tgt_id})
                        MERGE (src)-[r:CAUSES {edge_type: $edge_type}]->(tgt)
                        SET r.weight = $weight,
                            r.confidence = $confidence
                        """,
                        src_id=f"{domain_id}_{edge.source}",
                        tgt_id=f"{domain_id}_{edge.target}",
                        edge_type=edge.edge_type,
                        weight=edge.weight,
                        confidence=edge.confidence
                    )
            
            logger.info("Successfully synced all CAIOS causal graphs to Neo4j database.")
            driver.close()
            return True
            
    except Exception as e:
        logger.warning(f"Neo4j sync skipped (database offline or loading): {e}")
        return False

if __name__ == "__main__":
    success = sync_causal_graphs_to_neo4j()
    print("Neo4j Database Causal Seed Success:", success)
