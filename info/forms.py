from django.forms import ModelForm
from .models import Comment


class CommentForm(ModelForm):
    """
    A form for creating and updating comments.
    This form is tied to the Comment model and includes a single field for the comment text.
    """
    class Meta:
        model = Comment
        fields = ["comment"]
