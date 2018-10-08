from rest_framework.routers import DefaultRouter
from sapl.api.materia.views import MateriaLegislativaViewSet
# Não adicione app_name
# app_name = AppConfig.name


router = DefaultRouter()
router.register(r'materia', MateriaLegislativaViewSet)

urlpatterns = [

]
