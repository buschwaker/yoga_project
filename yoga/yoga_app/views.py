from django.http import HttpResponse


# Простая вьюшка, которая возвращает приветственное сообщение
def hello(request):
    return HttpResponse("Привет, мир!")
