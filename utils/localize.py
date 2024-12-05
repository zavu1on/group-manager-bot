import os
from argostranslate import package, translate

path = os.path.join(os.getcwd(), "assets/translate-en_ru-1_9.argosmodel")
package.install_from_path(path)
installed_languages = translate.get_installed_languages()


def translate(text: str) -> str:
    if len(installed_languages) < 2:
        return text

    translation = installed_languages[0].get_translation(installed_languages[1])
    return translation.translate(text)
