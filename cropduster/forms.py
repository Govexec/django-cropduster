try:
    from collections import OrderedDict
except ImportError:
    from django.utils.datastructures import SortedDict as OrderedDict

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms.util import flatatt
from django.forms.models import ModelMultipleChoiceField
from django.utils.html import escape, conditional_escape
from django.utils.encoding import force_unicode

from generic_plus.forms import BaseGenericFileInlineFormSet, GenericForeignFileWidget

from .utils import json


__all__ = ('CropDusterWidget', 'CropDusterThumbFormField', 'CropDusterInlineFormSet')


class CropDusterWidget(GenericForeignFileWidget):

    sizes = None

    template = "cropduster/custom_field.html"

    class Media:
        css = {'all': (u'%scropduster/css/cropduster.css?v=5' % settings.STATIC_URL,)}
        js = (
            u'%scropduster/js/jsrender.js' % settings.STATIC_URL,
            u'%scropduster/js/cropduster.js?v=5' % settings.STATIC_URL,
        )

    def get_context_data(self, name, value, attrs=None, bound_field=None):
        ctx = super(CropDusterWidget, self).get_context_data(name, value, attrs, bound_field)

        thumbs = OrderedDict({})

        sizes = self.sizes

        if callable(sizes):
            obj = getattr(ctx['instance'], 'content_object', None)
            sizes_callable = getattr(sizes, 'im_func', sizes)
            sizes = sizes_callable(obj)

        if ctx['value'] and ctx['instance'] is not None:
            for thumb in ctx['instance'].thumbs.all().order_by('-width'):
                size_name = thumb.name
                thumbs[size_name] = ctx['instance'].get_image_url(size_name)

        ctx.update({
            'sizes': json.dumps(sizes),
            'thumbs': thumbs,
        })
        return ctx


class CropDusterThumbWidget(forms.SelectMultiple):

    def __init__(self, *args, **kwargs):
        from cropduster.models import Thumb

        super(CropDusterThumbWidget, self).__init__(*args, **kwargs)
        self.model = Thumb

    def render_option(self, selected_choices, option_value, option_label):
        attrs = {}
        try:
            thumb = self.model.objects.get(pk=option_value)
        except (TypeError, self.model.DoesNotExist):
            pass
        else:
            # If the thumb has no images associated with it then
            # it has not yet been saved, and so its file path has
            # '_tmp' appended before the extension.
            use_tmp_file = not(thumb.image_set.all().count())
            attrs = {
                'data-width': thumb.width,
                'data-height': thumb.height,
                'data-tmp-file': json.dumps(use_tmp_file),
            }
        option_value = force_unicode(option_value)
        if option_value in selected_choices:
            selected_html = u' selected="selected"'
            if not self.allow_multiple_selected:
                # Only allow for a single selection.
                selected_choices.remove(option_value)
        else:
            selected_html = ''
        return (
            u'<option value="%(value)s"%(selected)s%(attrs)s>%(label)s</option>') % {
                'value': escape(option_value),
                'selected': selected_html,
                'attrs': flatatt(attrs),
                'label': conditional_escape(force_unicode(option_label)),
        }


class CropDusterThumbFormField(ModelMultipleChoiceField):

    widget = CropDusterThumbWidget

    def clean(self, value):
        """
        Override default validation so that it doesn't throw a ValidationError
        if a given value is not in the original queryset.
        """
        try:
            value = super(CropDusterThumbFormField, self).clean(value)
        except ValidationError, e:
            if self.error_messages['required'] in e.messages:
                raise
            elif self.error_messages['list'] in e.messages:
                raise
        return value


class CropDusterInlineFormSet(BaseGenericFileInlineFormSet):

    fields = ('image', 'thumbs', 'attribution', 'attribution_link', 'caption')

    def _construct_form(self, i, **kwargs):
        """
        Limit the queryset of the thumbs for performance reasons (so that it doesn't
        pull in every available thumbnail into the selectbox)
        """
        from cropduster.models import Image, Thumb

        form = super(CropDusterInlineFormSet, self)._construct_form(i, **kwargs)

        try:
            instance = Image.objects.get(pk=form['id'].value())
        except (ValueError, Image.DoesNotExist):
            instance = None

        thumbs_field = form.fields['thumbs']

        if instance:
            # Set the queryset to the current list of thumbs on the image
            thumbs_field.queryset = instance.thumbs.get_query_set()
        else:
            # Start with an empty queryset
            thumbs_field.queryset = Thumb.objects.none()

        if form.data:
            # Check if thumbs from POST data should be used instead.
            # These can differ from the values in the database if a
            # ValidationError elsewhere prevented saving.
            try:
                thumb_pks = map(int, form['thumbs'].value())
            except (TypeError, ValueError):
                pass
            else:
                if thumb_pks and thumb_pks != [o.pk for o in thumbs_field.queryset]:
                    thumbs_field.queryset = Thumb.objects.filter(pk__in=thumb_pks)

        return form
