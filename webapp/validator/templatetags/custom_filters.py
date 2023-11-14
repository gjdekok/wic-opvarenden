from django import template
import re

register = template.Library()

@register.filter
def split(value, arg):
    return value.split(arg)

@register.filter
def clean_list_item(value):
    cleaned_value = re.sub(r"[\[\]']", "", value)
    return cleaned_value.strip()

@register.filter
def highlight_interesting_text_before(text, interesting_text_before):
    # Check if the last 40 characters of interesting_text_before match a substring of text
    if interesting_text_before:
        last_40_chars = interesting_text_before[-40:]
        if last_40_chars in text:
            text = text.replace(last_40_chars, f"<strong>{last_40_chars}</strong>")
    return text

@register.filter
def highlight_interesting_text_after(text, interesting_text_after):
    # Check if interesting_text_after matches a substring of text
    if interesting_text_after:
        if interesting_text_after in text:
            text = text.replace(interesting_text_after, f"<strong>{interesting_text_after}</strong>")
    return text