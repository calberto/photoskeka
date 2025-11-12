from django.core.management.base import BaseCommand
from core.models import Fotografia
import cloudinary.uploader

class Command(BaseCommand):
    help = 'Faz upload das imagens locais para o Cloudinary'

    def handle(self, *args, **options):
        fotografias = Fotografia.objects.all()
        total = fotografias.count()
        
        self.stdout.write(f'Iniciando upload de {total} fotografias...')
        
        sucesso = 0
        erros = 0
        
        for i, foto in enumerate(fotografias, 1):
            try:
                # Verifica se o campo de imagem existe e tem arquivo
                if foto.arquivo and hasattr(foto.arquivo, 'path'):
                    # Faz upload para Cloudinary
                    result = cloudinary.uploader.upload(
                        foto.arquivo.path,
                        folder='photoskeka',  # pasta no Cloudinary
                        public_id=f'foto_{foto.id}',
                        resource_type='auto'  # auto-detecta se é imagem ou vídeo
                    )
                    
                    # Atualiza o campo com a URL do Cloudinary
                    foto.arquivo = result['secure_url']
                    foto.save()
                    
                    sucesso += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'[{i}/{total}] ✓ {foto.titulo}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'[{i}/{total}] ⚠ Sem arquivo: {foto.titulo}')
                    )
                    
            except Exception as e:
                erros += 1
                self.stdout.write(
                    self.style.ERROR(f'[{i}/{total}] ✗ Erro em {foto.titulo}: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Concluído! {sucesso} sucesso, {erros} erros')
        )