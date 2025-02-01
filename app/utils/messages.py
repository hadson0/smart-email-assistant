USER_MESSAGES = {
    'default': 'Ocorreu um erro inesperado. Por favor, tente novamente mais tarde.',
    'api_unavailable': 'Se for a sua primeira sessão, por favor, tente novamente em alguns instantes.',
    'rate_limit': 'Muitas solicitações foram feitas. Por favor, aguarde alguns instantes antes de tentar novamente.',
    'timeout': 'O serviço está demorando para responder. Por favor, tente novamente.',
    'auth_error': 'Estamos com problemas no serviço.',
    'connection_error': 'Verifique a sua conexão e tente novamente.',
}

def get_user_message(error_type: str = 'default') -> str:
    """Retorna uma mensagem de erro personalizada ao usuário."""
    return USER_MESSAGES.get(error_type, USER_MESSAGES['default'])