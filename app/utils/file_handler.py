import email
import PyPDF2


class FileHandler:
    """
    Lida com diferentes tipos de arquivos para extração de conteúdo de e-mails.
    Extensões suportadas: .txt, .pdf e .eml.
    """

    @staticmethod
    def file_validation(filename: str) -> bool:
        """Verifica se a extensão do arquivo é suportada."""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'txt', 'pdf', 'eml'}

    @staticmethod
    def extract_content(file):
        """
        Extrai o conteúdo do email de diferentes arquivos.
        Extensões suportadas: .txt, .pdf e .eml.

        Args:
            file (FileStorage): Objeto de arquivo enviado.

        Returns:
            Tuple[bool, str]: Status de sucesso e conteúdo/mensagem de erro.
        """
        try:
            extension = file.filename.rsplit('.', 1)[1].lower()

            if extension == 'txt':
                return FileHandler._handle_txt(file)
            elif extension == 'pdf':
                return FileHandler._handle_pdf(file)
            elif extension == 'eml':
                return FileHandler._handle_eml(file)
            else:
                return False, 'Tipo de arquivo não suportado.'

        except Exception:
            return False, 'Erro ao processar o arquivo.'

    @staticmethod
    def _handle_txt(file):
        """Processa arquivos .txt."""
        try:
            content = file.read().decode('utf-8')
            return True, content
        except UnicodeDecodeError:
            try:
                file.seek(0)  # Reseta o ponteiro do arquivo
                content = file.read().decode('latin-1')
                return True, content
            except Exception:
                return False, 'Erro ao processar o arquivo.'

    @staticmethod
    def _handle_pdf(file):
        """Processa arquivos .pdf."""
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            text_content = []

            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)

            if not text_content:
                return False, 'Erro ao processar o arquivo.'

            return True, "\n".join(text_content)

        except Exception:
            return False, 'Erro ao processar o arquivo.'

    @staticmethod
    def _handle_eml(file):
        """Processa arquivos .eml."""
        try:
            eml_content = file.read()
            email_message = email.message_from_bytes(eml_content)

            text_content = []

            subject = email_message.get('subject', '')
            if subject:
                text_content.append(f"Assunto: {subject}")

            from_addr = email_message.get('from', '')
            if from_addr:
                text_content.append(f"De: {from_addr}")

            to_addr = email_message.get('to', '')
            if to_addr:
                text_content.append(f"Para: {to_addr}")

            date = email_message.get('date', '')
            if date:
                text_content.append(f"Data: {date}")

            text_content.append('')

            # Extrai o corpo
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == 'text/plain':
                        try:
                            text = part.get_payload(decode=True).decode()
                            text_content.append(text)
                        except:
                            continue
            else:
                try:
                    text = email_message.get_payload(decode=True).decode()
                    text_content.append(text)
                except:
                    return False, 'Erro ao processar o arquivo.'

            return True, "\n".join(text_content)

        except Exception:
            print(1)
            return False, 'Erro ao processar o arquivo.'
