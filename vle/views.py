from django.template.loader import get_template
from django.template import RequestContext
from django.http import HttpResponse
from django.utils import simplejson
from models import SimpleFluid

from common.settings import STATIC_URL, SITE_URL

def vle(request):
    fluids = SimpleFluid.objects.all()
    dict = []

    for fluid in fluids:
        dict.append({
            'name' : fluid.name,
            'number' : fluid.cas_num,
            'formula' : fluid.formula
        })

    data = simplejson.dumps(dict)

    return HttpResponse(data, mimetype='application/json')
