
import re
import logging

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponse, JsonResponse
from django.template import RequestContext, loader
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView, UpdateView
from django.views.generic.base import RedirectView
from django.views.generic.edit import FormView
from django_filters.views import FilterView
import weasyprint
import sapl
from sapl.base.models import AppConfig
from sapl.compilacao.views import IntegracaoTaView
from sapl.crud.base import (RP_DETAIL, RP_LIST, Crud, CrudAux,
                            MasterDetailCrud, make_pagination)
from sapl.utils import show_results_filter_set

from .forms import (AnexoNormaJuridicaForm, NormaFilterSet, NormaJuridicaForm,
                    NormaPesquisaSimplesForm, NormaRelacionadaForm, AutoriaNormaForm)
from .models import (AnexoNormaJuridica, AssuntoNorma, NormaJuridica, NormaRelacionada,
                     TipoNormaJuridica, TipoVinculoNormaJuridica, AutoriaNorma)


# LegislacaoCitadaCrud = Crud.build(LegislacaoCitada, '')
AssuntoNormaCrud = CrudAux.build(AssuntoNorma, 'assunto_norma_juridica',
                                 list_field_names=['assunto', 'descricao'])


TipoNormaCrud = CrudAux.build(
    TipoNormaJuridica, 'tipo_norma_juridica',
    list_field_names=['sigla', 'descricao', 'equivalente_lexml'])
TipoVinculoNormaJuridicaCrud = CrudAux.build(
    TipoVinculoNormaJuridica, '',
    list_field_names=['sigla', 'descricao_ativa', 'descricao_passiva'])


class NormaRelacionadaCrud(MasterDetailCrud):
    model = NormaRelacionada
    parent_field = 'norma_principal'
    help_topic = 'norma_juridica'

    class BaseMixin(MasterDetailCrud.BaseMixin):
        list_field_names = ['norma_relacionada', 'tipo_vinculo']

    class CreateView(MasterDetailCrud.CreateView):
        form_class = NormaRelacionadaForm

    class UpdateView(MasterDetailCrud.UpdateView):
        form_class = NormaRelacionadaForm

        def get_initial(self):
            initial = super(UpdateView, self).get_initial()
            initial['tipo'] = self.object.norma_relacionada.tipo.id
            initial['numero'] = self.object.norma_relacionada.numero
            initial['ano'] = self.object.norma_relacionada.ano
            initial['ementa'] = self.object.norma_relacionada.ementa
            return initial

    class DetailView(MasterDetailCrud.DetailView):

        layout_key = 'NormaRelacionadaDetail'


class NormaPesquisaView(FilterView):
    model = NormaJuridica
    filterset_class = NormaFilterSet
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset()

        qs = qs.extra({
            'nm_i': "CAST(regexp_replace(numero,'[^0-9]','', 'g') AS INTEGER)",
            'norma_letra': "regexp_replace(numero,'[^a-zA-Z]','', 'g')"
        }).order_by('-data', '-nm_i', '-norma_letra')

        return qs

    def get_context_data(self, **kwargs):
        context = super(NormaPesquisaView, self).get_context_data(**kwargs)

        context['title'] = _('Pesquisar Norma Jurídica')

        self.filterset.form.fields['o'].label = _('Ordenação')

        qs = self.object_list
        if 'o' in self.request.GET and not self.request.GET['o']:
            qs = qs.order_by('-ano', 'tipo', '-numero')

        qr = self.request.GET.copy()

        if 'page' in qr:
            del qr['page']

        paginator = context['paginator']
        page_obj = context['page_obj']

        context['page_range'] = make_pagination(
            page_obj.number, paginator.num_pages)

        context['filter_url'] = ('&' + qr.urlencode()) if len(qr) > 0 else ''

        context['show_results'] = show_results_filter_set(qr)

        return context


