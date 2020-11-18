from django.forms import HiddenInput
from django.template import Context, loader
from django.core.urlresolvers import reverse
from django.conf import settings
from cropduster.models import SizeSet, Image as CropDusterImage


class AdminCropdusterWidget(HiddenInput):
    def __init__(self, size_set_slug, template="admin/inline.html", *args, **kwargs):
        try:
            self.size_set = SizeSet.objects.get(slug=size_set_slug)
        except SizeSet.DoesNotExist:
            self.size_set = None
        self.template = template
        super(AdminCropdusterWidget, self).__init__(*args, **kwargs)
        self.is_hidden = False

    def get_thumbnail_urls(self, image):
        urls = []
        if image:
            for size in image.size_set.get_unique_ratios():
                urls.append(image.thumbnail_url(size.slug))
        return urls

    def render(self, name, value, attrs=None):
        attrs.setdefault("class", "cropduster")

        cropduster_url = reverse("cropduster-upload")

        input = super(HiddenInput, self).render(name, value, attrs)

        image = None
        if value:
            try:
                image = CropDusterImage.objects.get(id=value)
            except CropDusterImage.DoesNotExist:
                pass

        template = loader.get_template(self.template)
        context = Context({
            "image": image,
            "size_set": self.size_set,
            "static_url": settings.STATIC_URL,
            "cropduster_url": cropduster_url,
            "input": input,
            "attrs": attrs,
            "thumbnail_urls": self.get_thumbnail_urls(image),
        })
        return template.render(context)
