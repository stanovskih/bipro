from django.urls import path

from . import views



#django.contrib.auth.views.login with django.contrib.auth.views.LoginView




#(r'^login/?$','django.contrib.auth.views.login',{'template_name':'login.html', 'authentication_form':MyAuthenticationForm}),

#admin.site.site_header = settings.ADMIN_SITE_HEADER

urlpatterns = [
    path('orders', views.OrderListView.as_view(), name='order_list'),
    path('orders/create', views.OrderCreateView.as_view(), name='order_create'),
    path('orders/<int:pk>/update/', views.OrderUpdateView.as_view(), name='order_update'),
    path('orders/<int:pk>/close/', views.OrderCloseView.as_view(), name='order_close'),
    path('orders/<int:pk>/foto/', views.FotoInOrderUpdateView.as_view(), name='order_close'),
    path('orders/reports', views.reports, name='order_reports'),

    path('getaddressfromphone', views.get_address_from_phone),
    path('getordershistory', views.get_orders_history),    
    path('getcompanyexec', views.get_company_exec),
    
    path('print', views.print),
    path('printdisconnect', views.print_disconnect),

#-------------ОТКЛЮЧЕНИЯ------------------------
    path('disconnects', views.DisconnectListView.as_view(), name='disconnect_list'),
    path('disconnects/create', views.DisconnectCreateView.as_view(), name='disconnect_create'),
    path('disconnects/<int:pk>/update', views.DisconnectUpdateView.as_view(), name='disconnect_update'),
    
] 