class AnexoNormaJuridicaCrud(MasterDetailCrud):
    model = AnexoNormaJuridica
    parent_field = 'norma'
    help_topic = 'anexonormajuridica'
    public = [RP_LIST, RP_DETAIL]

    class BaseMixin(MasterDetailCrud.BaseMixin):
        list_field_names = ['id', 'anexo_arquivo', 'assunto_anexo']

    class CreateView(MasterDetailCrud.CreateView):
        form_class = AnexoNormaJuridicaForm
        layout_key = 'AnexoNormaJuridica'

        def get_initial(self):
            initial = super(MasterDetailCrud.CreateView, self).get_initial()
            initial['norma'] = NormaJuridica.objects.get(id=self.kwargs['pk'])
            return initial

    class UpdateView(MasterDetailCrud.UpdateView):
        form_class = AnexoNormaJuridicaForm
        layout_key = 'AnexoNormaJuridica'

        def get_initial(self):
            initial = super(UpdateView, self).get_initial()
            initial['norma'] = self.object.norma
            initial['anexo_arquivo'] = self.object.anexo_arquivo
            initial['assunto_anexo'] = self.object.assunto_anexo
            initial['ano'] = self.object.ano
            return initial

    class DetailView(MasterDetailCrud.DetailView):
        form_class = AnexoNormaJuridicaForm
        layout_key = 'AnexoNormaJuridica'


class NormaTaView(IntegracaoTaView):
    model = NormaJuridica
    model_type_foreignkey = TipoNormaJuridica
    map_fields = {
        'data': 'data',
        'ementa': 'ementa',
        'observacao': 'observacao',
        'numero': 'numero',
        'ano': 'ano',
        'tipo': 'tipo',
    }

    map_funcs = {
        'publicacao_func': True
    }

    def get(self, request, *args, **kwargs):
        """
        Para manter a app compilacao isolada das outras aplicações,
        este get foi implementado para tratar uma prerrogativa externa
        de usuário.
        """
        if AppConfig.attr('texto_articulado_norma'):
            return IntegracaoTaView.get(self, request, *args, **kwargs)
        else:
            return self.get_redirect_deactivated()


class NormaCrud(Crud):
    model = NormaJuridica
    help_topic = 'norma_juridica'
    public = [RP_LIST, RP_DETAIL]

    class BaseMixin(Crud.BaseMixin):
        list_field_names = ['tipo', 'numero', 'ano', 'ementa']

        list_url = ''

        @property
        def search_url(self):
            namespace = self.model._meta.app_config.name
            return reverse('%s:%s' % (namespace, 'norma_pesquisa'))

    class DetailView(Crud.DetailView):
        pass

    class DeleteView(Crud.DeleteView):

        def get_success_url(self):
            return self.search_url

    class CreateView(Crud.CreateView):
        form_class = NormaJuridicaForm

        @property
        def cancel_url(self):
            return self.search_url

        def get_initial(self):
            logger = logging.getLogger(__name__)
            try:
                logger.info('Tentando obter objeto de modelo da esfera da federação.')
                esfera = sapl.base.models.AppConfig.objects.last(
                ).esfera_federacao
                self.initial['esfera_federacao'] = esfera
            except:
                logger.error('Erro ao obter objeto de modelo da esfera da federação.')
                pass
            self.initial['complemento'] = False
            return self.initial

        layout_key = 'NormaJuridicaCreate'

    class ListView(Crud.ListView, RedirectView):

        def get_redirect_url(self, *args, **kwargs):
            namespace = self.model._meta.app_config.name
            return reverse('%s:%s' % (namespace, 'norma_pesquisa'))

        def get(self, request, *args, **kwargs):
            return RedirectView.get(self, request, *args, **kwargs)

    class UpdateView(Crud.UpdateView):
        form_class = NormaJuridicaForm

        layout_key = 'NormaJuridicaCreate'

        def get_initial(self):
            initial = super(UpdateView, self).get_initial()
            norma = NormaJuridica.objects.get(id=self.kwargs['pk'])
            if norma.materia:
                initial['tipo_materia'] = norma.materia.tipo
                initial['ano_materia'] = norma.materia.ano
                initial['numero_materia'] = norma.materia.numero
                initial['esfera_federacao'] = norma.esfera_federacao
            return initial


