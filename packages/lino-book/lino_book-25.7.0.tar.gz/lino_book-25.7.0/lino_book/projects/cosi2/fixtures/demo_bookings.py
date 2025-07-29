from lino.api import dd, rt


def objects():
    Invoice = rt.models.trading.VatProductInvoice
    par = rt.models.contacts.Person.objects.filter(country__isocode="BE").first()
    prd = rt.models.products.Product.objects.get(id=1)
    jnl = rt.models.accounting.Journal.get_by_ref("SLS")

    yield (obj := Invoice(journal=jnl, partner=par, entry_date=dd.today()))

    def add(qty, unit_price, discount):
        line = obj.add_voucher_item(
            prd, qty, unit_price=unit_price, discount_amount=discount)
        line.full_clean()
        line.discount_amount_changed()
        return line

    yield add(30.94, "1.586", "2.01")
    yield add(44.19, "1.652", "2.87")

    obj.register_voucher()
    yield obj
