import logging
import json
import os
import requests
from typing import List, Dict, Any
from config import settings

logger = logging.getLogger("ContextCompressor")

class ContextCompressor:
    def __init__(self, token_limit: int = 10000):
        self.token_limit = token_limit

    def estimate_tokens(self, text: str) -> int:
        """Estimación rápida y conservadora del conteo de tokens (1 token ~ 4 caracteres)."""
        return len(text) // 4

    def compress_history(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Evalúa el tamaño del historial. Si supera el límite de tokens,
        condensa los turnos intermedios del chat usando el LLM (NVIDIA NIM o OpenAI)
        manteniendo intactas las instrucciones del sistema y el último turno del usuario.
        """
        system_msg = None
        user_initial = None
        interactive_turns = []

        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg
            elif len(interactive_turns) == 0 and msg["role"] == "user":
                user_initial = msg
            else:
                interactive_turns.append(msg)

        if not interactive_turns:
            return messages

        # Calcular tokens aproximados de los turnos interactivos
        total_chars = sum(len(msg["content"]) for msg in interactive_turns)
        estimated_tokens = total_chars // 4

        if estimated_tokens < self.token_limit:
            return messages

        logger.info(f"Historial superó el umbral ({estimated_tokens} tokens estimados). Iniciando compresión de contexto...")

        # Enviar aviso al dashboard en vivo si está disponible
        try:
            from runtime.dashboard import add_dashboard_log
            add_dashboard_log(f"[ContextCompressor] Comprimiendo {estimated_tokens} tokens de historial...")
        except Exception:
            pass

        # Preparar un prompt para resumir la conversación anterior
        summary_prompt = (
            "Eres un agente de compresión de contexto de alto rendimiento. "
            "A continuación se presenta un historial de interacción entre un desarrollador y varios sub-agentes del sistema operativo.\n"
            "Tu tarea es resumir esta conversación en un reporte técnico corto y super denso de Markdown, indicando:\n"
            "1. Qué tareas y archivos se crearon o modificaron.\n"
            "2. El estado actual de los últimos comandos ejecutados.\n"
            "3. Cualquier error detectado y qué queda pendiente.\n"
            "NO omitas nombres de archivos, funciones ni fragmentos de código cruciales. Sé sumamente conciso.\n\n"
            "=== HISTORIAL A COMPRIMIR ===\n"
        )

        for msg in interactive_turns[:-1]: # Excluimos el último mensaje para mantener la última directiva intacta
            summary_prompt += f"{msg['role'].upper()}: {msg['content']}\n"

        # Llamar al LLM para resumir
        try:
            summary = self._call_llm_for_summary(summary_prompt)
            logger.info("Compresión completada con éxito.")
            
            # Re-ensamblar mensajes con el resumen intermedio inyectado
            compressed_messages = []
            if system_msg:
                compressed_messages.append(system_msg)
            if user_initial:
                compressed_messages.append(user_initial)
                
            compressed_messages.append({
                "role": "user",
                "content": f"=== RESUMEN DE CONTEXTO ANTERIOR (COMPRIMIDO) ===\n{summary}"
            })
            
            # Mantener el último turno del usuario intacto
            if interactive_turns:
                compressed_messages.append(interactive_turns[-1])
                
            return compressed_messages

        except Exception as e:
            logger.error(f"Error comprimiendo el historial de contexto: {str(e)}")
            return messages

    def _call_llm_for_summary(self, prompt: str) -> str:
        """Llamada directa de bajo nivel para obtener el resumen del LLM."""
        nvidia_key = getattr(settings, "NVIDIA_API_KEY", "")
        openai_key = getattr(settings, "OPENAI_API_KEY", "")

        if nvidia_key:
            api_url = "https://integrate.api.nvidia.com/v1/chat/completions"
            api_key = nvidia_key
            model_name = "meta/llama-3.1-8b-instruct"
        elif openai_key:
            api_url = "https://api.openai.com/v1/chat/completions"
            api_key = openai_key
            model_name = "gpt-4o-mini"
        else:
            return "Modo Simulación: No se pudo resumir por falta de API keys."

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": "Eres un asistente de compresión de contexto rápido y denso."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1
        }

        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
