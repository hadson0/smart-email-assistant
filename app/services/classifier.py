from flask import current_app
import requests
from typing import Dict
from app.utils.retry import retry_api_call
from app.utils.messages import get_user_message
import re


class EmailClassifier:
    """
    Classe responsável pela classificação de emails utilizando a API da Hugging Face.
    """

    # É necessário tratar o conteúdo da label retornada pela API
    LABEL_MAP = {
        'LABEL_0': 'Improdutivo',
        'LABEL_1': 'Produtivo'
    }

    @staticmethod
    def classify_email(content: str) -> Dict[str, float]:
        """
        Classifica o conteúdo de um email como 'Produtivo' ou 'Improdutivo' usando um modelo refinado do DistilBERT da Hugging Face.

        Args:
            content (str): Texto do email.

        Returns:
            dict: Dicionário com a classificação e confiança.
        """

        api_token = current_app.config.get('HUGGINGFACE_API_TOKEN')
        if not api_token:
            return {'error': get_user_message('auth_error')}
        
        content = ' '.join(content.split())

        headers = {"Authorization": f"Bearer {api_token}"}
        data = {"inputs": content}

        try:
            response = retry_api_call(
                url=current_app.config.get('HUGGINGFACE_API_URL'),
                headers=headers,
                json=data,
                method='POST'
            )

            if response.status_code == 200:
                result = response.json()
                classifications = result[0]
                best_match = max(classifications, key=lambda x: x['score'])
                label = EmailClassifier.LABEL_MAP.get(
                    best_match['label'], 'Desconhecido')

                return {
                    'label': label,
                    'confidence': round(best_match['score'] * 100, 2)
                }

            elif response.status_code == 429:
                current_app.logger.warning("Limite de requisições atingido.")
                return {'error': get_user_message('rate_limit')}

            elif response.status_code == 401:
                current_app.logger.error("Falha na autenticação com a API.")
                return {'error': get_user_message('auth_error')}

            else:
                current_app.logger.error(
                    f"Erro na API: Código {response.status_code}")
                return {'error': get_user_message('api_unavailable')}

        except requests.exceptions.ConnectionError:
            current_app.logger.error("Erro de conexão com a API.")
            return {'error': get_user_message('connection_error')}

        except requests.exceptions.Timeout:
            current_app.logger.error("Tempo de resposta da API expirou.")
            return {'error': get_user_message('timeout')}

        except Exception as e:
            current_app.logger.error(f"Erro inesperado: {str(e)}")
            print(str(e))
            return {'error': get_user_message('unexpected_error')}
