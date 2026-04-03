from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import FinancialRecord, User


class FinanceAPITestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin_user', password='adminpass', role=User.ROLE_ADMIN)
        self.analyst = User.objects.create_user(username='analyst_user', password='analystpass', role=User.ROLE_ANALYST)
        self.viewer = User.objects.create_user(username='viewer_user', password='viewerpass', role=User.ROLE_VIEWER)

        self.admin_client = APIClient()
        token = self._get_token(self.admin.username, 'adminpass')
        self.admin_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        self.analyst_client = APIClient()
        token = self._get_token(self.analyst.username, 'analystpass')
        self.analyst_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        self.viewer_client = APIClient()
        token = self._get_token(self.viewer.username, 'viewerpass')
        self.viewer_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        self.record = FinancialRecord.objects.create(user=self.admin, amount=100, type=FinancialRecord.TYPE_INCOME, category='Sales', date='2026-04-01', notes='Initial')

    def _get_token(self, username, password):
        response = self.client.post(reverse('token_obtain_pair'), {'username': username, 'password': password}, format='json')
        return response.data['access']

    def test_viewer_cannot_list_records(self):
        response = self.viewer_client.get(reverse('record-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_analyst_can_list_records(self):
        response = self.analyst_client.get(reverse('record-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_admin_can_create_and_delete_record(self):
        payload = {'amount': 300.0, 'type': 'expense', 'category': 'Travel', 'date': '2026-04-02', 'notes': 'Trip'}
        response = self.admin_client.post(reverse('record-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        record_id = response.data['id']
        del_response = self.admin_client.delete(reverse('record-detail', args=[record_id]))
        self.assertEqual(del_response.status_code, status.HTTP_204_NO_CONTENT)

        record = FinancialRecord.objects.get(id=record_id)
        self.assertTrue(record.deleted)

    def test_restore_deleted_record(self):
        record = FinancialRecord.objects.create(user=self.admin, amount=50, type=FinancialRecord.TYPE_EXPENSE, category='Food', date='2026-04-03', notes='Lunch')
        record.deleted = True
        record.save()

        restore_url = reverse('record-restore', args=[record.id])
        response = self.admin_client.post(restore_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        record.refresh_from_db()
        self.assertFalse(record.deleted)

    def test_record_search(self):
        FinancialRecord.objects.create(user=self.admin, amount=80, type=FinancialRecord.TYPE_EXPENSE, category='Office', date='2026-04-03', notes='Stationery purchase')
        response = self.admin_client.get(reverse('record-list') + '?q=stationery')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_dashboard_available_for_every_role(self):
        for client in [self.admin_client, self.analyst_client, self.viewer_client]:
            response = client.get(reverse('dashboard-summary'))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('total_income', response.data)
            self.assertIn('total_expense', response.data)

