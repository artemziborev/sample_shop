import re

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Field, Div, HTML, Layout
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Subscriber, CallBackRequest


class CallBackRequestForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(
        attrs={
            'type': 'text',
            'name': 'popup_call__name',
            'placeholder': _('Ваше имя'),
            'class': 'w-100'
        }
    ))
    email = forms.EmailField(required=False,
                             widget=forms.EmailInput(
                                 attrs={
                                     'type': 'email',
                                     'name': 'popup_call__email',
                                     'placeholder': _('Ваш email'),
                                     'class': 'w-100',
                                 }
                             ))
    phone = forms.CharField(required=False,
                            widget=forms.TextInput(
                                attrs={
                                    'type': 'tel',
                                    'name': 'popup_call__tel',
                                    'placeholder': _('Ваш телефон'),
                                    'class': 'w-100',
                                }
                            ))
    message = forms.CharField(required=False,
                              widget=forms.Textarea(
                                  attrs={
                                      'name': 'popup_call__text',
                                      'rows': '3',
                                      'сlass': 'w-100',
                                      'placeholder': _('Ваше сообщение')
                                  }
                              ))
    form_type = forms.CharField(
        required=False,
        widget=forms.HiddenInput
    )

    class Meta:
        model = CallBackRequest
        fields = ('name', 'email', 'phone', 'message', 'form_type')

    def __init__(self, *args, **kwargs):
        if args:
            form_type = args[0]
            args = tuple()
        else:
            if kwargs and 'data' in kwargs:
                form_type = kwargs['data']['form_type']
            else:
                form_type = CallBackRequest.FORM_TYPE_CALLBACK
        super().__init__(*args, **kwargs)
        self.fields['form_type'].initial = form_type

        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.form_action = "pages:callback_form"
        self.helper.form_class = 'popup js-ajax-form'

        self.helper.layout = self.get_layout_by_type(form_type)

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        # Регулярка вытаскивает все цифры в массив
        cleaned_phone = re.findall(r'\d+', phone)
        cleaned_phone = "".join(cleaned_phone)
        return cleaned_phone

    def clean(self):
        cleaned_data = super().clean()

        if not (cleaned_data.get('phone', None) or cleaned_data.get('email', None)):
            msg = _("Укажите телефон или Email")
            self.add_error('phone', msg)
            self.add_error('email', msg)

    @staticmethod
    def get_layout_by_type(_type):
        if str(_type) == str(CallBackRequest.FORM_TYPE_CONTACT_US):
            button_text = _('Заказать звонок')
            layout = Layout(
                Div(HTML(_("Не нашли подходящий товар?")), css_class="section__ttl mb-2"),
                Div(HTML(_("Отправьте запрос нашим специалистам. Мы отвечаем на все запросы в течение 15 минут")),
                    css_class="mb-3 fz18"),
                Field('form_type'),
                Field('name', wrapper_class="d-flex flex-column tal mb-3 popup_call__col"),
                Field('email', wrapper_class="d-flex flex-column tal mb-3 popup_call__col"),
                Field('phone', wrapper_class="d-flex flex-column tal mb-3 popup_call__col"),
                Field('message', wrapper_class="d-flex flex-column tal mb-4 popup_call__col", css_class="w-100",
                      cols=None,
                      rows=None, style='height: 150px'),
                Submit('submit', button_text, css_class='btn mb-5'),
                HTML(
                    f"""
                    <label for="popup_call__checkbox" class="checkbox mb-3">
                      <input type="checkbox" id="popup_call__checkbox" required="" checked>
                      <span class="checkbox__text">Нажимая кнопку «{button_text}», я даю согласие на обработку своих <a href="#" data-fancybox="" data-src="#popup_sopd" >персональных данных</a>.</span>
                    </label>
                    """
                )
            )
        elif str(_type) == str(CallBackRequest.FORM_TYPE_COOP):
            button_text = _('Отправить сообщение')
            layout = Layout(
                Div(HTML(_("Хотите сотрудничать?")), css_class="section__ttl mb-2"),
                Div(HTML(_("Отправьте запрос нашим специалистам. Мы отвечаем на все запросы в течение 15 минут")),
                    css_class="tac fz16"),
                Div(
                    Div(
                        Div(
                            Field('form_type'),
                            Field('name', wrapper_class="col-xl-4 mb-3"),
                            Field('email', wrapper_class="col-xl-4 mb-3"),
                            Field('phone', wrapper_class="col-xl-4 mb-3"),
                            Field('message', wrapper_class="col-12 mb-3",
                                  css_class="w-100",
                                  cols=None,
                                  rows=None, style='height: 150px'),
                            css_class='row'
                        ),
                        css_class='feed__in mt-3 mt-xl-4'
                    ),
                    css_class='container'
                ),
                Div(
                    Submit('submit', button_text, css_class='btn btn_red mt-3 mb-3'),
                    HTML(
                        f"""
                          <label for="feed__checkbox" class="checkbox">
                            <input type="checkbox" id="feed__checkbox" required="" checked="">
                            <span class="checkbox__text">Нажимая кнопку «{button_text}», я даю согласие на обработку своих <a href="#" data-fancybox="" data-src="#popup_sopd" >персональных данных</a>.</span>
                          </label>
                        """
                    ),
                    css_class="d-flex flex-column align-items-center"
                ),
            )
        else:
            button_text = _('Заказать звонок')
            layout = Layout(
                Div(HTML(_("Заказать обратный звонок")), css_class="section__ttl mb-2"),
                Div(HTML(_("Отправьте запрос нашим специалистам. Мы отвечаем на все запросы в течение 15 минут")),
                    css_class="mb-3 fz18"),
                Field('form_type'),
                Field('name', wrapper_class="d-flex flex-column tal mb-3 popup_call__col"),
                Field('email', wrapper_class="d-flex flex-column tal mb-3 popup_call__col"),
                Field('phone', wrapper_class="d-flex flex-column tal mb-3 popup_call__col"),
                Field('message', wrapper_class="d-flex flex-column tal mb-4 popup_call__col", css_class="w-100",
                      cols=None,
                      rows=None, style='height: 150px'),
                Submit('submit', button_text, css_class='btn mb-5'),
                HTML(
                    f"""
                    <label for="popup_call__checkbox" class="checkbox mb-3">
                      <input type="checkbox" id="popup_call__checkbox" required="" checked>
                      <span class="checkbox__text">Нажимая кнопку «{button_text}», я даю согласие на обработку своих <a href="#" data-fancybox="" data-src="#popup_sopd" >персональных данных</a>.</span>
                    </label>
                    """
                )
            )
        return layout


class EmailSubscribeForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.widgets.EmailInput(attrs={
        'class': 'mb-3 w-100',
        'placeholder': _('Ваш e-mail')}
    ))

    class Meta:
        model = Subscriber
        fields = ('email',)