def recuperar_norma(request):
    logger = logging.getLogger(__name__)
    tipo = TipoNormaJuridica.objects.get(pk=request.GET['tipo'])
    numero = request.GET['numero']
    ano = request.GET['ano']

    try:
        logger.info('Tentando obter NormaJuridica (tipo={}, ano={}, numero={}).'
                    .format(tipo, ano, numero))
        norma = NormaJuridica.objects.get(tipo=tipo,
                                          ano=ano,
                                          numero=numero)
        response = JsonResponse({'ementa': norma.ementa,
                                 'id': norma.id})
    except ObjectDoesNotExist:
        logger.error('NormaJuridica buscada (tipo={}, ano={}, numero={}) não existe. '
                     'Definida com ementa vazia e id 0.'.format(tipo, ano, numero))
        response = JsonResponse({'ementa': '', 'id': 0})

    return response


def recuperar_numero_norma(request):
    tipo = TipoNormaJuridica.objects.get(pk=request.GET['tipo'])
    ano = request.GET.get('ano', '')
    param = {'tipo': tipo}
    param['ano'] = ano if ano else timezone.now().year
    norma = NormaJuridica.objects.filter(**param).order_by(
        'tipo', 'ano', 'numero').values_list('numero', 'ano').last()
    if norma:
        response = JsonResponse({'numero': int(re.sub("[^0-9].*", '', norma[0])) + 1,
                                 'ano': norma[1]})
    else:
        response = JsonResponse(
            {'numero': 1, 'ano': ano})

    return response


class AutoriaNormaCrud(MasterDetailCrud):
    model = AutoriaNorma
    parent_field = 'norma'
    help_topic = 'despacho_autoria'
    public = [RP_LIST, RP_DETAIL]
    list_field_names = ['autor', 'autor__tipo__descricao', 'primeiro_autor']

    class LocalBaseMixin():
        form_class = AutoriaNormaForm

        @property
        def layout_key(self):
            return None

    class CreateView(LocalBaseMixin, MasterDetailCrud.CreateView):

        def get_initial(self):
            initial = super().get_initial()
            norma = NormaJuridica.objects.get(id=self.kwargs['pk'])
            initial['data_relativa'] = norma.data
            initial['autor'] = []
            return initial

    class UpdateView(LocalBaseMixin, MasterDetailCrud.UpdateView):

        def get_initial(self):
            initial = super().get_initial()
            initial.update({
                'data_relativa': self.object.norma.data_apresentacao,
                'tipo_autor': self.object.autor.tipo.id,
            })
            return initial

class ImpressosView(PermissionRequiredMixin, TemplateView):
    template_name = 'materia/impressos/impressos.html'
    permission_required = ('materia.can_access_impressos', )


def gerar_pdf_impressos(request, context, template_name):
    template = loader.get_template(template_name)
    html = template.render(RequestContext(request, context))
    pdf = weasyprint.HTML(string=html, base_url=request.build_absolute_uri()
                          ).write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = (
        'inline; filename="relatorio_impressos.pdf"')
    response['Content-Transfer-Encoding'] = 'binary'

    return response


class NormaPesquisaSimplesView(PermissionRequiredMixin, FormView):
    form_class = NormaPesquisaSimplesForm
    template_name = 'materia/impressos/norma.html'
    permission_required = ('materia.can_access_impressos', )

    def form_valid(self, form):
        normas = NormaJuridica.objects.all().order_by(
            'numero')
        template_norma = 'materia/impressos/normas_pdf.html'

        titulo = form.cleaned_data['titulo']

        if form.cleaned_data['tipo_norma']:
            normas = normas.filter(tipo=form.cleaned_data['tipo_norma'])

        if form.cleaned_data['data_inicial']:
            normas = normas.filter(
                data__gte=form.cleaned_data['data_inicial'],
                data__lte=form.cleaned_data['data_final'])

        qtd_resultados = len(normas)
        if qtd_resultados > 2000:
            normas = normas[:2000]

        context = {'quantidade': qtd_resultados,
                   'titulo': titulo,
                   'normas': normas}

        return gerar_pdf_impressos(self.request, context, template_norma)
