from cas_server.auth import DjangoAuthUser  # pragma: no cover

from note.models import Alias


class CustomAuthUser(DjangoAuthUser):  # pragma: no cover
    """
    Override Django Auth User model to define a custom Matrix username.
    """

    def attributs(self):
        d = super().attributs()
        if self.user:
            d["normalized_name"] = Alias.normalize(self.user.username)
        return d
