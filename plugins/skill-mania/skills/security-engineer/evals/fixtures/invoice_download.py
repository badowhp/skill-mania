from cache import ttl_cache


@router.get("/api/invoices/{invoice_id}/download")
@ttl_cache(seconds=300, key=lambda invoice_id, principal: invoice_id)
def download_invoice(invoice_id: str, principal: Principal) -> RedirectResponse:
    invoice = invoice_repository.get(invoice_id)
    if invoice.tenant_id != principal.tenant_id:
        raise NotFound()
    audit.info("invoice_download", invoice_id=invoice.id, user_id=principal.user_id)
    return RedirectResponse(storage.sign(invoice.object_key, expires_in=300))


def test_cross_tenant_download_is_hidden(client, tenant_a_invoice, tenant_b_user):
    response = client.as_user(tenant_b_user).get(
        f"/api/invoices/{tenant_a_invoice.id}/download"
    )
    assert response.status_code == 404
