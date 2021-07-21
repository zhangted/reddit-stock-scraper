from django import template

register = template.Library()

@register.simple_tag
def convert_hours(hours):
    """Convert hours to more display friendly units."""
    if hours == 1:
        return "1 hour ago"
    elif hours < 23:
        return str(hours)+ " hours ago"
    elif hours == 24:
        return "1 day ago"
    else:
        if hours % 24 > 0:
            return str(hours//24) + " days ago and " + str(hours%24) + " hours ago" 
        else:
            return str(hours//24) + " days ago"