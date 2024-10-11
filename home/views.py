from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from .models import Product, Category
from django.shortcuts import get_object_or_404
from . import tasks
from utils import IsAdminUserMixin
from orders.forms import CartAddForm
from .forms import ProductSearchForm
from .documents import CategoryDocument


class HomeView(View):
    form_class = ProductSearchForm

    def get(self, request, category_slug=None):
        search_field = request.GET.get('search')
        products = Product.objects.filter(available=True)
        categories = Category.objects.filter(is_sub=False)

        if search_field:
            result_elastic = CategoryDocument.search().query('wildcard', slug=f'*{search_field}*')
            response = result_elastic.execute()
            category_names = [r.name for r in response.hits]
            products = products.filter(category__in=category_names)
        elif category_slug:
            category = Category.objects.get(slug=category_slug)
            products = products.filter(category=category)

        return render(request, 'home/home.html',
                      {'products': products, 'categories': categories, 'form': self.form_class})


class ProductDetailView(View):
    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        form = CartAddForm()
        return render(request, 'home/detail.html', {'product': product, 'form': form})


class BucketHome(IsAdminUserMixin, View):
    template_name = 'home/bucket.html'

    def get(self, request):
        objects = tasks.all_bucket_objects_task()
        return render(request, self.template_name, {'objects': objects})


class DeleteBucketObject(IsAdminUserMixin, View):
    def get(self, request, key):
        tasks.delete_object_task.delay(key)
        messages.success(request, 'your object will be delete soon.', 'info')
        return redirect('home:bucket')


class DownloadBucketObject(IsAdminUserMixin, View):
    def get(self, request, key):
        tasks.download_object_task.delay(key)
        messages.success(request, 'your download will start soon.', 'info')
        return redirect('home:bucket')

# Category.objects.filter(slug__contains=search_field)
