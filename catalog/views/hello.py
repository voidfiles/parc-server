from simpleapi import api_export


@api_export(method='GET', path=r'hello')
def hello(request):
    return 'hello'
