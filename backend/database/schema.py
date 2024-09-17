import graphene
from graphene_django import DjangoObjectType
from .models import Company, Job

class CompanyType(DjangoObjectType):
    class Meta:
        model = Company

class JobType(DjangoObjectType):
    class Meta:
        model = Job

class Query(graphene.ObjectType):
    allCompanies = graphene.List(CompanyType)
    allJobs = graphene.List(JobType)

    def resolve_allCompanies(self, info):
        return Company.objects.all()
    
    def resolve_allJobs(self, info):
        return Job.objects.all()
    
schema = graphene.Schema(query=Query)
