from django_medusa.renderers import StaticSiteRenderer


class RootRenderer(StaticSiteRenderer):
    def get_paths(self):
        return ['/']


renderers = [RootRenderer]
