def normalize(**kwargs):
    """Extract prompt/query from any JSON body."""
    params = kwargs.get("params", kwargs)
    q = params.get("prompt") or params.get("query") or kwargs.get("prompt") or kwargs.get("query")
    return q, params
