export default {
  barcode: function(frm, cdt, cdn) {
    const transaction_controller = new erpnext.TransactionController();
    transaction_controller.barcode(frm, cdt, cdn);
  },
};
