from django.shortcuts import render
from .models import UserSearch
from django.db.models import Q
from django.shortcuts import render
from .models import UserSearch  # Assuming you have a Product model for searching
from store.models import Product
from .recommend import generate_recommendations

def search_view(request):
    query = request.GET.get('q')  # This will now match the form input name
    products = Product.objects.none()   # Initialize an empty list for search results
    product_count = 0

    if request.user.is_authenticated and query:
        UserSearch.objects.create(user=request.user, search_query=query)
    if query:
        # Perform your product search logic here, e.g.:
        products = Product.objects.filter(
                Q(description__icontains=query) | Q(product_name__icontains=query)
            ).order_by('created_date')
        product_count = products.count()
    else:
        products = Product.objects.all()  # If keyword is empty, show all products
        product_count = products.count()
    context = {
    'products': products,
    'product_count': product_count,
    'query': query,
    
     }
    
    return render(request, 'store/store.html', context)

# def search(request):
#     products = Product.objects.none()  # Default empty queryset
#     product_count = 0
    
#     if 'keyword' in request.GET:
#         keyword = request.GET['keyword'].strip()  # Strip whitespace from the keyword
#         if keyword:  # Check if keyword is not empty
#             products = Product.objects.filter(
#                 Q(description__icontains=keyword) | Q(product_name__icontains=keyword)
#             ).order_by('created_date')
#             product_count = products.count()
#         else:
#             products = Product.objects.all()  # If keyword is empty, show all products
#             product_count = products.count()

#     context = {
#         'products': products,
#         'product_count': product_count,
#     }
    
#     return render(request, 'store/store.html', context)

