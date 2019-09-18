from django import template


def pretty_money(value):
    if value%100 == 0:
        return str(value//100) + '€'
    else:
        return str(value//100) + '€ ' + str(value%100)


register = template.Library()
register.filter('pretty_money', pretty_money)
