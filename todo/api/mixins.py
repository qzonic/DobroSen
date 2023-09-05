from rest_framework import mixins, viewsets


class ListCreateViewSet(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    """ A viewset that provides default `create()` and `list()` actions. """
    pass


class ListRetrieveUpdateViewSet(mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                mixins.UpdateModelMixin,
                                viewsets.GenericViewSet):
    """ A viewset that provides default `list()`, `retrieve()`, `update()` and `partial_update()` actions. """
    pass
