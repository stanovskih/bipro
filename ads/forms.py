from dataclasses import fields
from django import forms
from ads.models import Disconnect, Order, FotosInOrder
from django.forms import inlineformset_factory
from django.contrib.admin.widgets import FilteredSelectMultiple

from dict.models import WorkSystem

class CustomDateTimeInput(forms.DateTimeInput):
    input_type = 'datetime-local'  # Жестко заставляем Django рендерить этот тип

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        # Исключаем поля, которые не должен заполнять пользователь при создании/редактировании
        exclude = ['author', 'creation_date', 'modified_date', 'last_printed_date', 'company_owner','orderid', ]

        
        # Добавляем Bootstrap-классы для красивого отображения
        widgets = {
            'order_date': forms.DateInput(attrs={'class': 'form-control','type':'date',},format='%Y-%m-%d'),
            'plan_date': forms.DateInput(attrs={'class': 'form-control','type':'date',},format='%Y-%m-%d'),
            'state': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows':2, 'list':"standart-description"}),
            'number': forms.TextInput(attrs={'class': 'form-control','placeholder':'Будет присвоен после сохранения'}),
            'employee': forms.SelectMultiple(attrs={'class': 'tom-select-custom'}),
        #    'company': forms.Select(attrs={'class': 'form-control'}),
        #    'question': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        #fields = ('__ALL__',)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['worksystem'].queryset = WorkSystem.objects.filter(is_used = True)
        for field_name, field in self.fields.items():
            if field_name != 'employee':
                field.widget.attrs['class'] = 'form-control'

class OrderCloseForm(forms.ModelForm):
    class Meta:
        model = Order
        # Исключаем поля, которые не должен заполнять пользователь при создании/редактировании
        #exclude = ['author', 'creation_date', 'modified_date', 'last_printed_date', 'company_owner','orderid', ]
        fields = ('state', 'fact_date', 'fact_description')
        # Добавляем Bootstrap-классы для красивого отображения
        widgets = {
            #'fact_date': forms.DateTimeInput(attrs={'class': 'form-control','type':'date',},format='%Y-%m-%dT%H:%M'),
            'fact_date': CustomDateTimeInput(
                attrs={
                    'class': 'form-control',
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'fact_description': forms.Textarea(attrs={'class': 'form-control', 'rows':2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


FotoInOrderFormSet = inlineformset_factory(
    Order, 
    FotosInOrder, 
    fields=('name', 'foto', ), 
    extra=1,         # Количество пустых дополнительных форм для добавления
    
    # ПЕРЕДАЧА ВИДЖЕТОВ:
    widgets={
        'name': forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Введите имя...'
        }),
        'foto': forms.ClearableFileInput(attrs={
            'class': 'form-control-file',
            'accept': 'image/*' # Ограничивает выбор файлов только картинками
        }),
    },
)

class FotoInOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        # Исключаем поля, которые не должен заполнять пользователь при создании/редактировании
        #exclude = ['author', 'creation_date', 'modified_date', 'last_printed_date', 'company_owner','orderid', ]
        fields = ('id', )
        # Добавляем Bootstrap-классы для красивого отображения
        widgets = {
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class DisconnectForm(forms.ModelForm):
    class Meta:
        model = Disconnect
        # Исключаем поля, которые не должен заполнять пользователь при создании/редактировании
        exclude = ['author', 'creation_date', 'company_owner',]

        
        # Добавляем Bootstrap-классы для красивого отображения
        widgets = {

            'start_disconnect': CustomDateTimeInput(
                attrs={
                    'class': 'form-control',
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'plan_connection_date': CustomDateTimeInput(
                attrs={
                    'class': 'form-control',
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'fact_connection_date': CustomDateTimeInput(
                attrs={
                    'class': 'form-control',
                },
                format='%Y-%m-%dT%H:%M'
            ),

            'connected': forms.CheckboxInput(attrs={'class': 'form-control-checkbox'}),
            'published': forms.CheckboxInput(attrs={'class': 'form-control-checkbox'}),
            'building': forms.SelectMultiple(attrs={'class': 'tom-select-custom'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows':2}),


            
        #    'state': forms.Select(attrs={'class': 'form-control'}),
        #    'description': forms.Textarea(attrs={'class': 'form-control', 'rows':2, 'list':"standart-description"}),
        #    'number': forms.TextInput(attrs={'class': 'form-control','placeholder':'Будет присвоен после сохранения'}),
        #    #'employee': forms.CheckboxSelectMultiple(),
        #    'company': forms.Select(attrs={'class': 'form-control'}),
        #    'question': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        #fields = ('__ALL__',)

    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



        for field_name, field in self.fields.items():
            if field_name not in ['connected','building','published']:
                field.widget.attrs['class'] = 'form-control'
        
        

        #self.fields['building'].widget = FilteredSelectMultiple(
        #    attrs={'class': 'form-control'},
        #    verbose_name='Объекты',
        #    is_stacked=False  # True для vertical list, False для horizontal
        #)


