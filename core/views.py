from django.db.models import Q, Sum
from django.utils.dateparse import parse_date
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import FinancialRecord, User
from .permissions import IsAdmin, IsAnalystOrAdmin, IsOwnerOrAdmin, IsViewerAnalystAdmin
from .serializers import FinancialRecordSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]


class FinancialRecordViewSet(viewsets.ModelViewSet):
    queryset = FinancialRecord.objects.filter(deleted=False)
    serializer_class = FinancialRecordSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAnalystOrAdmin]
        elif self.action in ['create', 'update', 'partial_update', 'destroy', 'restore']:
            permission_classes = [IsAdmin]
        else:
            permission_classes = [IsViewerAnalystAdmin]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        qs = FinancialRecord.objects.filter(deleted=False)
        if self.request.user.role == 'analyst':
            qs = qs
        elif self.request.user.role == 'admin':
            qs = qs
        else:
            return qs.none()

        q = self.request.query_params.get('q')
        category = self.request.query_params.get('category')
        rec_type = self.request.query_params.get('type')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if q:
            qs = qs.filter(Q(notes__icontains=q) | Q(category__icontains=q))
        if category:
            qs = qs.filter(category__iexact=category)
        if rec_type in [FinancialRecord.TYPE_INCOME, FinancialRecord.TYPE_EXPENSE]:
            qs = qs.filter(type=rec_type)
        if start_date:
            parsed = parse_date(start_date)
            if parsed:
                qs = qs.filter(date__gte=parsed)
        if end_date:
            parsed = parse_date(end_date)
            if parsed:
                qs = qs.filter(date__lte=parsed)

        return qs

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        try:
            record = FinancialRecord.objects.get(pk=pk, deleted=True)
        except FinancialRecord.DoesNotExist:
            return Response({'detail': 'Record not found or not deleted'}, status=status.HTTP_404_NOT_FOUND)

        record.deleted = False
        record.save()
        serializer = self.get_serializer(record)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        instance.deleted = True
        instance.save()


class DashboardSummaryView(APIView):
    permission_classes = [IsViewerAnalystAdmin]

    def get(self, request):
        records = FinancialRecord.objects.filter(deleted=False)

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        category = request.query_params.get('category')
        rec_type = request.query_params.get('type')

        if start_date:
            parsed = parse_date(start_date)
            if not parsed:
                return Response({'detail': 'Invalid start_date format; expected YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
            records = records.filter(date__gte=parsed)
        if end_date:
            parsed = parse_date(end_date)
            if not parsed:
                return Response({'detail': 'Invalid end_date format; expected YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
            records = records.filter(date__lte=parsed)
        if category:
            records = records.filter(category__iexact=category)
        if rec_type in ['income', 'expense']:
            records = records.filter(type=rec_type)

        total_income = records.filter(type=FinancialRecord.TYPE_INCOME).aggregate(total=Sum('amount'))['total'] or 0
        total_expense = records.filter(type=FinancialRecord.TYPE_EXPENSE).aggregate(total=Sum('amount'))['total'] or 0

        category_totals = records.values('category').annotate(total=Sum('amount')).order_by('-total')

        recent_activity = FinancialRecordSerializer(records.order_by('-date', '-created_at')[:10], many=True).data

        monthly_trends = (
            records
            .values('date__year', 'date__month', 'type')
            .annotate(total=Sum('amount'))
            .order_by('date__year', 'date__month')
        )

        # normalize monthly trends
        trends = {}
        for item in monthly_trends:
            key = f"{item['date__year']}-{item['date__month']:02d}"
            trends.setdefault(key, {'income': 0, 'expense': 0})
            trends[key][item['type']] = float(item['total'])

        data = {
            'total_income': float(total_income),
            'total_expense': float(total_expense),
            'net_balance': float(total_income - total_expense),
            'category_totals': [{'category': x['category'], 'total': float(x['total'])} for x in category_totals],
            'recent_activity': recent_activity,
            'monthly_trends': [{'period': k, **v} for k, v in trends.items()],
        }

        return Response(data)

