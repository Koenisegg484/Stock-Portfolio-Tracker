from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('signals/', views.stock_signals_view, name='stock_signals'),
    
    path('data-collection/', views.data_collection_view, name='data_collection'),

    path('portfolio/create/', views.portfolio_view, name='portfolio_form'),
    path('portfolio/details/', views.portfolio_details_view, name='portfolio_details'),
    path('portfolio/performance/', views.calculate_performance_view, name='portfolio_performance'),
    path('portfolio/summary/', views.portfolio_summary_view, name='portfolio_summary'),
    path('stocks/signals/', views.stock_signals_view, name='stock_signals'),

    path('trade-analyzer/', views.trade_analyzer_view, name='trade_analyzer'),

    path('run-simulation/', views.run_simulation_view, name='run_simulation'),
]
