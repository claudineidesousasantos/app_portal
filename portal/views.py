from django.shortcuts import render


def home(request):
    return render(request, 'landingpage/index.html')
    # return render(request, 'portal/home.html')
