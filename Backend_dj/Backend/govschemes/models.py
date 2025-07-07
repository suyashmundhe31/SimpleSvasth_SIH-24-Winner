from django.db import models

class GovernmentScheme(models.Model):
    schemeName = models.CharField(max_length=255)
    schemeUrl = models.URLField(null=True)
    schemeDescription = models.TextField(null=True)
    userState = models.TextField(max_length=100,null=True)
    userAge = models.TextField(null=True)
    income = models.TextField(null=True)
    gender = models.TextField(max_length=10,null=True)
    familySize = models.TextField(null=True)
    maritalStatus = models.TextField(
max_length=20,null=True)
    healthProblems = models.TextField(blank=True, null=True,)
    caste = models.TextField(max_length=50,null=True)

    def __str__(self):
        return self.schemeName
