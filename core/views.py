from django.shortcuts import render


def home(request):
    return render(request, "referrals/home.html")

def upload(request):
    return render(request, "referrals/upload.html")

def charts(request):
    return render(request, "referrals/charts.html")
