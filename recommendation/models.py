from django.db import models
from accounts.models import Account

class UserSearch(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    search_query = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.search_query}"
    
