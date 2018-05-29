from django.core.management.base import BaseCommand

from sapl.legacy.migracao import migrar


class Command(BaseCommand):

    help = 'Migração de dados do SAPL 2.5 para o SAPL 3.1'

    def handle(self, *args, **options):
        migrar(interativo=False)
