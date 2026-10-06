from django.core.management.base import BaseCommand
from datetime import date, time
from baseApp.models import Cliente, Atendimento

class Command(BaseCommand):
    help = 'Popula o banco de dados com clientes e atendimentos de exemplo.'

    def handle(self, *args, **kwargs):
        c1, _ = Cliente.objects.get_or_create(
            nome='Carlos Eduardo Mendes',
            email='carlos.mendes@email.com',
            telefone='(11) 99887-1122',
            cpf='123.456.789-00',
            risco='alto',
            observacoes='Paciente hipertenso com acompanhamento contínuo.'
        )

        c2, _ = Cliente.objects.get_or_create(
            nome='Mariana Lima Ribeiro',
            email='mariana.ribeiro@email.com',
            telefone='(11) 98112-3344',
            cpf='987.654.321-11',
            risco='medio',
            observacoes='Retorno pós-exames de rotina.'
        )

        c3, _ = Cliente.objects.get_or_create(
            nome='Lucas Fernandes Ramos',
            email='lucas.ramos@email.com',
            telefone='(11) 97654-9988',
            cpf='456.789.123-22',
            risco='baixo',
            observacoes='Check-up anual preventiva.'
        )

        today = date.today()

        Atendimento.objects.get_or_create(
            cliente=c1,
            data=today,
            horario=time(9, 0),
            defaults={
                'descricao': 'Avaliação cardiológica e ajuste de medicação.',
                'risco': 'alto'
            }
        )

        Atendimento.objects.get_or_create(
            cliente=c2,
            data=today,
            horario=time(10, 30),
            defaults={
                'descricao': 'Análise de exames laboratoriais de sangue.',
                'risco': 'medio'
            }
        )

        Atendimento.objects.get_or_create(
            cliente=c3,
            data=today,
            horario=time(14, 0),
            defaults={
                'descricao': 'Consulta clínica geral e anamnese.',
                'risco': 'baixo'
            }
        )

        self.stdout.write(self.style.SUCCESS('Dados de exemplo semeados com sucesso!'))
