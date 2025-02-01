import time
import requests

def retry_api_call(
    url,
    backoff_factor= 2,
    total= 4,
    status_forcelist= [403, 429, 500, 502],
    **kwargs
):
    """
    Realiza uma chamada à API com lógica de retry.

    Referência: Adaptado de https://proxidize.com/blog/python-requests-retry/

    Args:
        url: Endpoint da API.
        backoff_factor: Delay exponencial.
        total: Número máximo de tentativas.
        status_forcelist: Códigos de status que devem ter retry.
        **kwargs: Argumentos para a função `requests.request`.

    Returns:
        requests.Response: Objeto de resposta da API ou `None` se todas as tentativas falharem.
    """
    last_response = None

    for attempt in range(total):
        try:
            response = requests.request(url=url, timeout=10, **kwargs)
            
            if response.status_code in status_forcelist:
                delay = backoff_factor ** attempt
                print(f"Tentativa {attempt + 1} falhou com status {response.status_code}. Retentando em {delay} segundos...")
                time.sleep(delay)
                last_response = response
                continue

            return response

        except requests.exceptions.RequestException as e:
            print(f"Requisição falhou: {str(e)}")
            if attempt == total - 1:
                raise e
            delay = backoff_factor ** attempt
            print(f"Retentando em {delay} segundos...")
            time.sleep(delay)

    # Log da última resposta após todas as tentativas
    return last_response