import json

def load_boulder_from_request(request):
    """
    Replace boulder data from valid Python to valid JS
    """
    return json.loads(
                request.form.get('boulder_data')
                .replace('\'', '"')
                .replace('True', 'true')
                .replace('False', 'false'))