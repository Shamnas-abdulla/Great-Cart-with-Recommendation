from django.shortcuts import render
from django.db.models import Q
from recommendation.recommend import generate_recommendations
from store.models import Product

def home(request):
    recommended_products = []
    if request.user.is_authenticated:
        print("bla bla bla bla")
        recommended_queries = generate_recommendations(request.user.id)
        print("----------------------------------",recommended_queries)
        if recommended_queries:
            query_filter = Q()
            for q in recommended_queries:
                query_filter |= Q(description__icontains=q) | Q(product_name__icontains=q)
            recommended_products = Product.objects.filter(query_filter).distinct()
        else:
            # Fallback: Show popular products
            recommended_products = Product.objects.all()[:8]  # Assuming you have a sales_count field
    else:
        recommended_products = Product.objects.none()

    return render(request, 'home.html', {'recommended_products': recommended_products})
