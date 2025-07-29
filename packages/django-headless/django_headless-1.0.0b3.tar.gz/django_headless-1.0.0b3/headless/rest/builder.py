from typing import Type

from django.db.models import Model
from django.urls import path
from rest_framework.viewsets import ModelViewSet

from ..registry import ModelConfig, headless_registry
from ..utils import camel_to_kebab, log
from .routers import rest_router
from .viewsets import SingletonViewSet
from ..settings import headless_settings


class RestBuilder:
    """
    Class for building a REST API for the models in the headless
    registry.
    """

    def __init__(self):
        self._models = headless_registry.get_models()
        self._serializer_classes = {}

    def build(self):
        """
        Builds the REST API by creating view sets and serializers and registering them
        to the router.
        :return:
        """
        log(":building_construction:", "Setting up REST routes")

        for model_config in self._models:
            model_class = model_config["model"]
            singleton = model_config["singleton"]
            view_set = self.get_view_set(model_config)
            base_path = camel_to_kebab(model_class.__name__)

            if singleton:
                rest_router.urls.append(
                    path(
                        base_path,
                        view_set.as_view(
                            {
                                "get": "retrieve",
                                "put": "update",
                                "patch": "partial_update",
                            }
                        ),
                    )
                )
            else:
                rest_router.register(base_path, view_set)

            self.log_routes(model_class, base_path, singleton)

    def get_serializer(self, model_class: Type[Model]):
        model_name = model_class._meta.label

        # Return serializer class from cache if it exists
        if self._serializer_classes.get(model_name, None):
            return self._serializer_classes[model_name]

        class Serializer(headless_settings.DEFAULT_SERIALIZER_CLASS):
            class Meta:
                model = model_class
                fields = "__all__"

        self._serializer_classes[model_name] = Serializer

        return Serializer

    def get_view_set(self, model_config: ModelConfig):
        model_class = model_config["model"]
        singleton = model_config["singleton"]
        serializer = self.get_serializer(model_class)

        if singleton:

            class ViewSet(SingletonViewSet):
                queryset = model_class.objects.none()
                serializer_class = serializer

                def get_queryset(self):
                    return model_class.objects.all()[:1]

        else:

            class ViewSet(ModelViewSet):
                queryset = model_class.objects.all()
                serializer_class = serializer

        return ViewSet

    @classmethod
    def log_routes(cls, model_class, base_path, singleton=False):
        if singleton:
            log("   ---", f"{model_class._meta.verbose_name}")
            log("     |---", f"GET /{base_path}")
            log("     |---", f"PUT /{base_path}")
            log("     |---", f"PATCH /{base_path}")
        else:
            log("   ---", f"{model_class._meta.verbose_name}")
            log("     |--", f"GET /{base_path}")
            log("     |--", f"GET /{base_path}/{{id}}")
            log("     |--", f"PUT /{base_path}/{{id}}")
            log("     |--", f"PATCH /{base_path}/{{id}}")
            log("     |--", f"POST /{base_path}")
            log("     |--", f"DELETE /{base_path}/{{id}}")

        log("\n")
