from .models import Barbershop

class BarbershopMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            barbershop_id = request.session.get('barbershop_id')
            if barbershop_id:
                request.current_barbershop = Barbershop.objects.filter(id=barbershop_id, owner=request.user).first()
            else:
                request.current_barbershop = None
        return self.get_response(request)
