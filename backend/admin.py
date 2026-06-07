from django.contrib import admin
from django.utils.html import format_html
from . import models

# Register your models here.
admin.site.register(models.Bedroom)
admin.site.register(models.Bathroom)
admin.site.register(models.Client)
admin.site.register(models.Booking)

@admin.register(models.Unit)
class UnitAdmin(admin.ModelAdmin):

    fields = (
        'name',
        'type',
        'number_of_rooms',
        'number_of_bathrooms',
        'occupancy',
        'breakfast',
        'breakfast_price',
        'active',
        'created_date',
        'last_updated',
        'thumbnail',
        'preview_thumbnail_field',
    )
    readonly_fields = (
        'preview_thumbnail_field',
        'number_of_rooms',
        'number_of_bathrooms',
    )

    def preview_thumbnail_field(self, obj):
        if obj.thumbnail:
            return format_html('<img src="/media/{}" style="max-height: 200px; max-width: 200px;" />', obj.thumbnail)
        return "No image uploaded yet."

    def number_of_rooms(self, obj):
        return obj.number_of_rooms_in_unit()

    def number_of_bathrooms(self, obj):
        return obj.number_of_bathrooms_in_unit()

    preview_thumbnail_field.short_description = 'Thumbnail Preview'


@admin.register(models.UnitPhoto)
class UnitPhotoAdmin(admin.ModelAdmin):

    fields = (
        'unit',
        'display',
        'thumbnail',
        'name',
        'description',
        'category',
        'created_date',
        'last_updated',
        'image',
        'preview_image_field',
    )
    readonly_fields = ('preview_image_field',)

    def preview_image_field(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 200px; max-width: 200px;" />', obj.image.url)
        return "No image uploaded yet."

    preview_image_field.short_description = 'Image Preview'


@admin.register(models.BedroomPhoto)
class BedroomPhotoAdmin(admin.ModelAdmin):

    fields = (
        'unit',
        'bedroom',
        'display',
        'name',
        'description',
        'created_date',
        'last_updated',
        'image',
        'preview_image_field',
    )
    readonly_fields = ('preview_image_field',)

    def preview_image_field(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 200px; max-width: 200px;" />', obj.image.url)
        return "No image uploaded yet."

    preview_image_field.short_description = 'Image Preview'


@admin.register(models.BathroomPhoto)
class BathroomPhotoAdmin(admin.ModelAdmin):

    fields = (
        'unit',
        'bathroom',
        'display',
        'name',
        'description',
        'created_date',
        'last_updated',
        'image',
        'preview_image_field',
    )
    readonly_fields = ('preview_image_field',)

    def preview_image_field(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 200px; max-width: 200px;" />', obj.image.url)
        return "No image uploaded yet."

    preview_image_field.short_description = 'Image Preview'
