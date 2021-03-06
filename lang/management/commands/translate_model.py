from functools import reduce

from modeltranslation.translator import translator
from modeltranslation.utils import build_localized_fieldname
from django.db.models import Q
from django.core.management import BaseCommand

from lang.translation import (
    AmazonTranslate,
    AVAILABLE_LANGUAGES,
    DEFAULT_LANGUAGE,
)

LANGUAGES_TO_TRANSLATE = [lang for lang in AVAILABLE_LANGUAGES if lang != DEFAULT_LANGUAGE]

translate = AmazonTranslate()


def translate_fields_object(obj, field):
    default_lang_field = build_localized_fieldname(field, DEFAULT_LANGUAGE)
    # NOTE: Both <field> and <field>_<default_lang> have same ref (Overide by modeltranslation)
    default_lang_value = getattr(obj, default_lang_field, None)
    if not default_lang_value:
        return

    for lang in LANGUAGES_TO_TRANSLATE:
        lang_field = build_localized_fieldname(field, lang)
        value = getattr(obj, lang_field, None)
        if value:
            continue

        new_value = translate.translate_text(
            default_lang_value,
            DEFAULT_LANGUAGE,
            lang,
        )['TranslatedText']

        setattr(obj, lang_field, new_value)
        yield lang_field


class Command(BaseCommand):
    """
    TODO: Look up in all languge field for initial required text
    """
    help = 'Use Amazon Translate to translate all models translated field\'s values'

    def handle(self, *args, **options):
        # get all models excluding proxy- and not managed models
        models = [
            m for m in translator.get_registered_models(abstract=False)
            if not m._meta.proxy and m._meta.managed
        ]

        print('\nLanguages:', AVAILABLE_LANGUAGES)
        print('Default language:', DEFAULT_LANGUAGE)
        print('Number of models:', len(models))

        for model in models:
            print(f'\nProcessing for Model: {model._meta.verbose_name.title()}')

            # Generate fields
            translation_fields = list(translator.get_options_for_model(model).fields.keys())
            if not translation_fields:
                continue

            # Generate filters to fetch only rows with missing translations
            q = reduce(
                lambda acc, f: acc | f,
                [
                    (
                        Q(**{f"{build_localized_fieldname(field, DEFAULT_LANGUAGE)}__isnull": False}) &
                        ~Q(**{f"{build_localized_fieldname(field, DEFAULT_LANGUAGE)}__exact": ""}) &
                        reduce(
                            lambda acc, f: acc | f,
                            [
                                (
                                    Q(**{f"{build_localized_fieldname(field, lang)}__isnull": True}) |
                                    Q(**{f"{build_localized_fieldname(field, lang)}__exact": ""})
                                )
                                for lang in LANGUAGES_TO_TRANSLATE
                            ]
                        )
                    )
                    for field in translation_fields
                ]
            )
            qs = model.objects.filter(q)

            qs_count = qs.count()
            index = 1
            print('\tFields:', translation_fields)
            print('\tTotal rows:', qs_count)

            for obj in qs.all():
                print(f'\t\t ({index}/{qs_count}) - {obj}')
                index += 1

                update_fields = []
                for field in translation_fields:
                    update_fields.extend(list(translate_fields_object(obj, field)))
                obj.save(update_fields=update_fields)
