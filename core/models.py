from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_VIEWER = 'viewer'
    ROLE_ANALYST = 'analyst'
    ROLE_ADMIN = 'admin'

    ROLE_CHOICES = [
        (ROLE_VIEWER, 'Viewer'),
        (ROLE_ANALYST, 'Analyst'),
        (ROLE_ADMIN, 'Admin'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_VIEWER)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class FinancialRecord(models.Model):
    TYPE_INCOME = 'income'
    TYPE_EXPENSE = 'expense'

    TYPE_CHOICES = [
        (TYPE_INCOME, 'Income'),
        (TYPE_EXPENSE, 'Expense'),
    ]

    user = models.ForeignKey('core.User', on_delete=models.CASCADE, related_name='records')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    category = models.CharField(max_length=100)
    date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.type} {self.amount} ({self.category})"

