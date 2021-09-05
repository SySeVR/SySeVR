def setup(app):
    from .domain import JoernDomain
    app.add_domain(JoernDomain)
