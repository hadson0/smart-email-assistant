import requests
from flask import current_app
from typing import Optional
from app.utils import retry_api_call, get_user_message


class ResponseGenerator:
    """
    Classe responsável pela geração de respostas automáticas para emails com a API da OpenAI.
    """

    OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
    MODEL = "gpt-4o-mini"

    @staticmethod
    def generate_response(email_content: str, personality: str, temperature: float) -> Optional[str]:
        """
        Gera uma resposta automática para o email, gerada pelo modelo GPT-4o mini da OpenAI.

        Args:
            email_content (str): Texto do email.
            personality (str): Prompt de personalidade que a resposta deve ter.
            temperature (float): Criatividade (temperatura) da resposta.

        Returns:
            Optional[str]: Resposta gerada.
        """

        api_key = current_app.config.get('OPENAI_API_KEY')
        if not api_key:
            current_app.logger.error("Chave da API OpenAI não configurada.")
            return get_user_message('auth_error')

        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {
            "model": ResponseGenerator.MODEL,
            "messages": [
                {"role": "system", "content": personality},
                {"role": "user", "content": f"Gere uma resposta para este email:\n\n{email_content}"}
            ],
            "temperature": temperature
        }

        try:
            response = retry_api_call(
                url=ResponseGenerator.OPENAI_API_URL,
                headers=headers,
                json=payload,
                method='POST'
            )

            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']

            elif response.status_code == 429:
                current_app.logger.warning("Limite de requisições OpenAI.")
                return get_user_message('rate_limit')

            elif response.status_code == 401:
                current_app.logger.error("Falha na autenticação da OpenAI.")
                return get_user_message('auth_error')

            else:
                current_app.logger.error(f"Erro na API da OpenAI: {response.status_code}")
                return get_user_message('api_unavailable')

        except requests.exceptions.ConnectionError:
            current_app.logger.error("Erro de conexão com a OpenAI.")
            return get_user_message('connection_error')

        except requests.exceptions.Timeout:
            current_app.logger.error("Tempo de resposta da OpenAI expirou.")
            return get_user_message('timeout')

        except Exception as e:
            current_app.logger.error(f"Erro inesperado com a OpenAI: {str(e)}")
            return get_user_message('unexpected_error')
