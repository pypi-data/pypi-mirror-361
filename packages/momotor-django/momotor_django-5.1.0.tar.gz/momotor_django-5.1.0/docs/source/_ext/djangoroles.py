# Based on https://stackoverflow.com/a/13663325


def setup(app):
    for role in ['django-admin', 'setting']:
        app.add_crossref_type(
            directivename=role,
            rolename=role,
            indextemplate=f"pair: %s; {role}",
        )
