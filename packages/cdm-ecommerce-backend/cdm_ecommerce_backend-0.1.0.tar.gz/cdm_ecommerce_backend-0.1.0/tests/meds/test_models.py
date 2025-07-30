"""Tests for the Medicine model."""

import pytest
from model_bakery import baker

from cdm_ecommerce.meds.models import Medicine

pytestmark = pytest.mark.django_db


def test_medicine_str():
    """Test the string representation of the Medicine model."""
    medicine = baker.make(Medicine, name="Paracetamol")
    assert str(medicine) == "Paracetamol"
