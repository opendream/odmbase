
from django.shortcuts import render



# =============================
# Home
# =============================

def home(request):
    return render(request, 'presentation/home.html')


def handler403(request):
    return render(request, '403.html')

