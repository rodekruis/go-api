import logging
import boto3

from modeltranslation.admin import TranslationBaseModelAdmin
from modeltranslation.utils import build_localized_fieldname
from modeltranslation import settings as mt_settings
from modeltranslation.manager import (
    get_translatable_fields_for_model,
    MultilingualQuerySet,
    FallbackValuesIterable,
    append_fallback,
)
from django.utils.translation import get_language as django_get_language

from rest_framework import serializers
from django.utils.translation import get_language
from django.conf import settings

logger = logging.getLogger(__name__)

# Array of language : ['en', 'es', 'fr', ....]
DJANGO_AVAILABLE_LANGUAGES = set([lang[0] for lang in settings.LANGUAGES])
AVAILABLE_LANGUAGES = mt_settings.AVAILABLE_LANGUAGES
DEFAULT_LANGUAGE = mt_settings.DEFAULT_LANGUAGE


# Overwrite TranslationBaseModelAdmin _exclude_original_fields to only show current language field in Admin panel
o__exclude_original_fields = TranslationBaseModelAdmin._exclude_original_fields
def _exclude_original_fields(self, exclude=None):  # noqa: E302
    current_lang = get_language()
    exclude = o__exclude_original_fields(self, exclude)
    # Exclude other languages
    return exclude + tuple([
        build_localized_fieldname(field, lang)
        for field in self.trans_opts.fields.keys()
        for lang in AVAILABLE_LANGUAGES
        if lang != current_lang
    ])


TranslationBaseModelAdmin._exclude_original_fields = _exclude_original_fields


# NOTE: Fixing modeltranslation Queryset to support experssions in Queryset values()
# https://github.com/deschler/django-modeltranslation/issues/517
def multilingual_queryset__values(self, *original, prepare=False, **expressions):
    if not prepare:
        return super(MultilingualQuerySet, self)._values(*original, **expressions)
    new_fields, translation_fields = append_fallback(self.model, original)
    clone = super(MultilingualQuerySet, self)._values(*list(new_fields), **expressions)
    clone.original_fields = tuple(original)
    clone.translation_fields = translation_fields
    clone.fields_to_del = new_fields - set(original)
    return clone


def multilingual_queryset_values(self, *fields, **expressions):
    fields += tuple(expressions)
    if not self._rewrite:
        return super(MultilingualQuerySet, self).values(*fields, **expressions)
    if not fields:
        # Emulate original queryset behaviour: get all fields that are not translation fields
        fields = self._get_original_fields()
    clone = self._values(*fields, prepare=True, **expressions)
    clone._iterable_class = FallbackValuesIterable
    return clone


MultilingualQuerySet._values = multilingual_queryset__values
MultilingualQuerySet.values = multilingual_queryset_values


class AmazonTranslate(object):
    """
    Amazon Translate helper
    """
    def __init__(self, client=None):
        self.translate = client or boto3.client(
            'translate',
            aws_access_key_id=settings.AWS_TRANSLATE_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_TRANSLATE_SECRET_KEY,
            region_name=settings.AWS_TRANSLATE_REGION,
        )

    def translate_text(self, text, source_language, dest_language):
        return self.translate.translate_text(
            Text=text,
            SourceLanguageCode=source_language,
            TargetLanguageCode=dest_language
        )


class TranslatedModelSerializerMixin(serializers.ModelSerializer):
    """
    Translation mixin for serializer
    - Using header/GET Params detect languge
    - Assign original field name to requested field_<language>
    - Provide fields for multiple langauge if multiple languages is specified. eg: field_en, field_es
    """
    def get_field_names(self, declared_fields, info):
        fields = super().get_field_names(declared_fields, info)

        requested_langs = []
        if self.context.get('request') is not None:
            lang_param = self.context['request'].query_params.get('lang') or django_get_language()
        else:
            logger.warn('Request is not passed using context. This can cause unexcepted behavior for translation')
            lang_param = django_get_language()

        if lang_param == 'all':
            requested_langs = AVAILABLE_LANGUAGES
        else:
            requested_langs = lang_param.split(',') if lang_param else []

        excluded_langs = [lang for lang in AVAILABLE_LANGUAGES if lang not in requested_langs]
        included_langs = [lang for lang in AVAILABLE_LANGUAGES if lang in requested_langs]
        exclude_fields = []
        included_fields_lang = {}
        for f in get_translatable_fields_for_model(self.Meta.model):
            exclude_fields.append(f)
            for lang in excluded_langs:
                exclude_fields.append(build_localized_fieldname(f, lang))
            included_fields_lang[f] = []
            for lang in included_langs:
                included_fields_lang[f].append(build_localized_fieldname(f, lang))

        self.included_fields_lang = included_fields_lang
        exclude_fields = set(exclude_fields)
        return [
            f for f in fields if f not in exclude_fields
        ]

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        for field, lang_fields in self.included_fields_lang.items():
            if len(lang_fields) != 1:
                break
            lang_field = lang_fields[0]
            fields[field] = fields.pop(lang_field)
            fields[field].source = lang_field
        return fields
