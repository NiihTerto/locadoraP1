from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from locacao.models_clientes import Cliente, Funcionario
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Popula a base de dados com dados iniciais de Clientes e Funcionários'

    def handle(self, *args, **kwargs):
        self.stdout.write('A popular dados de clientes e funcionários...')
        
        user, created = User.objects.get_or_create(
            username='gerente', 
            defaults={'email': 'gerente@locadora.com', 'is_staff': True, 'is_superuser': True}
        )
        if created:
            user.set_password('123456')
            user.save()
        Funcionario.objects.get_or_create(user=user, defaults={'cargo': 'Gerente Geral'})

        Cliente.objects.get_or_create(
            cpf='52998224725',
            defaults={
                'nome': 'Maria Oliveira',
                'telefone': '11999998888',
                'email': 'maria@email.com',
                'cnh_numero': '98765432100',
                'cnh_categoria': 'B',
                'cnh_validade': date.today() + timedelta(days=730)
            }
        )

        self.stdout.write(self.style.SUCCESS('Sucesso! Dados de P3 inseridos na base de dados.'))