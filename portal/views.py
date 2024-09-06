from django.shortcuts import render


def home(request):
    return render(request, 'portal/index.html')
    # return render(request, 'portal/home.html')
