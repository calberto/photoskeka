from django.core.management.base import BaseCommand
from django.core.management import call_command
from core.models import Fotografia
import os

class Command(BaseCommand):
    help = 'Limpa e recarrega fotografias com URLs do Cloudinary'

    def handle(self, *args, **options):
        fixture_file = 'fotografias_cloudinary.json'
        
        if not os.path.exists(fixture_file):
            self.stdout.write(self.style.ERROR(f'❌ Arquivo {fixture_file} não encontrado!'))
            return
        
        try:
            # Remove todas as fotografias
            total_removido = Fotografia.objects.count()
            self.stdout.write(f'Removendo {total_removido} fotografias antigas...')
            Fotografia.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Fotografias removidas'))
            
            # Carrega os novos dados
            self.stdout.write(f'Carregando dados de {fixture_file}...')
            call_command('loaddata', fixture_file, verbosity=2)
            
            total_carregado = Fotografia.objects.count()
            self.stdout.write(
                self.style.SUCCESS(f'✓ {total_carregado} fotografias carregadas com sucesso!')
            )
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Erro: {e}'))