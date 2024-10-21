from adminapp.models import *

def get_iudomain(domain):
    try:
        domain_name = IUMaster.objects.get(domain__icontains=domain)
        return domain_name
    except IUMaster.DoesNotExist():
        return None
