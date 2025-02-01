from fastapi import FastAPI

app = FastAPI()


@app.get('/')
def read_root(id, request):
    """ Some description

    Args:
        id: str - the id you're requesting
        request: Request - foo

    Returns:
        dict: The data you're looking for
    """
    return {'Hello': 'World'}
