from rest_framework import mixins, generics
from my app.models import Product
from myapp.serializers import ProductSerializer


class ProductList(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  generics.GenericsAPIView):
         queryset = Product.object.all()
         serializer_class = ProductSerializer

         def get(self, request, *arqs, **kwargs):
                 return self.list(request, *arqs, **kwargs)


        def post(self, request, *arqs, **kwargs):
        return self.create(request, *arqs, **kwargs)