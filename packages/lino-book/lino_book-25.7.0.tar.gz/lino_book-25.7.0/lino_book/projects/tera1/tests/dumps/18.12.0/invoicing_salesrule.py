# -*- coding: UTF-8 -*-
logger.info("Loading 6 objects to table invoicing_salesrule...")
# fields: partner, invoice_recipient, paper_type
loader.save(create_invoicing_salesrule(115, None, None))
loader.save(create_invoicing_salesrule(121, 180, None))
loader.save(create_invoicing_salesrule(126, 127, None))
loader.save(create_invoicing_salesrule(140, 139, None))
loader.save(create_invoicing_salesrule(148, 147, None))
loader.save(create_invoicing_salesrule(163, 162, None))

loader.flush_deferred_objects()
