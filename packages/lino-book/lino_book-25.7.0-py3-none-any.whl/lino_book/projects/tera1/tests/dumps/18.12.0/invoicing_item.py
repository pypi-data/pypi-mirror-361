# -*- coding: UTF-8 -*-
logger.info("Loading 16 objects to table invoicing_item...")
# fields: id, plan, partner, generator_type, generator_id, amount, preview, selected, invoice
loader.save(
    create_invoicing_item(
        47, 1, 113, None, None, '115.00',
        u'2 appointments (120.00 \u20ac)<br>\nCash daybook Daniel (-5.00 \u20ac)',
        True, 71))
loader.save(
    create_invoicing_item(48, 1, 114, None, None, '60.00',
                          u'2 appointments (60.00 \u20ac)', True, 72))
loader.save(
    create_invoicing_item(
        49, 1, 122, None, None, '105.00',
        u'2 appointments (120.00 \u20ac)<br>\nCash daybook Daniel (-15.00 \u20ac)',
        True, 73))
loader.save(
    create_invoicing_item(50, 1, 180, None, None, '60.00',
                          u'2 appointments (60.00 \u20ac)', True, 74))
loader.save(
    create_invoicing_item(51, 1, 150, None, None, '120.00',
                          u'2 appointments (120.00 \u20ac)', True, 75))
loader.save(
    create_invoicing_item(52, 1, 151, None, None, '60.00',
                          u'2 appointments (60.00 \u20ac)', True, 76))
loader.save(
    create_invoicing_item(53, 1, 132, None, None, '120.00',
                          u'2 appointments (120.00 \u20ac)', True, 77))
loader.save(
    create_invoicing_item(54, 1, 134, None, None, '60.00',
                          u'2 appointments (60.00 \u20ac)', True, 78))
loader.save(
    create_invoicing_item(
        55, 1, 139, None, None, '85.00',
        u'2 appointments (120.00 \u20ac)<br>\nCash daybook Daniel (-15.00 \u20ac)...',
        True, 79))
loader.save(
    create_invoicing_item(56, 1, 141, None, None, '60.00',
                          u'2 appointments (60.00 \u20ac)', True, 80))
loader.save(
    create_invoicing_item(
        57, 1, 146, None, None, '115.00',
        u'2 appointments (120.00 \u20ac)<br>\nCash daybook Daniel (-5.00 \u20ac)',
        True, 81))
loader.save(
    create_invoicing_item(58, 1, 172, None, None, '60.00',
                          u'2 appointments (60.00 \u20ac)', True, 82))
loader.save(
    create_invoicing_item(59, 1, 156, None, None, '120.00',
                          u'2 appointments (120.00 \u20ac)', True, 83))
loader.save(
    create_invoicing_item(60, 1, 157, None, None, '60.00',
                          u'2 appointments (60.00 \u20ac)', True, 84))
loader.save(
    create_invoicing_item(
        61, 1, 173, None, None, '100.00',
        u'2 appointments (120.00 \u20ac)<br>\nCash daybook Daniel (-20.00 \u20ac)',
        True, 85))
loader.save(
    create_invoicing_item(62, 1, 165, None, None, '60.00',
                          u'2 appointments (60.00 \u20ac)', True, 86))

loader.flush_deferred_objects()
