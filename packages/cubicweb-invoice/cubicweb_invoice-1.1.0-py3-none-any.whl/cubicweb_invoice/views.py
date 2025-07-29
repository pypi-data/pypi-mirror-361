"""template-specific forms/views/actions/components"""
from cubicweb.predicates import is_instance
from cubicweb_web.facet import RangeFacet, DateRangeFacet
from cubicweb_web.views import uicfg

uicfg.autoform_section.tag_subject_of(('Invoice', 'credit_account', '*'), 'main', 'attributes')
uicfg.autoform_section.tag_subject_of(('Invoice', 'debit_account', '*'), 'muledit', 'attributes')
uicfg.autoform_section.tag_subject_of(('Invoice', 'credit_account', '*'), 'main', 'attributes')
uicfg.autoform_section.tag_subject_of(('Invoice', 'debit_account', '*'), 'muledit', 'attributes')


class InvoiceEmitDateFacet(DateRangeFacet):
    __regid__ = 'invoice.emit_date.facet'
    __select__ = DateRangeFacet.__select__ & is_instance('Invoice')
    rtype = 'emit_date'


class InvoiceDueDateFacet(DateRangeFacet):
    __regid__ = 'invoice.due_date.facet'
    __select__ = DateRangeFacet.__select__ & is_instance('Invoice')
    rtype = 'due_date'


class InvoicePayDateFacet(DateRangeFacet):
    __regid__ = 'invoice.pay_date.facet'
    __select__ = DateRangeFacet.__select__ & is_instance('Invoice')
    rtype = 'pay_date'


class InvoiceAmountFacet(RangeFacet):
    __regid__ = 'invoice.amount.facet'
    __select__ = RangeFacet.__select__ & is_instance('Invoice')
    rtype = 'amount'
