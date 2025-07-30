"""Medicine models."""

from django.db import models


class Medicine(models.Model):
    """A medicine."""

    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()

    def __str__(self) -> str:
        """Return the string representation of the medicine."""
        return str(self.name)


class Meta:
    """Meta options for the Medicine model."""

    verbose_name_plural = "Medicines"
