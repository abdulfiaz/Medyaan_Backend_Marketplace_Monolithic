from adminapp.models import *

def get_iuid(domain):
    try:
        domain_name = IUMaster.objects.get(domain__icontains=domain)
        print("domain_name-->>", domain_name)
        return domain_name
    except IUMaster.DoesNotExist:
        return None