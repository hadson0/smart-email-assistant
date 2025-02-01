from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from .services import EmailClassifier, ResponseGenerator
from .utils import FileHandler, EmailPreprocessor
import re

main = Blueprint('main', __name__)


@main.route('/', methods=['GET'])
def index():
    """Renderiza a página principal."""
    return render_template('index.html', email_content='', classification_result=None, generated_response=None)

@main.route('/classify', methods=['POST'])
def classify_email():
    """Trata requisições de classificação de email."""
    email_content = request.form.get('email_content', '')
    email_content = EmailPreprocessor.preprocess_email(email_content)

    # Validação
    if not validate_email_content(email_content):
        flash('Por favor, forneça o conteúdo do e-mail ou envie um arquivo', 'error')
        return render_template('index.html')

    classification_result = EmailClassifier.classify_email(email_content)

    if 'error' in classification_result:
        flash(classification_result['error'], 'error')
        return render_template('index.html', email_content=email_content)

    return render_template('index.html',
                           email_content=email_content,
                           classification_result=classification_result)


@main.route('/generate-response', methods=['POST'])
def generate_response():
    """Gera uma resposta para o email fornecido."""
    data = request.form

    # Validação
    validation_error = validate_response_params(data)
    if validation_error:
        flash(validation_error, 'error')
        return render_template('index.html', email_content=data.get('email_content', '').strip())

    # Primeiro classifica o email, para evitar casos onde não tem classificação
    classification_result = EmailClassifier.classify_email(
        data['email_content'])
    if 'error' in classification_result:
        flash(classification_result['error'], 'error')
        return render_template('index.html', email_content=data['email_content'])
    
    personality = data.get('personality', '').strip() or 'Seja formal e educado'

    # Gera a resposta
    generated_response = ResponseGenerator.generate_response(
        email_content=data['email_content'],
        personality=personality,
        temperature=float(data.get('temperature', 0.3)),
        category=data.get('category', classification_result['label'])
    )

    return render_template(
        'index.html',
        email_content=data['email_content'],
        classification_result=classification_result,
        generated_response=generated_response
    )


@main.route('/process-file', methods=['POST'])
def process_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'Nenhum arquivo enviado'})

    file = request.files['file']
    if not FileHandler.file_validation(file.filename):
        return jsonify({'success': False, 'error': 'Tipo de arquivo não permitido'})

    success, content = FileHandler.extract_content(file)
    content = EmailPreprocessor.preprocess_email(content)

    return jsonify({
        'success': success,
        'content': content if success else '',
        'error': content if not success else ''
    })


@main.app_errorhandler(404)
def not_found_error(error):
    flash('Página não encontrada.', 'error')
    return render_template('index.html'), 404


@main.app_errorhandler(500)
def internal_error(error):
    flash('Erro interno do servidor.', 'error')
    return render_template('index.html'), 500


@main.app_errorhandler(Exception)
def handle_unexpected_error(error):
    print(error)
    flash('Ocorreu um erro inesperado.', 'error')
    return render_template('index.html'), 500


def validate_email_content(conteudo: str) -> bool:
    """
    Valida o conteúdo do email.
    """
    return bool(conteudo and conteudo.strip())


def validate_response_params(dados: dict) -> str:
    """
    Valida os parâmetros para geração de resposta.

    Args:
        dados (dict): Dicionário com parâmetros da requisição.

    Returns:
        str: Mensagem de erro ou string vazia (sem erro).
    """
    conteudo_email = dados.get('email_content', '')
    if not validate_email_content(conteudo_email):
        return 'Por favor, forneça o conteúdo do e-mail.'

    #personalidade = dados.get('personality', '').strip()
    #if not personalidade:
    #    return 'Por favor, forneça uma descrição da personalidade.'

     #temperatura = dados.get('temperature', 0.7)
    #try:
    #    temperatura = float(temperatura)
    #    if not 0 <= temperatura <= 1:
    #        return 'Temperatura deve estar entre 0 e 1.'
    #except (ValueError, TypeError):
     #   return 'Valor de temperatura inválido.'

    return ''
