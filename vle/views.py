from django.template.loader import get_template
from django.template import RequestContext
from django.http import HttpResponse
from django.utils import simplejson

from common.views import common_dict

from models import SimpleFluid

from common.settings import STATIC_URL, SITE_URL

def data_base(request):
    fluids = SimpleFluid.objects.all()
    lines = []

    for fluid in fluids:
        lines.append({
            'name' : fluid.name,
            'number' : fluid.cas_num,
            'formula' : fluid.formula
        })

    data = simplejson.dumps(lines)

    return HttpResponse(data, mimetype='application/json')

def gui(request):
    dict = common_dict()
    t = get_template('vle/pr.html')
    c = RequestContext(request, dict)
    return HttpResponse(t.render(c))


