from django.core.management.base import BaseCommand
from django.core.management import call_command
import os

class Command(BaseCommand):
    help = 'Carrega dados iniciais se o arquivo existir'

    def handle(self, *args, **options):
        fixture_file = 'dados.json'
        
        if os.path.exists(fixture_file):
            self.stdout.write(f'Carregando dados de {fixture_file}...')
            try:
                call_command('loaddata', fixture_file, verbosity=2)
                self.stdout.write(self.style.SUCCESS('✓ Dados carregados com sucesso!'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Erro ao carregar dados: {e}'))
        else:
            self.stdout.write(self.style.WARNING(f'Arquivo {fixture_file} não encontrado. Pulando...'))