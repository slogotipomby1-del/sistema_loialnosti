import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse


@pytest.mark.django_db
def test_admin_index_shows_admin_memo(client):
    user_model = get_user_model()
    admin_user = user_model.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="StrongPassword123!",
    )

    client.force_login(admin_user)
    response = client.get(reverse("admin:index"))

    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert 'data-testid="admin-memo-card"' in content
