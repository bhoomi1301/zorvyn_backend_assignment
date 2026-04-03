from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import DashboardSummaryView, FinancialRecordViewSet, UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('records', FinancialRecordViewSet, basename='record')

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
    path('dashboard/', DashboardSummaryView.as_view(), name='dashboard-summary'),
]
