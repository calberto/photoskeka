from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.apps import apps
import os

class Command(BaseCommand):
    help = 'Carrega dados iniciais apenas se o banco estiver vazio'

    def handle(self, *args, **options):
        fixture_file = 'dados.json'
        
        # Verifica se o arquivo existe
        if not os.path.exists(fixture_file):
            self.stdout.write(self.style.WARNING(f'Arquivo {fixture_file} não encontrado. Pulando...'))
            return
        
        try:
            # Verifica se já existem fotografias no banco
            Fotografia = apps.get_model('core', 'Fotografia')
            
            if Fotografia.objects.exists():
                total = Fotografia.objects.count()
                self.stdout.write(
                    self.style.WARNING(f'⚠ Banco já possui {total} fotografias. Pulando importação...')
                )
                return
            
            # Se chegou aqui, o banco está vazio - pode carregar
            self.stdout.write(self.style.SUCCESS(f'→ Carregando dados de {fixture_file}...'))
            call_command('loaddata', fixture_file, verbosity=2)
            
            # Confirma quantas foram carregadas
            total_carregado = Fotografia.objects.count()
            self.stdout.write(
                self.style.SUCCESS(f'✓ {total_carregado} fotografias carregadas com sucesso!')
            )
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Erro ao carregar dados: {e}'))