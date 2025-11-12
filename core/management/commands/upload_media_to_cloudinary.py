from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Fotografia
import cloudinary
import cloudinary.uploader
import os

class Command(BaseCommand):
    help = 'Faz upload das imagens locais para o Cloudinary'

    def handle(self, *args, **options):
        # Configura o Cloudinary com as variáveis de ambiente
        cloudinary.config(
            cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
            api_key=os.environ.get('CLOUDINARY_API_KEY'),
            api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
            secure=True
        )
        
        # Verifica se as credenciais foram carregadas
        if not cloudinary.config().cloud_name:
            self.stdout.write(
                self.style.ERROR('❌ Erro: Variáveis do Cloudinary não configuradas!')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'✓ Cloudinary configurado: {cloudinary.config().cloud_name}')
        )
        
        fotografias = Fotografia.objects.all()
        total = fotografias.count()
        
        self.stdout.write(f'Iniciando upload de {total} fotografias...\n')
        
        sucesso = 0
        erros = 0
        pulados = 0
        
        for i, foto in enumerate(fotografias, 1):
            try:
                # Verifica se o campo de imagem existe e tem arquivo
                if foto.arquivo and hasattr(foto.arquivo, 'path'):
                    import os as os_module
                    
                    # Verifica se o arquivo existe fisicamente
                    if not os_module.path.exists(foto.arquivo.path):
                        pulados += 1
                        self.stdout.write(
                            self.style.WARNING(f'[{i}/{total}] ⚠ Arquivo não existe: {foto.titulo}')
                        )
                        continue
                    
                    # Faz upload para Cloudinary
                    result = cloudinary.uploader.upload(
                        foto.arquivo.path,
                        folder='photoskeka',
                        public_id=f'foto_{foto.id}',
                        resource_type='auto',
                        overwrite=True
                    )
                    
                    # Atualiza o campo com a nova URL
                    foto.arquivo = result['secure_url']
                    foto.save()
                    
                    sucesso += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'[{i}/{total}] ✓ {foto.titulo}')
                    )
                else:
                    pulados += 1
                    self.stdout.write(
                        self.style.WARNING(f'[{i}/{total}] ⚠ Sem arquivo vinculado: {foto.titulo}')
                    )
                    
            except Exception as e:
                erros += 1
                self.stdout.write(
                    self.style.ERROR(f'[{i}/{total}] ✗ Erro em {foto.titulo}: {str(e)}')
                )
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS(f'✓ Upload concluído!')
        )
        self.stdout.write(f'  Sucesso: {sucesso}')
        self.stdout.write(f'  Erros: {erros}')
        self.stdout.write(f'  Pulados: {pulados}')
        self.stdout.write('='*50)