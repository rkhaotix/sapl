from datetime import datetime

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils.timezone import utc
from rest_framework.generics import ListAPIView
from rest_framework.permissions import (IsAuthenticated, AllowAny)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from reversion.models import Version

from sapl.api.apps import _time_refresh_models
from sapl.api.serializers import ModelChoiceSerializer


class ModelChoiceView(ListAPIView):

    # FIXME aplicar permissão correta de usuário
    permission_classes = (IsAuthenticated,)
    serializer_class = ModelChoiceSerializer

    def get(self, request, *args, **kwargs):
        self.model = ContentType.objects.get_for_id(
            self.kwargs['content_type']).model_class()

        pagination = request.GET.get('pagination', '')

        if pagination == 'False':
            self.pagination_class = None

        return ListAPIView.get(self, request, *args, **kwargs)

    def get_queryset(self):
        return self.model.objects.all()


class TimeRefreshDatabaseView(APIView):

    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        return Response(_time_refresh_models)


class TimeRefreshMobileViewSet(ReadOnlyModelViewSet):
    permission_classes = (AllowAny,)
    deletados = None

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        response.data['deleted'] = self.deletados if self.deletados else []
        return response

    def get_queryset(self):
        qs = super().get_queryset()
        opts = qs.model._meta

        data_min = self.request.query_params.get('data_min', None)
        data_max = self.request.query_params.get('data_max', None)
        tipo_update = self.request.query_params.get('tipo_update', '1')

        if data_min:
            data_min = datetime.strptime(data_min, '%Y-%m-%dT%H:%M:%S.%f')
            data_min = data_min.replace(tzinfo=utc)
        if data_max:
            data_max = datetime.strptime(data_max, '%Y-%m-%dT%H:%M:%S.%f')
            data_max = data_max.replace(tzinfo=utc)

        if data_min or data_max:
            if tipo_update == 'sync':
                q_model = Q(content_type__app_label=opts.app_label,
                            content_type__model=opts.model_name)

                q_data = Q()
                if data_min:
                    q_data &= Q(revision__date_created__gte=data_min)

                if data_max:
                    q_data &= Q(revision__date_created__lte=data_max)

                vs = Version.objects.filter(q_model).order_by(
                    '-revision__date_created', '-object_id')

                vs_sync = vs.filter(q_data).values_list('object_id', flat=True)
                vs_sync = set(map(int, vs_sync))

                # com o código abaixo envia todos os deletados no período sel.
                qs = qs.filter(id__in=vs_sync)
                qs_values = set(qs.values_list('id', flat=True))
                self.deletados = vs_sync - qs_values

                # com código abaixo envia todos os deletados
                # qs_values = set(qs.values_list('id', flat=True))
                # qs = qs.filter(id__in=vs_sync)
                # vs = vs.values_list('object_id', flat=True)
                # vs = set(map(int, vs))
                # self.deletados = vs - qs_values

            elif tipo_update == 'get':
                """
                    apesar de a data ser datetime e o campo data_inicio
                    ser DateField, devido a este fato, as partes de um dia
                    é descartada no filtro. 
                """
                params = {}
                if data_min:
                    params['{}__gte'.format(
                        self.field_to_filter_date)] = data_min
                if data_max:
                    params['{}__lte'.format(
                        self.field_to_filter_date)] = data_max

                qs = qs.filter(**params)

        return qs
