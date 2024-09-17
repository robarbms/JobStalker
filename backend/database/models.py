from django.db import models

"""
Company Django model
"""
class Company(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    address = models.TextField(blank=True, null=True)
    site_url = models.URLField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    descrption = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    stock = models.TextField(max_length=10, blank=True, null=True)
    founded_date = models.DateField(blank=True, null=True)
    parent_company = models.ForeignKey('Company', onDelete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

"""
Job Django model
"""
class Job(models.Model):
    id = models.AutoField(primary_key=True)
    job_id = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    company_id = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='jobs')
    created_at = models.DateTimeField(auto_now_add=True)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    date_posted = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    link = models.URLField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

