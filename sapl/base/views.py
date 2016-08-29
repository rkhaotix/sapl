from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateView
from django_filters.views import FilterView

from sapl.crud.base import (Crud, CrudBaseMixin, CrudCreateView,
                            CrudDetailView, CrudUpdateView, make_pagination)
from sapl.materia.models import MateriaLegislativa, TipoMateriaLegislativa
from sapl.utils import permissao_tb_aux

from .forms import CasaLegislativaForm, RelatorioMateriasPorAutorFilterSet
from .models import CasaLegislativa


def get_casalegislativa():
    return CasaLegislativa.objects.first()


class RelatorioMateriasPorAutorView(FilterView):
    model = MateriaLegislativa
    filterset_class = RelatorioMateriasPorAutorFilterSet
    paginate_by = 10
    template_name = 'base/RelatorioMateriasPorAutor_filter.html'

    def get_filterset_kwargs(self, filterset_class):
        super(RelatorioMateriasPorAutorView,
              self).get_filterset_kwargs(filterset_class)

        kwargs = {'data': self.request.GET or None}
        qs = self.get_queryset()

        return kwargs

    def get_context_data(self, **kwargs):
        context = super(RelatorioMateriasPorAutorView,
                        self).get_context_data(**kwargs)

        context['title'] = _('Matérias por Autor')

        qtdes = {}
        for tipo in TipoMateriaLegislativa.objects.all():
            qs = kwargs['object_list']
            qtde = len(qs.filter(tipo_id=tipo.id))
            if qtde > 0:
                qtdes[tipo] = qtde
        context['qtdes'] = qtdes

        qr = self.request.GET.copy()
        context['filter_url'] = ('&' + qr.urlencode()) if len(qr) > 0 else ''

        return context


class CasaLegislativaCrud(Crud):
    model = CasaLegislativa
    help_path = ''

    class BaseMixin(PermissionRequiredMixin, CrudBaseMixin):
        list_field_names = ['codigo', 'nome', 'sigla']

        def has_permission(self):
            if self.request.user.is_superuser:
                return True
            else:
                return False

    class CreateView(PermissionRequiredMixin, CrudCreateView):
        permission_required = {'base.add_casa_legislativa'}
        form_class = CasaLegislativaForm

    class UpdateView(PermissionRequiredMixin, CrudUpdateView):
        permission_required = {'base.change_casalegislativa'}
        form_class = CasaLegislativaForm

    class DetailView(CrudDetailView):
        form_class = CasaLegislativaForm

        def get(self, request, *args, **kwargs):
            return HttpResponseRedirect(
                reverse('sapl.base:casalegislativa_update',
                        kwargs={'pk': self.kwargs['pk']}))


class HelpView(PermissionRequiredMixin, TemplateView):
    # XXX treat non existing template as a 404!!!!

    def get_template_names(self):
        return ['ajuda/%s.html' % self.kwargs['topic']]


class SistemaView(PermissionRequiredMixin, TemplateView):
    template_name = 'sistema.html'
    permission_required = ''

    def has_permission(self):
        return permissao_tb_aux(self)
