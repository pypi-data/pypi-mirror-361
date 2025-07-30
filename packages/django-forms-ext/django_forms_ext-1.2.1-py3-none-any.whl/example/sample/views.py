try:
    from django.core.urlresolvers import reverse
except ModuleNotFoundError:
    from django.urls import reverse
from django.forms import ModelForm
from django.forms import modelformset_factory
from django.forms.models import BaseModelFormSet
from django.views.generic.edit import CreateView
from forms_ext.fields import ForeignKeyChoiceField
from forms_ext.fields import QuerysetChoiceField
from forms_ext.views.generic import FormSetView

from sample import models


class PersonForm(ModelForm):
    eye_color = ForeignKeyChoiceField(models.EyeColor)

    class Meta(object):
        exclude = ()
        model = models.Person


class PersonFormSet(BaseModelFormSet):

    def __init__(self, *args, **kwargs):
        super(PersonFormSet, self).__init__(*args, **kwargs)

        eye_colors = [("", "------")]
        eye_colors.extend([(c.pk, c.name) for c in models.EyeColor.objects.all()])
        for form in self.forms:
            form.fields["eye_color"].choices = eye_colors


class FewQueries(FormSetView):
    model = models.Person
    form_class = modelformset_factory(model, form=PersonForm, formset=PersonFormSet, extra=10)


class ManyQueries(FormSetView):
    model = models.Person
    form_class = modelformset_factory(model, extra=10, fields=("eye_color",))


class SimpleFormsetView(FormSetView):
    model = models.Person
    form_class = modelformset_factory(model, fields=("eye_color",))


class QuerysetChoiceFieldForm(ModelForm):
    second_eye_color = QuerysetChoiceField(queryset=models.EyeColor.objects.all())

    class Meta(object):
        model = models.Person
        exclude = ()


class QuerysetChoiceFieldView(CreateView):
    form_class = QuerysetChoiceFieldForm
    template_name = "sample/form.html"

    def get_success_url(self):
        return reverse("querysetchoice")
