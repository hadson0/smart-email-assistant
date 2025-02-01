import re
from email.header import decode_header
import base64


class EmailPreprocessor:
    HEADERS = [
        'De:', 'Para:', 'Data:', 'Sent:', 
        'From:', 'To:', 'Date:', 'Cc:', 'Bcc:'
    ]

    PATTERNS_TO_REMOVE = [
        r'\d+\s+message[s]?',       # Contagem de mensagens
        r'<[\w\.-]+@[\w\.-]+\.\w+>',  # Emails 
        r'https?://\S+',               # links
        r'\d{2}/\d{2}/\d{4}.*',       # Datas
        r'\w+,\s+\w+\s+\d{1,2},\s+\d{4}\s+at\s+\d{1,2}:\d{2}\s+[AP]M',  # Data Gmail
        r'Gmail.*',                    # menções ao Gmail
        r'\d+/\d+',                     # números de página
        # TODO: Melhorar a lista
    ]

    @staticmethod
    def decode_utf8_text(text: str) -> str:
        """Decodifica texto em UTF-8 se necessário."""
        if '=?UTF-8?B?' in text:
            encoded_text = re.search(r'=\?UTF-8\?B\?(.*?)\?=', text)
            if encoded_text:
                try:
                    decoded_bytes = base64.b64decode(encoded_text.group(1))
                    return decoded_bytes.decode('utf-8')
                except:
                    return text
        return text

    @staticmethod
    def clean_text(text: str) -> str:
        """Limpa o texto."""
        text = ' '.join(text.split())
        text = re.sub(r'\s+([.,])', r'\1', text)
        text = re.sub(r'[$$$$*#`_\->~|]', '', text)
        return text.strip()

    @classmethod
    def preprocess_email(cls, content: str) -> str:
        """Preprocessa o conteúdo do email."""
        for pattern in cls.PATTERNS_TO_REMOVE:
            content = re.sub(pattern, '', content)
            
        lines = content.split('\n')
        processed_lines = []
        subject = None
        
        for line in lines:
            line = line.strip()            
            if not line:
                continue
                
            # Processa o assunto
            if ('Assunto:' in line or 'Subject:' in line) and not subject:
                subject_text = line.replace('Assunto:', '').replace('Subject:', '').strip()
                subject = cls.decode_utf8_text(subject_text)
                continue

            if not subject:
                subject = cls.decode_utf8_text(line)
                continue                
                
            # Ignora linhas de cabeçalho
            if any(header in line for header in cls.HEADERS):
                continue
                
            # Remove as imagens no corpo do texto
            if '[image:' in line or 'image.png' in line:
                continue
                
            processed_lines.append(line)
        
        result = []
        if subject:
            result.append(cls.clean_text(subject))
            result.append('')
        result.extend([cls.clean_text(line) for line in processed_lines])
        
        return '\n'.join(result)