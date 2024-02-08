from django import template

register = template.Library()


@register.filter(name='format_price')
def format_price(value):
    formatted_value = "{:,.2f}".format(value)
    return formatted_value
