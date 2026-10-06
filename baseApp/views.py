from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, View
from django.http import JsonResponse
from django.contrib import messages
from datetime import datetime, date, time, timedelta
from .models import Cliente, Atendimento, AtendimentoArquivo, RISCO_CHOICES

class HomeView(TemplateView):
    """
    Class-Based View principal para renderização da página Home e do Cronograma Diário (24h).
    """
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Data selecionada ou Data Atual (Hoje)
        data_param = self.request.GET.get('data')
        hoje = date.today()
        
        if data_param:
            try:
                data_selecionada = datetime.strptime(data_param, '%Y-%m-%d').date()
            except ValueError:
                data_selecionada = hoje
        else:
            data_selecionada = hoje

        # Filtro de Risco / Categoria
        risco_param = self.request.GET.get('risco', 'todos')
        if risco_param not in ['todos', 'alto', 'medio', 'baixo']:
            risco_param = 'todos'

        # Querysets nativos do ORM
        atendimentos_qs = Atendimento.objects.filter(data=data_selecionada).select_related('cliente').prefetch_related('arquivos')
        if risco_param != 'todos':
            atendimentos_qs = atendimentos_qs.filter(risco=risco_param)

        # Gerar a lista de 48 blocos de 30 minutos (00:00 até 23:30)
        time_slots = []
        atendimentos_por_horario = {}

        current_dt = datetime.combine(data_selecionada, time(0, 0))
        end_dt = datetime.combine(data_selecionada, time(23, 30))

        while current_dt <= end_dt:
            time_str = current_dt.strftime('%H:%M')
            time_slots.append(time_str)
            atendimentos_por_horario[time_str] = []
            current_dt += timedelta(minutes=30)

        # Agrupar atendimentos por horário
        for aten in atendimentos_qs:
            slot_str = aten.horario.strftime('%H:%M')
            if slot_str in atendimentos_por_horario:
                atendimentos_por_horario[slot_str].append(aten)
            else:
                # Caso venha com minuto que não é cravado em :00 ou :30, aproxima para a chave
                atendimentos_por_horario[slot_str] = [aten]

        # Montar estrutura de dados iterável no template
        cronograma_slots = []
        for slot in time_slots:
            cronograma_slots.append({
                'horario': slot,
                'items': atendimentos_por_horario.get(slot, [])
            })

        # Lista de clientes para o formulário de atendimento
        clientes = Cliente.objects.all().order_by('nome')

        context.update({
            'data_selecionada': data_selecionada,
            'data_selecionada_iso': data_selecionada.strftime('%Y-%m-%d'),
            'data_selecionada_formatada': data_selecionada.strftime('%d/%m/%Y'),
            'hoje_iso': hoje.strftime('%Y-%m-%d'),
            'risco_selecionado': risco_param,
            'risco_choices': RISCO_CHOICES,
            'cronograma_slots': cronograma_slots,
            'clientes': clientes,
            'total_atendimentos': atendimentos_qs.count(),
            'usuario_sistema': {
                'nome': 'Dra. Ana Silva',
                'funcao': 'Médica Responsável / Administradora',
                'email': 'ana.silva@clinica.com.br',
                'crm': 'CRM/SP 123456',
                'status': 'Ativo'
            }
        })
        return context


class CadastrarClienteView(View):
    """
    Class-Based View para cadastro de Cliente/Paciente.
    Sem cadastro de senha pois não é conta de usuário do sistema.
    """
    def post(self, request, *args, **kwargs):
        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip()
        telefone = request.POST.get('telefone', '').strip()
        cpf = request.POST.get('cpf', '').strip()
        risco = request.POST.get('risco', 'medio')
        observacoes = request.POST.get('observacoes', '').strip()

        if not nome:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'O nome do cliente é obrigatório.'}, status=400)
            messages.error(request, 'O nome do cliente é obrigatório.')
            return redirect('baseApp:home')

        cliente = Cliente.objects.create(
            nome=nome,
            email=email or None,
            telefone=telefone or None,
            cpf=cpf or None,
            risco=risco,
            observacoes=observacoes or None
        )

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Cliente cadastrado com sucesso!',
                'cliente': {
                    'id': cliente.id,
                    'nome': cliente.nome,
                    'risco': cliente.risco,
                    'risco_display': cliente.get_risco_display()
                }
            })

        messages.success(request, f'Cliente "{cliente.nome}" cadastrado com sucesso!')
        return redirect('baseApp:home')


class CadastrarAtendimentoView(View):
    """
    Class-Based View para cadastro de Atendimento com descrição e upload de arquivos.
    """
    def post(self, request, *args, **kwargs):
        cliente_id = request.POST.get('cliente_id')
        data_str = request.POST.get('data')
        horario_str = request.POST.get('horario')
        descricao = request.POST.get('descricao', '').strip()
        risco = request.POST.get('risco', 'medio')

        if not cliente_id or not data_str or not horario_str or not descricao:
            msg = 'Preencha todos os campos obrigatórios (Cliente, Data, Horário e Descrição).'
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': msg}, status=400)
            messages.error(request, msg)
            return redirect('baseApp:home')

        try:
            cliente = get_object_or_404(Cliente, id=cliente_id)
            data_val = datetime.strptime(data_str, '%Y-%m-%d').date()
            horario_val = datetime.strptime(horario_str, '%H:%M').time()
        except (ValueError, Cliente.DoesNotExist) as e:
            msg = 'Dados de cliente, data ou horário inválidos.'
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': msg}, status=400)
            messages.error(request, msg)
            return redirect('baseApp:home')

        atendimento = Atendimento.objects.create(
            cliente=cliente,
            data=data_val,
            horario=horario_val,
            descricao=descricao,
            risco=risco
        )

        # Upload de arquivos (fotos, .pdf, .docx)
        arquivos = request.FILES.getlist('arquivos')
        arquivos_criados = []
        for file_obj in arquivos:
            arq = AtendimentoArquivo.objects.create(
                atendimento=atendimento,
                arquivo=file_obj,
                nome_original=file_obj.name
            )
            arquivos_criados.append(arq.nome_original)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Atendimento cadastrado com sucesso!',
                'atendimento_id': atendimento.id,
                'arquivos_qtd': len(arquivos_criados)
            })

        messages.success(request, 'Atendimento agendado com sucesso!')
        return redirect(f'/?data={data_val.strftime("%Y-%m-%d")}')


class DetalhesAtendimentoView(View):
    """
    Retorna os detalhes de um atendimento via JSON para popups/modais de histórico.
    """
    def get(self, request, pk, *args, **kwargs):
        atendimento = get_object_or_404(Atendimento.objects.select_related('cliente').prefetch_related('arquivos'), pk=pk)
        arquivos_data = []
        for arq in atendimento.arquivos.all():
            arquivos_data.append({
                'id': arq.id,
                'nome': arq.nome_original,
                'url': arq.arquivo.url,
                'extensao': arq.extensao
            })

        return JsonResponse({
            'id': atendimento.id,
            'cliente': atendimento.cliente.nome,
            'cliente_id': atendimento.cliente.id,
            'data': atendimento.data.strftime('%d/%m/%Y'),
            'horario': atendimento.horario.strftime('%H:%M'),
            'risco': atendimento.risco,
            'risco_display': atendimento.get_risco_display(),
            'descricao': atendimento.descricao,
            'arquivos': arquivos_data
        })
