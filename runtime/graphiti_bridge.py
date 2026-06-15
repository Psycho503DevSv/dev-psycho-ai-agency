import logging
import os
import asyncio
from datetime import datetime
from typing import List, Optional
from config import settings

logger = logging.getLogger("GraphitiBridge")

class GraphitiBridge:
    def __init__(self):
        self.uri = settings.NEO4J_URI
        self.user = settings.NEO4J_USER
        self.password = settings.NEO4J_PASSWORD
        self.openai_key = settings.OPENAI_API_KEY
        self.enabled = settings.USE_GRAPHITI
        self._graphiti = None
        self._initialized = False

    async def initialize(self) -> bool:
        """Inicializa la conexión con Graphiti y Neo4j, construyendo índices y restricciones."""
        if not self.enabled:
            logger.info("Graphiti está desactivado por configuración de usuario (USE_GRAPHITI=False).")
            return False
        
        try:
            # Importación dinámica para evitar errores si no está instalada la librería
            from graphiti_core import Graphiti
            
            # Validar variables de entorno OpenAI requeridas por Graphiti
            if self.openai_key:
                os.environ["OPENAI_API_KEY"] = self.openai_key
            elif not os.getenv("OPENAI_API_KEY"):
                logger.warning("OPENAI_API_KEY no está configurada. Graphiti requiere OpenAI para la extracción de entidades.")
                return False

            # Inicializar la instancia de Graphiti
            self._graphiti = Graphiti(
                uri=self.uri,
                user=self.user,
                password=self.password
            )
            
            # Construir índices y restricciones en Neo4j
            await self._graphiti.build_indices_and_constraints()
            self._initialized = True
            logger.info("Puente Graphiti inicializado correctamente y conectado a Neo4j.")
            return True
        except Exception as e:
            logger.error(f"Error inicializando el puente de Graphiti: {str(e)}", exc_info=True)
            self._initialized = False
            return False

    async def add_episode(self, content: str, name: str = "activity_log", source_description: str = "system_event") -> bool:
        """Registra un nuevo episodio semántico en la base de datos de grafos."""
        if not self._initialized or not self._graphiti:
            logger.debug("Graphiti no está inicializado. Saltando registro de episodio.")
            return False
        try:
            from graphiti_core.nodes import EpisodeType
            await self._graphiti.add_episode(
                name=name,
                episode_body=content,
                source=EpisodeType.text,
                source_description=source_description,
                reference_time=datetime.now()
            )
            logger.info(f"Episodio '{name}' añadido exitosamente a Graphiti.")
            return True
        except Exception as e:
            logger.error(f"Error al añadir episodio a Graphiti: {str(e)}")
            return False

    async def search_context(self, query: str) -> List[str]:
        """Busca hechos semánticos y relaciones en base a una consulta en lenguaje natural."""
        if not self._initialized or not self._graphiti:
            logger.debug("Graphiti no está inicializado. No se puede consultar contexto semántico.")
            return []
        try:
            results = await self._graphiti.search(query=query)
            facts = []
            for res in results:
                if hasattr(res, "fact"):
                    facts.append(res.fact)
                elif isinstance(res, dict) and "fact" in res:
                    facts.append(res["fact"])
            return facts
        except Exception as e:
            logger.error(f"Error al consultar contexto semántico en Graphiti: {str(e)}")
            return []

# Instancia global única
bridge = GraphitiBridge()
